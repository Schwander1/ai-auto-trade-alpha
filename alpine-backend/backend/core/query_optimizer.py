"""
Query Optimization Utilities
Provides helpers for optimizing database queries to prevent N+1 problems
and improve performance.
"""
from typing import List, Type, Optional, Any
from sqlalchemy.orm import Session, joinedload, selectinload, Query
from sqlalchemy import func, case, Integer
from sqlalchemy.inspection import inspect
import logging

logger = logging.getLogger(__name__)


def optimize_query_with_relationships(
    query: Query,
    model: Type,
    relationships: Optional[List[str]] = None,
    use_selectin: bool = True
) -> Query:
    """
    Optimize a query by eagerly loading relationships to prevent N+1 queries.

    Args:
        query: SQLAlchemy query object
        model: SQLAlchemy model class
        relationships: List of relationship names to eagerly load (None = auto-detect)
        use_selectin: If True, use selectinload (better for large datasets),
                     if False, use joinedload (better for small datasets)

    Returns:
        Optimized query with eager loading

    Example:
        ```python
        # Before: N+1 query problem
        users = db.query(User).all()
        for user in users:
            print(user.roles)  # Separate query for each user

        # After: Single query with eager loading
        users = optimize_query_with_relationships(
            db.query(User),
            User,
            relationships=['roles']
        ).all()
        for user in users:
            print(user.roles)  # Already loaded, no additional queries
        ```
    """
    if relationships is None:
        # Auto-detect relationships
        relationships = _get_relationship_names(model)

    if not relationships:
        return query

    # Use selectinload for better performance with large datasets
    # Use joinedload for better performance with small datasets
    loader = selectinload if use_selectin else joinedload

    for rel_name in relationships:
        try:
            # Verify relationship exists
            if hasattr(model, rel_name):
                query = query.options(loader(getattr(model, rel_name)))
        except Exception as e:
            logger.warning(f"Could not eager load relationship '{rel_name}' on {model.__name__}: {e}")

    return query


def _get_relationship_names(model: Type) -> List[str]:
    """Get all relationship names from a SQLAlchemy model"""
    try:
        mapper = inspect(model)
        return [rel.key for rel in mapper.relationships]
    except Exception as e:
        logger.warning(f"Could not inspect relationships for {model.__name__}: {e}")
        return []


def batch_query_by_ids(
    db: Session,
    model: Type,
    ids: List[int],
    batch_size: int = 1000
) -> List[Any]:
    """
    Query multiple records by IDs in batches to avoid large IN clauses.

    Args:
        db: Database session
        model: SQLAlchemy model class
        ids: List of IDs to query
        batch_size: Number of IDs per batch

    Returns:
        List of model instances

    Example:
        ```python
        # Query 5000 records in batches of 1000
        signals = batch_query_by_ids(db, Signal, signal_ids, batch_size=1000)
        ```
    """
    if not ids:
        return []

    results = []
    for i in range(0, len(ids), batch_size):
        batch_ids = ids[i:i + batch_size]
        batch_results = db.query(model).filter(model.id.in_(batch_ids)).all()
        results.extend(batch_results)

    return results


def aggregate_count_by_condition(
    db: Session,
    model: Type,
    conditions: List[tuple],
    label_prefix: str = "count"
) -> dict:
    """
    Aggregate counts by multiple conditions in a single query.
    Prevents N+1 queries when counting records by different conditions.

    Args:
        db: Database session
        model: SQLAlchemy model class
        conditions: List of (condition, label) tuples
                   condition is a SQLAlchemy filter expression
                   label is the key name for the result
        label_prefix: Prefix for label names

    Returns:
        Dictionary with count results

    Example:
        ```python
        # Before: Multiple queries
        total = db.query(User).count()
        active = db.query(User).filter(User.is_active == True).count()
        verified = db.query(User).filter(User.is_verified == True).count()

        # After: Single aggregated query
        counts = aggregate_count_by_condition(
            db,
            User,
            [
                (True, 'total'),  # No filter = total count
                (User.is_active == True, 'active'),
                (User.is_verified == True, 'verified')
            ]
        )
        # Returns: {'total': 100, 'active': 80, 'verified': 60}
        ```
    """
    if not conditions:
        return {}

    # Build aggregation expressions
    aggregations = []
    for condition, label in conditions:
        if condition is True:
            # No filter - count all
            aggregations.append(
                func.count(model.id).label(f"{label_prefix}_{label}")
            )
        else:
            # Conditional count
            aggregations.append(
                func.sum(
                    case((condition, 1), else_=0)
                ).label(f"{label_prefix}_{label}")
            )

    # Execute single query
    result = db.query(*aggregations).first()

    # Convert to dictionary
    return {
        label: getattr(result, f"{label_prefix}_{label}", 0) or 0
        for _, label in conditions
    }


def optimize_pagination_query(
    query: Query,
    limit: int,
    offset: int,
    order_by: Optional[Any] = None
) -> Query:
    """
    Optimize pagination query with proper ordering and limits.

    Args:
        query: SQLAlchemy query object
        limit: Maximum number of results
        offset: Number of results to skip
        order_by: Column or expression to order by (default: primary key)

    Returns:
        Optimized pagination query

    Example:
        ```python
        # Optimized pagination
        query = optimize_pagination_query(
            db.query(Signal),
            limit=50,
            offset=0,
            order_by=Signal.created_at.desc()
        )
        signals = query.all()
        ```
    """
    if order_by is not None:
        query = query.order_by(order_by)

    if limit > 0:
        query = query.limit(limit)

    if offset > 0:
        query = query.offset(offset)

    return query


def get_query_count(query: Query) -> int:
    """
    Get count of query results efficiently.
    Uses COUNT(*) which is faster than loading all records.

    Args:
        query: SQLAlchemy query object

    Returns:
        Total count of matching records

    Example:
        ```python
        # Efficient count
        count = get_query_count(db.query(Signal).filter(Signal.is_active == True))
        ```
    """
    # Remove limit/offset for accurate count
    count_query = query.statement.with_only_columns([func.count()]).order_by(None)
    return query.session.execute(count_query).scalar() or 0


def optimize_bulk_operations(
    db: Session,
    model: Type,
    records: List[dict],
    batch_size: int = 1000
) -> List[Any]:
    """
    Optimize bulk insert/update operations by batching.

    Args:
        db: Database session
        model: SQLAlchemy model class
        records: List of dictionaries with record data
        batch_size: Number of records per batch

    Returns:
        List of created/updated model instances

    Example:
        ```python
        # Bulk insert in batches
        signals = optimize_bulk_operations(
            db,
            Signal,
            signal_data_list,
            batch_size=1000
        )
        ```
    """
    results = []
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        batch_objects = [model(**record) for record in batch]
        db.bulk_insert_mappings(model, batch)
        results.extend(batch_objects)

    return results
