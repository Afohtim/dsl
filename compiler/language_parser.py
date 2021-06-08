import lexer
assembly_code = ""
var_map = dict()
stack_index = -4
declared = set()
label_counters = dict()

command_stack = ""
tokens = []
current_token = lexer.Token


def next_token(n=1):
    global tokens
    for i in range(n):
        if len(tokens) > 0:
            tokens = tokens[1:]
    if tokens:
        return tokens[0]
    else:
        return lexer.Token("eof", "eof", 0, 0)


def lookup_token(n):
    global tokens
    return tokens[n]


vector_view_count = 0


def next_vector_view():
    global vector_view_count
    res = f"vector_view_{vector_view_count}"
    vector_view_count += 1
    return res

temp_var_count = 0


def get_temp_var_name():
    global temp_var_count
    res = f"temp_var{temp_var_count}"
    temp_var_count += 1
    return res


class ASTNode:
    def __init__(self, type="", content=""):
        self.children = []
        self.content = content
        self.type = type
        self.expression_type = "num"
        self.variable_name = None

    def codegen(self):
        cgen = ""
        children_code = []
        for child in self.children:
            if child.expression_type == "num" or child.type == "id":
                children_code.append(child.codegen())
                if child.expression_type != "num" and child.type != "id":
                    cgen += child.codegen()
                    children_code[-1] = child.variable_name
            else:
                cgen += child.codegen()
                children_code.append(child.variable_name)

        if self.type == "op":
            if self.children[0].expression_type == "num" and self.children[1].expression_type == "num":
                cgen += children_code[0]
                cgen += " " + self.content + " "
                cgen += children_code[1]
            else:
                if self.content == '.':
                    self.expression_type = "scalar"
                    self.variable_name = get_temp_var_name()
                    cgen += f"scalar_result_t {self.variable_name} = vector_ddot({children_code[0]}, {children_code[1]}) ;\n" \
                            f"printf(\"status=%d, result=%g\\n\", res.status, res.result) ;\n"

        elif self.type in ["id", "num"]:
            cgen = f" {self.content} "
        elif self.type == "declaration":
            if self.content in ["int", "double"]:
                if len(self.children) == 2:
                    if self.children[1].expression_type == "scalar":
                        cgen += f"double {children_code[0]} = {children_code[1]}.res ;\n"
                    else:
                        cgen += f"{self.content} {children_code[0]} = {children_code[1]};\n"
                else:
                    cgen += f"{self.content} {children_code[0]};\n"
            elif self.content == "vector":
                if len(self.children) == 1:
                    cgen += f"vector_t {children_code[0]} ;\n"
                else:
                    cgen += f"vector_t {children_code[0]} = vector_from_view(vgp_clone(&{children_code[1]}.vector), true) ;\n"

        elif self.type == "assign":
            cgen += f"{children_code[0]} {self.content} {children_code[1]};\n"
        elif self.type == "block":
            cgen += '{\n'
            for i in children_code:
                cgen += i
            cgen += '\n}\n'
        elif self.type == "program":
            cgen += children_code[0]
        elif self.type == "func":
            cgen += f"{self.children[0].content} {self.children[1].content} ()" + "{\n"
            for child in children_code[2:]:
                cgen += child
            cgen += '\n}\n'
        elif self.type == 'if':
            if len(self.children) == 2:
                cgen += f"if({children_code[0]})" + children_code[1]
            else:
                cgen += f"if({children_code[0]})" + children_code[1] + "else" + children_code[2]
        elif self.type == "return":
            cgen += "return " + children_code[0] + ';'
        elif self.type == "while":
            cgen += f"while({children_code[0]}) {children_code[1]}"
        elif self.type == "do":
            block = children_code[0]
            while block[-1] == '\n':
                block = block[:-1]
            cgen += f"do{block} while({children_code[1]});\n"
        elif self.type == "vector":
            arguments = ""
            for child in children_code:
                if arguments:
                    arguments += ", "
                arguments += child
            self.variable_name = next_vector_view()
            cgen += f"vector_view_t {self.variable_name} = vector_view_from_array({len(self.children)}, (double []) {arguments}) ;\n"
        else:
            cgen += self.type + ' ' + self.content + ' '
            for child in children_code:
                cgen += child
            cgen += '\n'
        return cgen



