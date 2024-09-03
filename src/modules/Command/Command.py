
from typing import Any


class Command:
    name: str
    action: callable

    def __init__(self, name: str, action: callable) -> None:
        self.name = name
        self.action = action

    def execute(self, *args: Any) -> Any:
        return self.action(*args)

