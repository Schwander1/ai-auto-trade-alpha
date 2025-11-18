"""Persistent webhook retry queue using Redis"""
import json
import logging
import asyncio
from typing import Dict, Optional, List
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, asdict
from enum import Enum

from backend.core.cache import redis_client
from backend.core.config import settings

logger = logging.getLogger(__name__)


class WebhookStatus(str, Enum):
    """Webhook delivery status"""
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"
    EXPIRED = "expired"


@dataclass
class WebhookRetryJob:
    """Webhook retry job data structure"""
    webhook_id: str
    url: str
    payload: Dict
    headers: Dict
    method: str = "POST"
    max_retries: int = 5
    retry_count: int = 0
    status: WebhookStatus = WebhookStatus.PENDING
    created_at: str = None
    next_retry_at: str = None
    last_error: Optional[str] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc).isoformat()
        if self.next_retry_at is None:
            # First retry after 1 minute
            self.next_retry_at = (datetime.now(timezone.utc) + timedelta(minutes=1)).isoformat()

    def to_dict(self) -> Dict:
        """Convert to dictionary for Redis storage"""
        data = asdict(self)
        data['status'] = self.status.value
        return data

    @classmethod
    def from_dict(cls, data: Dict) -> 'WebhookRetryJob':
        """Create from dictionary"""
        data['status'] = WebhookStatus(data['status'])
        return cls(**data)