def emit(string):
    global assembly_code
    assembly_code = assembly_code + string


def get_new_label(s):
    if s not in label_counters.keys():
        label_counters[s] = 0
    new_label = s + str(label_counters[s])
    label_counters[s] += 1
    return new_label


"""
EXPECT
"""


def fail(s):
    print(s)
    raise Exception(s)


def assert_token(token, string, forced_fail=False):
    if not forced_fail and token.content() == string:
        return True
    else:
        # TODO exception
        fail("expected \"{str}\" but got \"{token}\" at {line}:{char}".format(str=string, token=token.content(),
                                                                              line=token.line(), char=token.char()))


def token_is_type(token):
    if token.content() in ["int", "double", "vector", "matrix"]:
        return True


def assert_token_identifier(token):
    if token.is_identifier():
        return True
    else:
        return assert_token(token, "")


"""
PARSING
"""



def parse_factor():
    # TODO postfix ++ --
    global current_token
    node = ASTNode()
    if current_token.content() == '(':
        node.type = "()"
        current_token = next_token()
        node.children.append(parse_expr())
        assert_token(current_token, ')')
        current_token = next_token()
        return node
    elif current_token.content().isnumeric():
        node.content = current_token.content()
        node.type = "num"
        current_token = next_token()
        return node

    elif current_token.is_identifier():
        if var_map[current_token.content()] == "vector":
            node.expression_type = 'vec'
        elif var_map[current_token.content()] == "matrix":
            node.expression_type = 'mtx'
        #offset = var_map[tokens[0].content()]
        node.content = current_token.content()
        node.type = "id"
        current_token = next_token()
        return node

    elif current_token.content() == '`':
        node.type = "vector"
        node.expression_type = "vec"
        current_token = next_token()
        while current_token.content() != '`':
            node.children.append(parse_expr())
            if current_token.content() == ',':
                current_token = next_token()
        current_token = next_token()
        return node
    else:
        return assert_token(tokens[0], "")
    return node


def parse_unary_expr():
    # TODO prefix ++ --
    global current_token
    node = ASTNode()
    if current_token.content() in ['+', '-', '!', '~']:
        node.content = current_token.content()
        node.type = "uop"
        node.content = current_token.content()
        node.children.append(parse_expr())
    else:
        node = parse_factor()

    return node


def parse_term():
    global current_token
    node = parse_unary_expr()
    while current_token.content() in ['*', '/', '%', '.']:
        child = node
        node = ASTNode()
        node.children.append(child)
        node.type = "op"
        node.content = current_token.content()
        current_token = next_token()
        node.children.append(parse_unary_expr())
    return node


def parse_additive_expr():
    global current_token
    node = parse_term()
    while current_token.content() in ['+', '-']:
        child = node
        node = ASTNode()
        node.children.append(child)
        node.type = "op"
        node.content = current_token.content()
        current_token = next_token()
        node.children.append(parse_term())

    return node


def parse_shift_expr():
    global current_token
    node = parse_additive_expr()
    while current_token.content() in ['>>', '<<']:
        child = node
        node = ASTNode()
        node.children.append(child)
        node.type = "op"
        node.content = current_token.content()
        current_token = next_token()
        node.children.append(parse_additive_expr())
    return node


def parse_compare_expr():
    global current_token
    node = parse_shift_expr()
    while current_token.content() in ['>', '>=', '<', '<=']:
        child = node
        node = ASTNode()
        node.children.append(child)
        node.type = "op"
        node.content = current_token.content()
        current_token = next_token()
        node.children.append(parse_shift_expr())
    return node


def parse_equality_expr():
    global current_token
    node = parse_compare_expr()
    while current_token.content() in ['==', '!=']:
        child = node
        node = ASTNode()
        node.children.append(child)
        node.type = "op"
        node.content = current_token.content()
        current_token = next_token()
        node.children.append(parse_compare_expr())
    return node


