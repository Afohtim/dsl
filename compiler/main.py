import sys, os, re
import lexer
import language_parser

#expected form of a C program, without line breaks
source_re = r"int main\s*\(\s*\)\s*{\s*return\s+(?P<ret>[0-9]+)\s*;\s*}" 



source_file = "../code.c" #sys.argv[1]
assembly_file = os.path.splitext(source_file)[0] + ".s"

with open(source_file, 'r') as infile, open(assembly_file, 'w') as outfile:
    source = infile.read().strip()
    match = re.match(source_re, source)


    tokens = lexer.lex(source)
    token_strings = []
    for token in tokens:
        token_strings.append(token.content())
    print(token_strings)
    retval = language_parser.parse(tokens)
    print(retval)
    outfile.write(retval)
