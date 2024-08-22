import psycopg2
from typing import Optional, Dict, List
import json

from ..User.User import User

class DBClient:
    def __init__(self, dbname: str, user: str, password: str, host: str = 'localhost', port='5432'):
        self.connection_params = {
            'dbname': dbname,
            'user': user,
            'password': password,
            'host': host,
            'connect_timeout': 60,
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

    def get_user(self, phone_number: str) -> Optional[User]:
        """
        Retrieve the user's information based on the phone number.
        
        :param phone_number: The phone number to search for.
        :return: An instance of the User class or None if not found.
        """
        self._connect()
        if self.conn is None:
            return None
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT phone_number, assistant_id, api_keys, email FROM users WHERE phone_number = %s", (phone_number,))
                result = cur.fetchone()
                if result:
                    return User(
                        phone_number=result[0],
                        assistant_id=result[1],
                        api_keys=result[2],
                        email=result[3]
                    )
                return None
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
        finally:
            self._disconnect()

    def add_user(self, user: User) -> bool:
        """
        Add a new user to the database.
        
        :param user: An instance of the User class containing the user's information.
        :return: True if the user was added successfully, False otherwise.
        """
        self._connect()
        if self.conn is None:
            return False
        try:
            with self.conn.cursor() as cur:
                cur.execute("INSERT INTO users (phone_number, assistant_id, api_keys, email) VALUES (%s, %s, %s, %s)", 
                            (user.phone_number, user.assistant_id, user.api_keys, user.email))
                self.conn.commit()
                return True
        except Exception as e:
            print(f"Error adding user: {e}")
            return False
        finally:
            self._disconnect()

    def update_user(self, user: User) -> bool:
        """
        Update the user's information in the database.
        
        :param user: An instance of the User class containing the updated user's information.
        :return: True if the user was updated successfully, False otherwise.
        """
        self._connect()
        if self.conn is None:
            return False
        try:
            with self.conn.cursor() as cur:
                cur.execute("UPDATE users SET assistant_id = %s, api_keys = %s, email = %s WHERE phone_number = %s", 
                            (user.assistant_id, json.dumps(user.api_keys), user.email, user.phone_number))
                self.conn.commit()
                return True
        except Exception as e:
            print(f"Error updating user: {e}")
            return False
        finally:
            self._disconnect()

    def remove_user(self, user: User) -> bool:
        """
        Remove a user from the database.
        
        :param user: An instance of the User class.
        :return: True if the user was removed successfully, False otherwise.
        """
        self._connect()
        if self.conn is None:
            return False
        try:
            with self.conn.cursor() as cur:
                cur.execute("DELETE FROM users WHERE phone_number = %s", (user.phone_number,))
                self.conn.commit()
                return True
        except Exception as e:
            print(f"Error removing user: {e}")
            return False
        finally:
            self._disconnect()

    def get_all_users(self) -> List[User]:
        """
        Retrieve all users from the database.
        :return: A list of User instances.
        """
        self._connect()
        if self.conn is None:
            return []
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT phone_number, assistant_id, api_keys, email FROM users")
                users = [
                    User(
                        phone_number=row[0],
                        assistant_id=row[1],
                        api_keys=row[2],
                        email=row[3]
                    )
                    for row in cur.fetchall()
                ]
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

    def add_api_key(self, user: User, api_key_name: str, api_key_value: str) -> bool:
        """
        Add or update an API key in the user's api_keys JSON object.

        :param user: An instance of the User class.
        :param api_key_name: The name of the API key (e.g., "openai_api_key").
        :param api_key_value: The value of the API key.
        :return: True if the API key was added/updated successfully, False otherwise.
        """
        self._connect()
        if self.conn is None:
            return False
        try:
            with self.conn.cursor() as cur:
                # Get the current api_keys value
                cur.execute("SELECT api_keys FROM users WHERE phone_number = %s", (user.phone_number,))
                current_api_keys = cur.fetchone()[0]

                # Update or add the new API key
                if current_api_keys is None:
                    current_api_keys = {}
                else:
                    current_api_keys = dict(current_api_keys)

                current_api_keys[api_key_name] = api_key_value

                # Update the database with the new api_keys
                cur.execute(
                    "UPDATE users SET api_keys = %s WHERE phone_number = %s",
                    (json.dumps(current_api_keys), user.phone_number)
                )
                self.conn.commit()

                # Update the user object in memory
                user.api_keys = current_api_keys

                return True
        except Exception as e:
            print(f"Error adding/updating API key: {e}")
            return False
        finally:
            self._disconnect()

    def add_api_key_to_all_users(self, api_key_name: str, api_key_value: str) -> bool:
        """
        Add or update an API key in the api_keys JSON object for all users.

        :param api_key_name: The name of the API key (e.g., "openai_api_key").
        :param api_key_value: The value of the API key.
        :return: True if the API key was added/updated successfully for all users, False otherwise.
        """
        self._connect()
        if self.conn is None:
            return False
        try:
            with self.conn.cursor() as cur:
                # Fetch all users
                cur.execute("SELECT phone_number, api_keys FROM users")
                users = cur.fetchall()

                # Iterate through all users and update their api_keys
                for user in users:
                    phone_number = user[0]
                    current_api_keys = user[1]

                    # Update or add the new API key
                    if current_api_keys is None:
                        current_api_keys = {}
                    else:
                        current_api_keys = dict(current_api_keys)

                    current_api_keys[api_key_name] = api_key_value

                    # Update the database with the new api_keys
                    cur.execute(
                        "UPDATE users SET api_keys = %s WHERE phone_number = %s",
                        (json.dumps(current_api_keys), phone_number)
                    )

                # Commit all changes at once
                self.conn.commit()

                return True
        except Exception as e:
            print(f"Error adding/updating API key for all users: {e}")
            return False
        finally:
            self._disconnect()



__all__ = ['DBClient']
