import psycopg2
from psycopg2 import sql
from typing import Optional, Dict, List

class DBClient:
    def __init__(self, dbname: str, user: str, password: str, host: str = 'localhost', port='5432'):
        self.connection_params = {
            'dbname': dbname,
            'user': user,
            'password': password,
            'host': host,  # Change this to use the host parameter
            'connect_timeout': 60, # Add a connection timeout,
            'port': port
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

    def get_user(self, phone_number: str) -> Optional[Dict[str, str]]:
        """
        Retrieve the user's information based on the phone number.
        
        :param phone_number: The phone number to search for.
        :return: A dictionary containing the user's information or None if not found.
        """
        self._connect()
        if self.conn is None:
            return None
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT phone_number, assistant_id, openai_api_key FROM users WHERE phone_number = %s", (phone_number,))
                result = cur.fetchone()
                if result:
                    return {
                        "phone_number": result[0],
                        "assistant_id": result[1],
                        "openai_api_key": result[2]
                    }
                return None
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
        finally:
            self._disconnect()

    def add_user(self, phone_number: str, assistant_id: str, openai_api_key: str) -> bool:
        self._connect()
        if self.conn is None:
            return False
        try:
            with self.conn.cursor() as cur:
                cur.execute("INSERT INTO users (phone_number, assistant_id, openai_api_key) VALUES (%s, %s, %s)", 
                            (phone_number, assistant_id, openai_api_key))
                self.conn.commit()
                return True
        except Exception as e:
            print(f"Error adding user: {e}")
            return False
        finally:
            self._disconnect()

    def update_user(self, phone_number: str, assistant_id: str, openai_api_key: str) -> bool:
        self._connect()
        if self.conn is None:
            return False
        try:
            with self.conn.cursor() as cur:
                cur.execute("UPDATE users SET assistant_id = %s, openai_api_key = %s WHERE phone_number = %s", 
                            (assistant_id, openai_api_key, phone_number))
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
                cur.execute("SELECT phone_number, assistant_id, openai_api_key FROM users")
                users = [{"phone_number": row[0], "assistant_id": row[1], "openai_api_key": row[2]} for row in cur.fetchall()]
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