def parse_bit_and_expr():
    global current_token
    node = parse_equality_expr()
    while current_token.content() == "&":
        child = node
        node = ASTNode()
        node.children.append(child)
        node.type = "op"
        node.content = current_token.content()
        current_token = next_token()
        node.children.append(parse_equality_expr())
    return node


def parse_bit_xor_expr():
    global current_token
    node = parse_bit_and_expr()
    while current_token.content() == "^":
        child = node
        node = ASTNode()
        node.children.append(child)
        node.type = "op"
        node.content = current_token.content()
        current_token = next_token()
        node.children.append(parse_bit_and_expr())
    return node


def parse_bit_or_expr():
    global current_token
    node = parse_bit_xor_expr()
    while current_token.content() == "|":
        child = node
        node = ASTNode()
        node.children.append(child)
        node.type = "op"
        node.content = current_token.content()
        current_token = next_token()
        node.children.append(parse_bit_xor_expr())
    return node


def parse_logical_and_expr():
    global current_token
    node = parse_bit_or_expr()
    while current_token.content() == "&&":
        child = node
        node = ASTNode()
        node.children.append(child)
        node.type = "op"
        node.content = current_token.content()
        current_token = next_token()
        node.children.append(parse_bit_or_expr())
    return node


def parse_logical_or_expr():
    global current_token
    node = parse_logical_and_expr()
    while current_token.content() == "||":
        child = node
        node = ASTNode()
        node.children.append(child)
        node.type = "op"
        node.content = current_token.content()
        current_token = next_token()
        node.children.append(parse_logical_and_expr())
    return node


def parse_conditional_expr():
    global current_token
    node = parse_logical_or_expr()
    if current_token.content() == '?':
        child = node
        node = ASTNode()
        node.type = "cond"
        node.content = '?'
        node.children.append(child)
        current_token = next_token()
        node.children.append(parse_expr())
        assert_token(current_token, ':')
        current_token = next_token()
        node.children.append(parse_conditional_expr())
    return node


def parse_expr():
    global current_token
    node = None
    if current_token.is_identifier():
        id = current_token.content()
        if id in var_map.keys() or True:
            if lookup_token(1).content() in ['=', '+=', "-=", '*=']:
                child = ASTNode("id", id)
                node = ASTNode("assign",  lookup_token(1).content())
                node.children.append(child)
                current_token = next_token(2)
                node.children.append(parse_conditional_expr())
                #offset = var_map[id]
                return node
            else:
                return parse_conditional_expr()
        else:
            fail("{} is not found".format(id))
    else:
        return parse_conditional_expr()


def parse_declaration():
    global current_token
    if token_is_type(current_token):  # declaration
        if lookup_token(1).is_identifier():
            id = lookup_token(1).content()
            if id in declared:
                fail("{} is declared".format(id))
            if lookup_token(2).content() == '=':
                var_map[id] = current_token.content()
                node = ASTNode("declaration", current_token.content())  # current_token = type
                node.children.append(ASTNode("id", id))
                current_token = next_token(3)
                node.children.append(parse_expr())
                assert_token(current_token, ';')
                current_token = next_token()
                return node
            else:
                var_map[id] = current_token.content()
                node = ASTNode("declaration", current_token.content())  # current_token = type
                node.children.append(ASTNode("id", id))
                assert_token(lookup_token(2), ';')  # idk
                current_token = next_token(3)
                return node
            declared.add(id)
            #var_map[id] = stack_index
            #stack_index -= 4
            assert_token(tokens[0], ";")
            return node


