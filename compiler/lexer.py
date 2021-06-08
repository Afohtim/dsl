class Token:
    def __init__(self, token_string, token_type, line, symbol_pos):
        self.__token_string = token_string
        self.__token_type = token_type
        self.__line = line
        self.__symbol_pos = symbol_pos

    def type(self):
        return self.__token_type

    def content(self):
        return self.__token_string

    def is_identifier(self):
        return self.__token_type == "identifier"

    def line(self):
        return self.__line

    def char(self):
        return self.__symbol_pos


separators = ['{', '}', '(', ')', ';', ',', '`']
single_char_operators = ['!', '~', '+', '-', '*', '/', '>', '<', '^', '%', '&', '|', '=', '?', ':', '.']
keywords = ["int", "double", "return", "vector", "matrix"]



def is_possible(char):
    return char.islower() or char.isupper() or char.isdigit() or char == '_'


def lex(code):
    token_list = []
    line = 1
    line_start = -1
    if code[-1] != '\n':
        code = code + '\n'
    i = 0
    while i < len(code) - 1:
        char = code[i]
        if char.isspace():
            if char == '\n':
                line += 1
                line_start = i
        elif char in separators:
            token_list.append(Token(char, "separator", line, i - line_start))
        elif char in single_char_operators:
            if char in ['~', '?', ':']:
                token_list.append(Token(char, "operator", line, i - line_start))
            elif code[i + 1] == '=':
                token_list.append(Token(char + '=', "operator", line, i - line_start))
                i += 1
            elif code[i + 1] == char and char in ['+', '-', '<', '>', '&', '|']:
                token_list.append(Token(char + char, "operator", line, i - line_start))
                i += 1
            else:
                token_list.append(Token(char, "operator", line, i - line_start))
        else:
            if is_possible(char):
                identifier = char
                j = i + 1
                while j < len(code) - 1 and (is_possible(code[j])):
                    identifier += code[j]
                    j += 1
                if identifier in keywords:
                    # add as keyword
                    token_list.append(Token(identifier, "keyword", line, i - line_start))
                else:
                    if identifier.isnumeric():
                        token_list.append(Token(identifier, "numeric", line, i - line_start))
                        if code[j] == '.':  # check if double numeral
                            identifier += code[j]
                            j += 1
                            while code[j].isnumeric():
                                identifier += code[j]
                                j += 1
                    else:
                        token_list.append(Token(identifier, "identifier", line, i - line_start))


                i = j - 1

        i += 1

    return token_list
