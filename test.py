import re_parse

print(re_parse.parser.parse("x"))
print(re_parse.parser.parse("[x-y]&[y-z]"))
print(re_parse.parser.parse("~ab*"))
print(re_parse.parser.parse("[a-c]|[x-y]&[y-z]"))
