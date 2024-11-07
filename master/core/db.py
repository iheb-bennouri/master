from contextlib import contextmanager
import redis
from master.config.logging import get_logger
from master.exceptions.db import AccessError
from master.core.api import Meta

role_key_prefix = "user_roles:"  # Prefix for storing user roles in Redis
_logger = get_logger(__name__)


class RedisManager(metaclass=Meta):
    __meta_path__ = 'core.db.manager'

    def __init__(self):
        self.connections = {}

    @classmethod
    def _get_connection(cls):
        """Internal method to return a connection for role management."""
        return redis.StrictRedis(host='localhost', port=6379, db=0)

    def create_role(self, admin_user_id, target_user_id, role):
        """Allows an admin to assign a role to a user."""
        if not self.is_admin(admin_user_id):
            raise AccessError("Only admins can create roles.")

        connection = self._get_connection()
        connection.set(f"{role_key_prefix}{target_user_id}", role)
        _logger.info(f"Role '{role}' assigned to user {target_user_id} by admin {admin_user_id}")

    def get_role(self, user_id):
        """Fetches the role of a user."""
        connection = self._get_connection()
        role = connection.get(f"{role_key_prefix}{user_id}")
        return role.decode() if role else None

    def is_admin(self, user_id):
        """Checks if a user has an admin role."""
        return self.get_role(user_id) == "admin"

    def create_connection(self, user_id, host='localhost', port=6379, db=0):
        """Creates a new Redis connection if the user is an admin."""
        if not self.is_admin(user_id):
            raise AccessError("Only admins can create connections.")

        if user_id not in self.connections:
            self.connections[user_id] = redis.StrictRedis(host=host, port=port, db=db)
            _logger.info(f"Connection created for admin user {user_id}")
        else:
            _logger.info(f"Connection for user {user_id} already exists")

    def close_connection(self, user_id):
        """Closes a user's connection."""
        if user_id in self.connections:
            del self.connections[user_id]
            _logger.info(f"Connection closed for user {user_id}")
        else:
            _logger.info(f"No connection found for user {user_id}")

    @contextmanager
    def transaction(self, user_id):
        """Executes a transaction block if the user has a connection."""
        if user_id not in self.connections:
            raise ObjectError(f"No connection found for user {user_id}")

        connection = self.connections[user_id]
        pipeline = connection.pipeline()

        try:
            yield pipeline
            pipeline.execute()
        except Exception as e:
            pipeline.reset()
            _logger.error(f"Transaction for user {user_id} failed: {e}")
            raise e
