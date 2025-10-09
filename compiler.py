import re
from collections import namedtuple

# --------------------------
# Lexer
# --------------------------
Token = namedtuple("Token", ["type", "value"])

TOKEN_SPEC = [
    # Control flow
    ("WHILE", r"> enter .* while .*"),
    ("IF", r"> inspect whether .*"),
    ("LEAVE", r"> leave .*"),
    # Statements
    ("ASSIGN", r"The [a-zA-Z_][a-zA-Z0-9_]* transforms into .+?\."),
    ("PRINT", r"You speak of .+?\."),
    ("INPUT", r"You seek wisdom from beyond and call it [a-zA-Z_][a-zA-Z0-9_]*\."),
    # Expression helpers
    ("AND", r"\band\b"),
    ("OR", r"or perhaps|or"),
    ("NOT", r"is not"),
    ("EQ", r"is much like"),
    ("NEQ", r"differs from"),
    ("LT", r"stands before"),
    ("GT", r"towers above"),
    ("LE", r"stands no further than"),
    ("GE", r"stands not below"),
    ("PLUS", r"reflect on all you have learned:"),
    ("MINUS", r"recall the distance between"),
    ("MUL", r"envision .* by .*"),
    ("DIV", r"divide .* among .*"),
    ("MOD", r"keep what remains of .* after sharing with .*"),
    ("NEWLINE", r"\n"),
    ("SKIP", r"[ \t]+"),
    # Fallback
    ("STMT", r".+?\."),
]

token_re = re.compile("|".join(f"(?P<{name}>{regex})" for name, regex in TOKEN_SPEC), re.IGNORECASE)

def tokenize(code):
    tokens = []
    for mo in token_re.finditer(code):
        kind = mo.lastgroup
        value = mo.group().strip()
        if kind in ("SKIP", "NEWLINE"):
            continue
        tokens.append(Token(kind, value))
    return tokens

# --------------------------
# AST Node
# --------------------------
class Node:
    def __init__(self, nodetype, children=None, value=None):
        self.type = nodetype
        self.children = children or []
        self.value = value

    def __repr__(self, level=0):
        ret = "  " * level + f"{self.type}"
        if self.value:
            ret += f" ({self.value})"
        ret += "\n"
        for child in self.children:
            ret += child.__repr__(level + 1)
        return ret

# --------------------------
# Parser
# --------------------------
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def eat(self, ttype=None):
        tok = self.current()
        if tok and (ttype is None or tok.type == ttype):
            self.pos += 1
            return tok
        return None

    def parse(self):
        nodes = []
        while self.current():
            node = self.statement()
            if node:
                nodes.append(node)
            else:
                self.pos += 1 # skip unknown token
        return Node("Program", nodes)

    # ----------------------
    # Statements
    # ----------------------
    def statement(self):
        tok = self.current()
        if not tok:
            return None
        if tok.type == "INPUT":
            return self.input_stmt()
        elif tok.type == "ASSIGN":
            return self.assign_stmt()
        elif tok.type == "PRINT":
            return self.print_stmt()
        elif tok.type == "WHILE":
            return self.while_stmt()
        elif tok.type == "IF":
            return self.if_stmt()
        elif tok.type == "LEAVE":
            self.eat("LEAVE")
            return Node("EndBlock")
        elif tok.type == "STMT":
            # generic narrative line
            t = self.eat("STMT")
            return Node("Stmt", value=t.value)
        return None

    def input_stmt(self):
        tok = self.eat("INPUT")
        var_name = tok.value.split()[-1].replace(".", "")
        return Node("Input", [Node("Var", value=var_name)])

    def assign_stmt(self):
        tok = self.eat("ASSIGN")
        match = re.match(r"The (\w+) transforms into (.+?)\.", tok.value, re.IGNORECASE)
        if match:
            lhs, rhs = match.groups()
            return Node("Assign", [Node("Var", value=lhs), self.expr_from_text(rhs)])
        return None

    def print_stmt(self):
        tok = self.eat("PRINT")
        expr_text = tok.value[len("You speak of "):].replace(".", "").strip()
        return Node("Print", [self.expr_from_text(expr_text)])

    def while_stmt(self):
        tok = self.eat("WHILE")
        cond_text = re.search(r"while (.+)", tok.value, re.IGNORECASE).group(1)
        return Node("While", [self.expr_from_text(cond_text)])

    def if_stmt(self):
        tok = self.eat("IF")
        cond_text = re.search(r"whether (.+)", tok.value, re.IGNORECASE).group(1)
        return Node("If", [self.expr_from_text(cond_text)])

    # ----------------------
    # Expressions 
    # ----------------------
    def expr_from_text(self, text):
        # literals
        text = text.replace("nothing", "0")
        for lit in ["all", "universe", "everything"]:
            text = text.replace(lit, "1")
        # arithmetic
        if " and " in text:
            parts = [p.strip() for p in text.split(" and ")]
            return Node("BinOp", [Node("Expr", value=parts[0]), Node("Expr", value=parts[1])], value="+")
        if " differs from " in text:
            a, b = text.split(" differs from ")
            return Node("BinOp", [Node("Expr", value=a.strip()), Node("Expr", value=b.strip())], value="!=")
        if " is much like " in text:
            a, b = text.split(" is much like ")
            return Node("BinOp", [Node("Expr", value=a.strip()), Node("Expr", value=b.strip())], value="==")
        if " stands before " in text:
            a, b = text.split(" stands before ")
            return Node("BinOp", [Node("Expr", value=a.strip()), Node("Expr", value=b.strip())], value="<")
        if " towers above " in text:
            a, b = text.split(" towers above ")
            return Node("BinOp", [Node("Expr", value=a.strip()), Node("Expr", value=b.strip())], value=">")
        # fallback
        return Node("Expr", value=text.strip())

# --------------------------
# Run example
# --------------------------
if __name__ == "__main__":
    code = """
    The adventure begins.

    You seek wisdom from beyond and call it the final_quest.
    The first_light transforms into nothing.
    The second_light transforms into all.
    The journey transforms into nothing.

    > enter cavern while the journey stands before the final_quest
    The reflection transforms into the first_light and the second_light.
    The first light transforms into the second_light.
    The second light transforms into the reflection.
    The journey transforms into the journey and the universe.
    > leave cavern

    You speak of the second_light.

    The adventure ends.
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    tree = parser.parse()
    print(tree)