class WebhookRetryQueue:
    """Persistent webhook retry queue using Redis"""

    def __init__(self):
        self.redis = redis_client
        self.queue_key = "webhook:retry:queue"
        self.job_key_prefix = "webhook:retry:job:"
        self.processing_key = "webhook:retry:processing"
        self.max_retry_delay = timedelta(hours=24)  # Max 24 hours between retries
        self.retry_delays = [
            timedelta(minutes=1),    # 1st retry: 1 minute
            timedelta(minutes=5),    # 2nd retry: 5 minutes
            timedelta(minutes=15),   # 3rd retry: 15 minutes
            timedelta(hours=1),      # 4th retry: 1 hour
            timedelta(hours=6),      # 5th retry: 6 hours
        ]

    def _get_job_key(self, webhook_id: str) -> str:
        """Get Redis key for a job"""
        return f"{self.job_key_prefix}{webhook_id}"

    async def enqueue(
        self,
        webhook_id: str,
        url: str,
        payload: Dict,
        headers: Dict,
        method: str = "POST",
        max_retries: int = 5
    ) -> bool:
        """
        Enqueue a webhook for retry

        Args:
            webhook_id: Unique identifier for the webhook
            url: Webhook URL
            payload: Request payload
            headers: Request headers
            method: HTTP method (default: POST)
            max_retries: Maximum number of retry attempts

        Returns:
            True if enqueued successfully, False otherwise
        """
        if not self.redis:
            logger.warning("Redis not available, webhook retry queue disabled")
            return False

        try:
            job = WebhookRetryJob(
                webhook_id=webhook_id,
                url=url,
                payload=payload,
                headers=headers,
                method=method,
                max_retries=max_retries
            )

            # Store job data
            job_key = self._get_job_key(webhook_id)
            self.redis.setex(
                job_key,
                int(self.max_retry_delay.total_seconds() * 2),  # TTL: 2x max retry delay
                json.dumps(job.to_dict())
            )

            # Add to sorted set (sorted by next_retry_at timestamp)
            next_retry_ts = datetime.fromisoformat(job.next_retry_at).timestamp()
            self.redis.zadd(self.queue_key, {webhook_id: next_retry_ts})

            logger.info(f"Enqueued webhook retry: {webhook_id} (retry at {job.next_retry_at})")
            return True

        except Exception as e:
            logger.error(f"Error enqueueing webhook retry: {e}", exc_info=True)
            return False

    async def dequeue(self, limit: int = 10) -> List[WebhookRetryJob]:
        """
        Dequeue webhooks ready for retry

        Args:
            limit: Maximum number of jobs to dequeue

        Returns:
            List of webhook jobs ready for retry
        """
        if not self.redis:
            return []

        try:
            now = datetime.now(timezone.utc).timestamp()

            # Get jobs ready for retry (next_retry_at <= now)
            job_ids = self.redis.zrangebyscore(
                self.queue_key,
                "-inf",
                now,
                start=0,
                num=limit
            )

            if not job_ids:
                return []

            jobs = []
            for job_id in job_ids:
                job_id_str = job_id.decode() if isinstance(job_id, bytes) else job_id

                # Get job data
                job_key = self._get_job_key(job_id_str)
                job_data = self.redis.get(job_key)

                if not job_data:
                    # Job expired or deleted, remove from queue
                    self.redis.zrem(self.queue_key, job_id_str)
                    continue

                try:
                    job_dict = json.loads(job_data)
                    job = WebhookRetryJob.from_dict(job_dict)

                    # Mark as processing
                    job.status = WebhookStatus.PROCESSING
                    self.redis.setex(
                        job_key,
                        int(self.max_retry_delay.total_seconds() * 2),
                        json.dumps(job.to_dict())
                    )

                    # Remove from queue (will be re-added if retry fails)
                    self.redis.zrem(self.queue_key, job_id_str)

                    jobs.append(job)

                except Exception as e:
                    logger.error(f"Error parsing job {job_id_str}: {e}")
                    # Remove invalid job
                    self.redis.zrem(self.queue_key, job_id_str)
                    self.redis.delete(job_key)

            return jobs

        except Exception as e:
            logger.error(f"Error dequeuing webhook retries: {e}", exc_info=True)
            return []

    async def mark_success(self, webhook_id: str) -> bool:
        """
        Mark a webhook as successfully delivered

        Args:
            webhook_id: Webhook identifier

        Returns:
            True if marked successfully
        """
        if not self.redis:
            return False

        try:
            job_key = self._get_job_key(webhook_id)
            job_data = self.redis.get(job_key)

            if job_data:
                job_dict = json.loads(job_data)
                job = WebhookRetryJob.from_dict(job_dict)
                job.status = WebhookStatus.SUCCESS

                # Update job
                self.redis.setex(
                    job_key,
                    86400,  # Keep for 24 hours for audit
                    json.dumps(job.to_dict())
                )

            # Remove from queue
            self.redis.zrem(self.queue_key, webhook_id)

            logger.info(f"Marked webhook as successful: {webhook_id}")
            return True

        except Exception as e:
            logger.error(f"Error marking webhook success: {e}", exc_info=True)
            return False

    async def mark_failed(
        self,
        webhook_id: str,
        error: str,
        retry: bool = True
    ) -> bool:
        """
        Mark a webhook as failed and schedule retry if applicable

        Args:
            webhook_id: Webhook identifier
            error: Error message
            retry: Whether to schedule a retry

        Returns:
            True if processed successfully
        """
        if not self.redis:
            return False

        try:
            job_key = self._get_job_key(webhook_id)
            job_data = self.redis.get(job_key)

            if not job_data:
                logger.warning(f"Job not found for webhook: {webhook_id}")
                return False

            job_dict = json.loads(job_data)
            job = WebhookRetryJob.from_dict(job_dict)
            job.last_error = error
            job.retry_count += 1

            # Check if we should retry
            if retry and job.retry_count < job.max_retries:
                # Calculate next retry time
                delay_index = min(job.retry_count - 1, len(self.retry_delays) - 1)
                delay = self.retry_delays[delay_index]
                job.next_retry_at = (datetime.now(timezone.utc) + delay).isoformat()
                job.status = WebhookStatus.PENDING

                # Re-add to queue
                next_retry_ts = datetime.fromisoformat(job.next_retry_at).timestamp()
                self.redis.zadd(self.queue_key, {webhook_id: next_retry_ts})

                logger.info(
                    f"Scheduled retry {job.retry_count}/{job.max_retries} for webhook {webhook_id} "
                    f"at {job.next_retry_at}"
                )
            else:
                # Max retries exceeded
                job.status = WebhookStatus.FAILED
                logger.warning(
                    f"Webhook {webhook_id} failed after {job.retry_count} retries: {error}"
                )

            # Update job
            self.redis.setex(
                job_key,
                int(self.max_retry_delay.total_seconds() * 2),
                json.dumps(job.to_dict())
            )

            return True

        except Exception as e:
            logger.error(f"Error marking webhook failed: {e}", exc_info=True)
            return False

    async def get_status(self, webhook_id: str) -> Optional[Dict]:
        """
        Get status of a webhook job

        Args:
            webhook_id: Webhook identifier

        Returns:
            Job status dictionary or None if not found
        """
        if not self.redis:
            return None

        try:
            job_key = self._get_job_key(webhook_id)
            job_data = self.redis.get(job_key)

            if not job_data:
                return None

            job_dict = json.loads(job_data)
            job = WebhookRetryJob.from_dict(job_dict)

            return {
                "webhook_id": job.webhook_id,
                "status": job.status.value,
                "retry_count": job.retry_count,
                "max_retries": job.max_retries,
                "next_retry_at": job.next_retry_at,
                "last_error": job.last_error,
                "created_at": job.created_at
            }

        except Exception as e:
            logger.error(f"Error getting webhook status: {e}", exc_info=True)
            return None


# Global instance
_webhook_retry_queue: Optional[WebhookRetryQueue] = None


def get_webhook_retry_queue() -> WebhookRetryQueue:
    """Get global webhook retry queue instance"""
    global _webhook_retry_queue
    if _webhook_retry_queue is None:
        _webhook_retry_queue = WebhookRetryQueue()
    return _webhook_retry_queue
