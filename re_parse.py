import ply.lex as lex
import ply.yacc as yacc

# RE : union
#    | xor
#    | inter
#
# union : RE '|' inter
#
# xor : RE '^' inter
#
# inter : intersection
#       | difference
#       | concatenation
#
# intersection : inter '&' concatenation
#
# difference : inter '-' concatenation
#
# concatenation : concatenation quant
#               | quant
#
# neg_rev : negation
#         | reversal
#         | atom
#
# negation : '~' neg_rev
#
# reversal : '`' neg_rev
#
# quant : star
#       | plus
#       | neg_rev
#       | range_rep
#
# star : quant '*'
#
# plus : quant '+'
#
# opt : quant '?'
#
# range_rep : quant '(' INT ')'
#           | quant '(' INT ',)'
#           | quant '(,' INT ')'
#           | quant '(' INT ',' INT ')'
#
# INT : [0-9] INT
#     | [0-9]
#
# atom : group
#      | any
#      | char
#      | set
#
# group : '(' RE ')'
#
# any : '.'
#
# set : positive_set
#     | negative_set
#
# positive_set : '[' set_items ']'
#
# negative_set : '[^' set_items ']'
#
# set_items : range
#           | char
#
# range : char '-' char
#
# char : .

tokens = (
    "OCTAL",
    "BACK",
    "DOT",
    "STAR",
    "PLUS",
    "LPAREN",
    "RPAREN",
    "LBRACK",
    "RBRACK",
    "LBRACE",
    "RBRACE",
    "COMMA",
    "BAR",
    "CARET",
    "DASH",
    "TILDE",
    "AND",
    "OPT",
    "EMPTY",
    "TICK",
    "CHAR",
)

def t_OCTAL(t):
    r"\\0o[0-3][0-7]{0,2}"
    result = 0
    for c in t.value[3:]:
        result *= 8
        result += int(c)
    t.value = chr(result)
    return t

def t_BACK(t):
    r'\\'
    # If we find an escape character, read the next character
    # and return it as a CHAR
    next = lexer.token()
    if next is not None:
        next.type = "CHAR"
        return next
    else:
        raise Exception("End of stream after escape token")
        

t_DOT    = r'\.'
t_STAR   = r'\*'
t_PLUS   = r'\+'
t_LPAREN = r"\("
t_RPAREN = r"\)"
t_LBRACK = r"\["
t_RBRACK = r"\]"
t_LBRACE = r"\{"
t_RBRACE = r"\}"
t_COMMA  = r" ,"
t_BAR    = r"\|"
t_CARET  = r"\^"
t_TILDE  = r"\~"
t_AND    = r"\&"
t_DASH   = r"\-"
t_OPT    = r"\?"
t_EMPTY  = r" @" # Space is for higher matching precedence than CHAR
t_TICK   = r" `" # Space is for higher matching precedence than CHAR
t_CHAR   = r"."

def t_error(t):
    print("Wut token", t);

lexer = lex.lex();

precedence = (
    ('left', 'TILDE', 'TICK'),
    ('right', 'OPT', 'STAR', 'PLUS'),
    ('left', 'AND', 'DASH'),
    ('left', 'BAR', 'CARET'),
    )

def p_RE(p):
    '''RE : union
          | xor
          | inter
          | BACK''' # BACK never appears. yacc needs to use this token.
    p[0] = p[1]

def p_union(p):
    '''union : RE BAR inter'''
    p[0] = ['Union', p[1], p[3]]

def p_xor(p):
    '''xor : RE CARET inter'''
    p[0] = ['xor', p[1], p[3]]

def p_inter(p):
    '''inter : intersection
             | difference
             | concatenation'''
    p[0] = p[1]
                        
def p_intersection(p):
    '''intersection :  inter AND concatenation'''
    p[0] = ['Intersection', p[1], p[3]]

def p_difference(p):
    '''difference :  inter DASH concatenation'''
    p[0] = ['Difference', p[1], p[3]]

def p_concatenation(p):
    '''concatenation : concatenation quant
                     | quant'''
    if len(p) == 3:
        p[0] = ['Concat', p[1], p[2]]
    else:
        p[0] = p[1]

def p_neg_rev(p):
    '''neg_rev : TILDE neg_rev
               | TICK neg_rev
               | atom'''
    if len(p) == 3:
        if p[1] == "`":
            p[0] = ['Reverse', p[2]]
        else:
            p[0] = ['Not', p[2]]
    else:
        p[0] = p[1]

def p_quant(p):
        '''quant : star
                 | plus
                 | opt
                 | neg_rev
                 | range_rep'''
        p[0] = p[1]
        
def p_star(p):
    '''star : quant STAR'''
    p[0] = ['Repetition', '0', '-1', p[1]]

def p_plus(p):
    '''plus : quant PLUS'''
    p[0] = ['Repetition', '1', '-1', p[1]]

def p_opt(p):
    '''opt : quant OPT'''
    p[0] = ['Repetition', '0', '1', p[1]]

def p_range_rep(p):
    '''range_rep : quant LBRACE INT RBRACE
                 | quant LBRACE INT COMMA RBRACE
                 | quant LBRACE COMMA INT RBRACE
                 | quant LBRACE INT COMMA INT RBRACE'''
    if len(p) == 5:
        p[0] = ['Repetition', p[3], p[3], p[1]]
    elif len(p) == 6:
        if p[3] == ",":
            p[0] = ['Repetition', '0', p[4], p[1]]
        else:
            p[0] = ['Repetition', p[3], '-1', p[1]]
    else:
        p[0] = ['Repetition', p[3], p[5], p[1]]
    
def p_INT(p):
    '''INT : CHAR INT
           | CHAR'''
    if not (ord('0') <= ord(p[1]) <= ord('9')):
        raise Exception("Unexpected character in range repetition: " + p[1])
    if len(p) == 2: # CHAR case
        p[0] = p[1]
    else:
        p[0] = p[1] + p[2]
        
def p_atom(p):
    '''atom : group
            | any
            | char
            | empty
            | set'''
    p[0] = p[1]

def p_group(p):
    '''group : LPAREN RE RPAREN'''
    p[0] = p[2]

def p_any(p):
    '''any : DOT'''
    p[0] = ['Range', (0, 255)]

def p_char(p):
    '''char : CHAR
            | OCTAL'''
    p[0] = ['Range', (ord(p[1]), ord(p[1]))]

def p_empty(p):
    '''empty : EMPTY'''
    p[0] = ['Empty']
    
def p_set(p):
    '''set : positive_set
           | negative_set'''
    p[0] = p[1]

def p_positive_set(p):
    '''positive_set : LBRACK set_items RBRACK'''
    p[0] = p[2]

def p_negative_set(p):
    '''negative_set : LBRACK CARET set_items RBRACK'''
    p[0] = ['Not', p[3]]

def p_set_items(p):
    '''set_items : set_item
                 | set_item set_items'''
    if len(p) == 3:
        p[0] = ['Union', p[1], p[2]]
    else:
        p[0] = p[1]

def p_set_item(p):
    '''set_item : range
                | char'''
    p[0] = p[1]

def p_range(p):
    '''range : char DASH char'''
    p[0] = ['Range', (p[1][1][0], p[3][1][0])]

def p_error(p):
    print("Parse wut", p);
    
parser = yacc.yacc()
