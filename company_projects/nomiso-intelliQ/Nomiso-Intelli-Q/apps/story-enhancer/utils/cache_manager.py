import redis
import json
import logging
from config.settings import Settings
from redis import exceptions
import typing

# Ensure basic logging output if the root logger has no handlers yet (works when
# CacheManager is imported before the main application bootstraps logging).
if not logging.getLogger().handlers:
    logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

# Initialize module logger
logger = logging.getLogger(__name__)

class CacheManager:
    """
    A manager for caching data, with support for Redis or in-memory storage.

    This class provides a simple key-value store interface that can be backed by
    either a Redis server or a standard Python dictionary for in-memory caching.
    The choice of backend is determined by the application settings.
    """
    def __init__(self):
        """
        Initializes the CacheManager.

        It reads Redis connection settings and attempts to connect to the Redis server.
        If a connection cannot be established or if Redis is not configured, it falls
        back to using an in-memory dictionary for caching.
        """
        self.settings = Settings()
        self.is_redis = self.settings.redis_host is not None
        if self.is_redis:
            assert self.settings.redis_host is not None
            assert self.settings.redis_port is not None
            self.client = redis.Redis(
                host=self.settings.redis_host,
                port=self.settings.redis_port,
                password=self.settings.redis_password,
                db=0,
                decode_responses=True
            )
            try:
                self.client.ping()
                logger.info("[REDIS] Connected to Redis successfully at %s:%s", self.settings.redis_host, self.settings.redis_port)
            except exceptions.ConnectionError as e:
                logger.warning("[REDIS] Could not connect to Redis: %s. Falling back to in-memory cache.", e)
                self.is_redis = False
                self.client = {}
        else:
            logger.info("[CACHE] Using in-memory cache backend (Redis not configured).")
            self.client = {}

    def get(self, key):
        """
        Retrieve an item from the cache.

        If using Redis, this method deserializes the value from JSON.

        Args:
            key: The key of the item to retrieve.

        Returns:
            The value associated with the key, or None if the key is not found.
        """
        if self.is_redis:
            client = typing.cast(redis.Redis, self.client)
            value = client.get(key)
            if value is not None:
                assert isinstance(value, str)
                return json.loads(value)
            return None
        
        client = typing.cast(dict, self.client)
        return client.get(key)

    def set(self, key, value, ex=None):
        """
        Set an item in the cache.

        If using Redis, this method serializes the value to JSON before storing it.

        Args:
            key: The key of the item to set.
            value: The value to be stored.
            ex (Optional[int]): For Redis, the expiration time in seconds.
        """
        if self.is_redis:
            client = typing.cast(redis.Redis, self.client)
            client.set(key, json.dumps(value), ex=ex)
        else:
            client = typing.cast(dict, self.client)
            client[key] = value

    def delete(self, key):
        """
        Delete an item from the cache.

        Args:
            key: The key of the item to delete.
        """
        if self.is_redis:
            client = typing.cast(redis.Redis, self.client)
            client.delete(key)
        else:
            client = typing.cast(dict, self.client)
            if key in client:
                del client[key]

cache_manager = CacheManager()
"""A global instance of the CacheManager for easy access throughout the application.""" 