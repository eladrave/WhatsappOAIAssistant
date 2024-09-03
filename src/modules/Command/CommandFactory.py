from .Command import Command

class CommandFactory:
    @staticmethod
    def create_command(name: str, action: callable) -> Command:
        return Command(name, action)

    