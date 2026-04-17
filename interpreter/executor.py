from ast_sind.nodes import *
from lexer.tokens import TokenType

class Interpreter:
    def __init__(self):
        self.variables = {}
    
    def visit(self, node):
        method_name = f"visit_{type(node).__name__}"
        method = getattr(self, method_name, self.no_visit_method)
        return method(node)
    
    def no_visit_method(self, node):
        raise Exception(f"No visit method for {type(node).__name__}")
    
    def visit_ProgramNode(self, node):
        for stmt in node.statements:
            self.visit(stmt)
    
    def visit_PrintNode(self, node):
        value = self.visit(node.value)
        print(value)
    
    def visit_NumberNode(self, node):
        return node.value
    
    def visit_StringNode(self, node):
        return node.value
    
    def visit_VariableNode(self, node):
        if node.name not in self.variables:
            raise Exception(f"Variable `{node.name}` is not defined")
        return self.variables[node.name]
    
    def visit_BinaryOpNode(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)

        if node.op.type == TokenType.GT:
            return left > right
        if node.op.type == TokenType.LT:
            return left < right
        
        raise Exception("Unknown Opration") 

    def visit_IfNode(self, node):
        condition = self.visit(node.condition)

        if condition:
            for stmt in node.body:
                self.visit(stmt)
            
        else:
            if node.else_body:
                for stmt in node.else_body:
                    self.visit(stmt)

    def visit_AssignNode(self, node):
        value = self.visit(node.value)
        self.variables[node.name] = value

    def visit_WhileNode(self, node):
        while self.visit(node.condition):
            for stmt in node.body:
                self.visit(stmt)
