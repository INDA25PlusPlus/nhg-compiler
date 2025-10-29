import re
from collections import namedtuple

# ric said no ascii art, so i remove :crying face:

# Lexer
Token = namedtuple("Token", ["type", "value"])

TOKEN_SPEC = [
    ("WHILE", r"> enter .* while .*"),
    ("IF", r"> inspect whether .*"),
    ("LEAVE", r"> leave .*"),
    ("ASSIGN", r"The [a-zA-Z_][a-zA-Z0-9_]* transforms into .+?\."),
    ("PRINT", r"You speak of .+?\."),
    ("INPUT", r"You seek wisdom from beyond and call it [a-zA-Z_][a-zA-Z0-9_]*\."),
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

# AST Nodes
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

# Parser
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
    # Statements
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
            # generic statement
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
    # Expressions
    def expr_from_text(self, text):
        # literals
        text = text.replace("nothing", "0")
        for lit in ["all", "universe", "everything"]:
            text = text.replace(lit, "1")
        # arithmetic and comparisons
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

# Adventlang to Java Compiler
class JavaGenerator:
    def __init__(self, ast):
        self.ast = ast
        self.decls = {}        # var -> type ('int'|'String'|'boolean')
        self.output_lines = []
        self.indent_level = 2  # inside main start
        self.pending_lines = []  # lines to put inside main
    def indent(self):
        return " " * (4 * self.indent_level)
    def infer_types_first_pass(self):
        # Walk AST and infer variable types from assigns and inputs and literal appearances.
        def walk(node):
            if node is None:
                return
            if node.type == "Assign":
                varname = node.children[0].value
                rhs = node.children[1]
                t = self.infer_type(rhs)
                prev = self.decls.get(varname)
                if prev is None:
                    self.decls[varname] = t
                else:
                    # if previously int and now String, prefer String
                    if prev != t:
                        if "String" in (prev, t):
                            self.decls[varname] = "String"
                # walk rhs children
                walk(rhs)
            elif node.type == "Input":
                varname = node.children[0].value
                # assume int by default for numeric programs
                if varname not in self.decls:
                    self.decls[varname] = "int"
            else:
                for c in node.children:
                    walk(c)
        walk(self.ast)
    def infer_type(self, node):
        # simple inference
        if node.type == "Expr":
            v = node.value.strip()
            if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
                return "String"
            if re.fullmatch(r"\d+", v):
                return "int"
            # default to int for identifiers/numeric expressions
            return "int"
        if node.type == "BinOp":
            op = node.value
            if op in ("==", "!=", "<", ">", "<=", ">="):
                return "boolean"
            if op == "+":
                # could be sum or string concat; if any child is string literal, it's String
                left, right = node.children
                lt = self.infer_type(left)
                rt = self.infer_type(right)
                if lt == "String" or rt == "String":
                    return "String"
                return "int"
            # arithmetic -> int
            return "int"
        return "int"
    def expr_to_java(self, node):
        if node is None:
            return "0"
        if node.type == "Expr":
            v = node.value.strip()
            # quoted literal
            if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
                return v
            if re.fullmatch(r"\d+", v):
                return v
            # identifiers: strip optional articles like 'the' or 'a'
            v2 = re.sub(r'^(the|a|an)\s+', '', v, flags=re.IGNORECASE)
            # replace spaces with underscores for identifiers that had spaces (if any)
            return v2.replace(" ", "_")
        if node.type == "BinOp":
            op = node.value
            left = self.expr_to_java(node.children[0])
            right = self.expr_to_java(node.children[1])
            op_map = {
                "+": "+",
                "!=": "!=",
                "==": "==",
                "<": "<",
                ">": ">",
                "<=": "<=",
                ">=": ">="
            }
            jop = op_map.get(op, op)
            return f"({left} {jop} {right})"
        # fallback
        return "0"
    def generate(self):
        self.infer_types_first_pass()
        lines = []
        lines.append("import java.util.*;")
        lines.append("")
        lines.append("public class AdventProgram {")
        lines.append("    public static void main(String[] args) {")
        lines.append("        Scanner sc = new Scanner(System.in);")
        # declarations
        for var, typ in sorted(self.decls.items()):
            if typ == "String":
                lines.append(f"        {typ} {var} = \"\";")
            elif typ == "boolean":
                lines.append(f"        {typ} {var} = false;")
            else:
                lines.append(f"        {typ} {var} = 0;")
        # body
        self.indent_level = 2
        for stmt in self.ast.children:
            self.emit_node(stmt, lines)
        lines.append("        sc.close();")
        lines.append("    }")
        lines.append("}")
        return "\n".join(lines)
    def emit_node(self, node, lines):
        if node is None:
            return
        t = node.type
        if t == "Assign":
            lhs = node.children[0].value
            rhs = node.children[1]
            jexpr = self.expr_to_java(rhs)
            lines.append(f"{self.indent()}{lhs} = {jexpr};")
        elif t == "Print":
            expr = node.children[0]
            jexpr = self.expr_to_java(expr)
            # if jexpr is a bare identifier of int but the declared type is int, print it directly
            lines.append(f"{self.indent()}System.out.println({jexpr});")
        elif t == "Input":
            var = node.children[0].value
            # if declared type is String -> sc.nextLine(); else parseInt
            typ = self.decls.get(var, "int")
            if typ == "String":
                lines.append(f"{self.indent()}{var} = sc.nextLine();")
            else:
                lines.append(f"{self.indent()}{var} = Integer.parseInt(sc.nextLine());")
        elif t == "While":
            cond_node = node.children[0]
            jcond = self.expr_to_java(cond_node)
            lines.append(f"{self.indent()}while ({jcond}) {{")
            self.indent_level += 1
        elif t == "If":
            cond_node = node.children[0]
            jcond = self.expr_to_java(cond_node)
            lines.append(f"{self.indent()}if ({jcond}) {{")
            self.indent_level += 1
        elif t == "EndBlock":
            self.indent_level = max(1, self.indent_level - 1)
            lines.append(f"{self.indent()}}}")
        elif t == "Stmt":
            # generic statement, emit as comment
            lines.append(f"{self.indent()}// {node.value}")
        else:
            # descend
            for c in node.children:
                self.emit_node(c, lines)
            
if __name__ == "__main__":
    code = """
The adventure begins.

You seek wisdom from beyond and call it final_quest.
The first_light transforms into nothing.
The second_light transforms into all.
The journey transforms into nothing.

> enter cavern while the journey stands before the final_quest
The reflection transforms into the first_light and the second_light.
The first_light transforms into the second_light.
The second_light transforms into the reflection.
The journey transforms into the journey and the universe.
> leave cavern

You speak of the second_light.

The adventure ends.
"""
    tokens = tokenize(code)
    parser = Parser(tokens)
    tree = parser.parse()
    gen = JavaGenerator(tree)
    java_src = gen.generate()
    print(java_src)
    with open("AdventProgram.java", "w", encoding="utf-8") as f:
        f.write(java_src)
