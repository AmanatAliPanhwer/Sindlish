from .env import Environment

class Frame:
    """
    Represents a single function call execution context.
    """
    def __init__(self, name: str, statements: list, parent_env: Environment = None, slot_count: int = 0):
        self.name = name
        self.env = Environment(parent=parent_env)
        self.statements = statements
        self.slots = [None] * slot_count
        self.ip = 0
        self.return_value = None
        self.is_completed = False

    def __repr__(self):
        return f"<Frame {self.name} | IP: {self.ip}/{len(self.statements)}>"