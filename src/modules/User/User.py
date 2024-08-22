

from typing import Optional


class User:
    def __init__(self, assistant_id: str, api_keys: dict, phone_number: str, email: Optional[str] = None) -> None:
        self.assistant_id = assistant_id
        self.api_keys = api_keys
        self.phone_number = phone_number
        self.email = email

    def __repr__(self):
        return f"User(phone_number={self.phone_number}, assistant_id={self.assistant_id}, api_keys={self.api_keys}, email={self.email})"
