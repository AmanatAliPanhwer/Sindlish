class Node:
    pass

class NumberNode(Node):
    def __init__(self, value):
        self.value = value


class StringNode(Node):
    def __init__(self, value):
        self.value = value

class VariableNode(Node):
    def __init__(self, name):
        self.name = name

class BinaryOpNode(Node):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class PrintNode(Node):
    def __init__(self, value):
        self.value = value

class IfNode(Node):
    def __init__(self, condition, body, else_body):
        self.condition = condition
        self.body = body
        self.else_body = else_body

class ProgramNode(Node):
    def __init__(self, statements):
        self.statements = statements

class AssignNode(Node):
    def __init__(self, name, value):
        self.name = name
        self.value = value
