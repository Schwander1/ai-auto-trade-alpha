"""
Cache TTL constants for consistent caching across the application
"""
# Cache TTL values in seconds
CACHE_TTL_SHORT = 30  # 30 seconds - for frequently changing data (trading status)
CACHE_TTL_MEDIUM = 60  # 1 minute - for moderately changing data (signals, security metrics)
CACHE_TTL_LONG = 300  # 5 minutes - for relatively static data (user profiles, subscriptions, analytics)
CACHE_TTL_VERY_LONG = 3600  # 1 hour - for rarely changing data

# Specific cache TTLs by use case
CACHE_TTL_USER_PROFILE = CACHE_TTL_LONG  # 5 minutes
CACHE_TTL_SIGNALS = CACHE_TTL_MEDIUM  # 1 minute
CACHE_TTL_SIGNAL_HISTORY = CACHE_TTL_LONG  # 5 minutes
CACHE_TTL_SIGNAL_EXPORT = CACHE_TTL_SHORT  # 30 seconds
CACHE_TTL_TRADING_STATUS = CACHE_TTL_SHORT  # 30 seconds
CACHE_TTL_SECURITY_METRICS = CACHE_TTL_MEDIUM  # 1 minute
CACHE_TTL_ANALYTICS = CACHE_TTL_LONG  # 5 minutes
CACHE_TTL_SUBSCRIPTION = CACHE_TTL_LONG  # 5 minutes
CACHE_TTL_USER_LIST = CACHE_TTL_MEDIUM  # 1 minute

