from contextlib import contextmanager
import psycopg2
from psycopg2 import sql
from master.config.logging import get_logger
from master.config.parser import arguments
from master.exceptions.db import DatabaseAccessError, DatabaseSessionError
from master.core.api import Meta

ROLE_TABLE_NAME = "user_roles"  # Table for storing user roles in PostgreSQL
_logger = get_logger(__name__)


class PostgresManager(metaclass=Meta):
    __meta_path__ = 'core.db.manager'

    def __init__(self):
        self.connections = {}

    def admin_connection(self):
        """Internal method to return a connection for role management."""
        try:
            admin_username = arguments.configuration['db_user']
            if admin_username in self.connections:
                return self.connections[admin_username]
            connection = psycopg2.connect(
                host=arguments.configuration['db_hostname'],
                port=arguments.configuration['db_port'],
                dbname=arguments.configuration['db_name'],
                password=arguments.configuration['db_password'],
                user=admin_username)
            return connection
        except psycopg2.Error as e:
            _logger.error(f"Error connecting to PostgreSQL: {e}")
            raise DatabaseSessionError("Could not establish a database connection.")

    def create_role(self, admin_user_id, target_user_id, role):
        """Allows an admin to assign a role to a user."""
        if not self.is_admin(admin_user_id):
            raise DatabaseAccessError("Only admins can create roles.")

        connection = self.admin_connection()
        cursor = connection.cursor()
        try:
            query = sql.SQL("INSERT INTO {table} (user_id, role) VALUES (%s, %s) ON CONFLICT (user_id) DO UPDATE SET role = %s").format(
                table=sql.Identifier(ROLE_TABLE_NAME))
            cursor.execute(query, (target_user_id, role, role))
            connection.commit()
            _logger.info(f"Role '{role}' assigned to user {target_user_id} by admin {admin_user_id}")
        except Exception as e:
            connection.rollback()
            _logger.error(f"Failed to assign role: {e}")
            raise e
        finally:
            cursor.close()
            connection.close()

    def get_role(self, user_id):
        """Fetches the role of a user."""
        connection = self.admin_connection()
        cursor = connection.cursor()
        try:
            query = sql.SQL("SELECT role FROM {table} WHERE user_id = %s").format(
                table=sql.Identifier(ROLE_TABLE_NAME))
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            _logger.error(f"Failed to get role: {e}")
            raise e
        finally:
            cursor.close()
            connection.close()

    def is_admin(self, user_id):
        """Checks if a user has an admin role."""
        return self.get_role(user_id) == "admin"

    def create_connection(self, user_id):
        """Creates a new PostgreSQL connection if the user is an admin."""
        if not self.is_admin(user_id):
            raise DatabaseAccessError("Only admins can create connections.")

        if user_id not in self.connections:
            self.connections[user_id] = self.admin_connection()
            _logger.info(f"Connection created for admin user {user_id}")
        else:
            _logger.info(f"Connection for user {user_id} already exists")

    def close_connection(self, user_id):
        """Closes a user's connection."""
        if user_id in self.connections:
            self.connections[user_id].close()
            del self.connections[user_id]
            _logger.info(f"Connection closed for user {user_id}")
        else:
            _logger.info(f"No connection found for user {user_id}")

    @contextmanager
    def transaction(self, user_id):
        """Executes a transaction block if the user has a connection."""
        if user_id not in self.connections:
            raise DatabaseSessionError(f"No connection found for user {user_id}")

        connection = self.connections[user_id]
        cursor = connection.cursor()

        try:
            yield cursor
            connection.commit()
        except Exception as e:
            connection.rollback()
            _logger.error(f"Transaction for user {user_id} failed: {e}")
            raise e
        finally:
            cursor.close()
