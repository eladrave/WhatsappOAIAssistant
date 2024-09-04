from .Command import Command

from typing import Any

class CommandHandler:
    def __init__(self, commands: dict) -> None:
        self.commands = commands

    def register_command(self, command: Command) -> None:
        self.commands[command.name] = command
    
    def execute_command(self, command_name: str, *args) -> Any:
        if command_name in self.commands:
            return self.commands[command_name].execute(*args)
        else:
            raise Exception(f"Command {command_name} not found")

    # method return str or None if no command is found
    def extract_command(self, message: str) -> str:
        for command in self.commands:
            if message.startswith(command):
                return command
        return None