def parse_statement():
    global current_token
    global var_map, declared, stack_index
    node = ASTNode()
    if current_token.content() == "return":  # return statement
        current_token = next_token()
        node.content = "return"
        node.type = "return"
        node.children.append(parse_expr())
        assert_token(current_token, ";")
        current_token = next_token()
        return node
    elif current_token.content() == "if":  # if statement
        node.type = 'if'

        assert_token(lookup_token(1), '(')
        current_token = next_token(2)
        node.children.append(parse_expr())
        assert_token(current_token, ')')
        current_token = next_token()
        node.children.append(parse_block_item())



        if current_token.content() == "else":
            current_token = next_token()
            node.children.append(parse_block_item())

        return node
    elif current_token.content() == "do":
        node.type = "do"
        current_token = next_token()
        node.children.append(parse_block_item())
        assert_token(lookup_token(0), "while")
        assert_token(lookup_token(1), '(')
        current_token = next_token(2)
        node.children.append(parse_expr())
        assert_token(lookup_token(0), ')')
        assert_token(lookup_token(1), ';')
        current_token = next_token(2)
        return node
    elif current_token.content() == "while":
        node.type = "while"
        begin_label, end_label = get_new_label("_loop_begin"), get_new_label("_loop_end")
        assert_token(lookup_token(1), '(')
        current_token = next_token(2)
        node.children.append(parse_expr())
        assert_token(lookup_token(0), ')')
        current_token = next_token()
        node.children.append(parse_block_item())
        return node
    elif current_token.content() == "for":  # todo
        node.type = "for"
        """current_var_map, current_stack_index, current_declared = var_map.copy(), stack_index, declared.copy()
        declared = set()

        assert_token(tokens[1], '(')
        if tokens[2].content() == ';':
            tokens = tokens[3:]
        else:
            tokens = parse_block_item(tokens[2:])
        begin_label, end_label = get_new_label("_loop_begin"), get_new_label("_loop_end")
        #emit("{}:\n".format(begin_label))
        if tokens[0].content() == ';':
            pass
            #emit("\tmovl $1 %eax\n")
        else:
            tokens = parse_expr(tokens)
        assert_token(tokens[0], ';')
        tokens = tokens[1:]
        #emit("\tcmpl $0, %eax\n\tje {}\n".format(end_label))
        end_loop_tokens = []
        while tokens[0].content() != ')':
            end_loop_tokens.append(tokens[0])
            tokens = tokens[1:]
        assert_token(tokens[0], ')')
        tokens = parse_block_item(tokens[1:])
        end_loop_tokens.append(lexer.Token("dummy token", "", 0, 0))
        end_loop_tokens = parse_expr(end_loop_tokens)
        if end_loop_tokens[0].content() != "dummy token":
            assert_token(end_loop_tokens[0], ')', forced_fail=True)
        #emit("\tjmp {begin}\n{end}:\n".format(begin=begin_label, end=end_label))

        #emit("\taddl ${}, %esp\n".format((current_stack_index - stack_index)))
        var_map, stack_index, declared = current_var_map, current_stack_index, current_declared
        return tokens """
    elif current_token.content() == '{':  # block_element
        node.type = "block"
        current_var_map, current_stack_index, current_declared = var_map.copy(), stack_index, declared.copy()
        declared = set()

        current_token = next_token()
        while current_token.content() != '}':
            node.children.append(parse_block_item())
        assert_token(current_token, '}')
        current_token = next_token()

        return node
    else:
        node = parse_expr()
        current_token = next_token()
        return node


def parse_block_item():
    node = None
    if token_is_type(current_token):
        node = parse_declaration()
    else:
        node = parse_statement()
    return node


def parse_function():
    global current_token
    global assembly_code
    node = ASTNode("func")
    token_is_type(current_token)
    assert_token_identifier(lookup_token(1))
    node.children.append(ASTNode("type", lookup_token(0).content()))
    node.children.append(ASTNode("id", lookup_token(1).content()))
    assert_token(lookup_token(2), '(')
    assert_token(lookup_token(3), ')')
    assert_token(lookup_token(4), '{')
    current_token = next_token(5)
    while current_token.content() != '}':
        node.children.append(parse_block_item())
    current_token = next_token()
    return node


def parse_program():
    global tokens
    node = ASTNode("program")
    while tokens:
        node.children.append(parse_function())
    return node


def parse(token_list):
    global tokens, current_token
    tokens = token_list
    current_token = tokens[0]
    root = parse_program()
    return root.codegen()
