import psycopg2
from psycopg2 import sql
from typing import Optional, Dict, List

class DBClient:
    def __init__(self, dbname: str, user: str, password: str, host: str = 'localhost'):
        self.connection_params = {
            'dbname': dbname,
            'user': user,
            'password': password,
            'host': host,
            'connect_timeout': 10  # Add a connection timeout
        }
        self.conn = None

    def _connect(self):
        try:
            if self.conn is None or self.conn.closed:
                self.conn = psycopg2.connect(**self.connection_params)
        except psycopg2.OperationalError as e:
            print(f"Error connecting to the database: {e}")
            self.conn = None

    def _disconnect(self):
        if self.conn is not None and not self.conn.closed:
            self.conn.close()

    def check_user_exists(self, phone_number: str) -> bool:
        self._connect()
        if self.conn is None:
            return False
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT 1 FROM users WHERE phone_number = %s", (phone_number,))
                return cur.fetchone() is not None
        except Exception as e:
            print(f"Error checking user existence: {e}")
            return False
        finally:
            self._disconnect()

    def get_assistant_id(self, phone_number: str) -> Optional[str]:
        self._connect()
        if self.conn is None:
            return None
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT assistant_id FROM users WHERE phone_number = %s", (phone_number,))
                result = cur.fetchone()
                return result[0] if result else None
        except Exception as e:
            print(f"Error getting assistant ID: {e}")
            return None
        finally:
            self._disconnect()

    def add_user(self, phone_number: str, assistant_id: str) -> bool:
        self._connect()
        if self.conn is None:
            return False
        try:
            with self.conn.cursor() as cur:
                cur.execute("INSERT INTO users (phone_number, assistant_id) VALUES (%s, %s)", (phone_number, assistant_id))
                self.conn.commit()
                return True
        except Exception as e:
            print(f"Error adding user: {e}")
            return False
        finally:
            self._disconnect()

    def update_user(self, phone_number: str, assistant_id: str) -> bool:
        self._connect()
        if self.conn is None:
            return False
        try:
            with self.conn.cursor() as cur:
                cur.execute("UPDATE users SET assistant_id = %s WHERE phone_number = %s", (assistant_id, phone_number))
                self.conn.commit()
                return True
        except Exception as e:
            print(f"Error updating user: {e}")
            return False
        finally:
            self._disconnect()

    def remove_user(self, phone_number: str) -> bool:
        self._connect()
        if self.conn is None:
            return False
        try:
            with self.conn.cursor() as cur:
                cur.execute("DELETE FROM users WHERE phone_number = %s", (phone_number,))
                self.conn.commit()
                return True
        except Exception as e:
            print(f"Error removing user: {e}")
            return False
        finally:
            self._disconnect()

    def get_all_users(self) -> List[Dict[str, str]]:
        self._connect()
        if self.conn is None:
            return []
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT phone_number, assistant_id FROM users")
                users = [{"phone_number": row[0], "assistant_id": row[1]} for row in cur.fetchall()]
                return users
        except Exception as e:
            print(f"Error getting all users: {e}")
            return []
        finally:
            self._disconnect()

    def read_config(self) -> Dict[str, str]:
        self._connect()
        if self.conn is None:
            return {}
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT key, value FROM config")
                config = {row[0]: row[1] for row in cur.fetchall()}
                return config
        except Exception as e:
            print(f"Error reading config: {e}")
            return {}
        finally:
            self._disconnect()

__all__ = ['DBClient']
