import ply.lex as lex
import ply.yacc as yacc

tokens = (
    "BACK",
    "DOT",
    "STAR",
    "PLUS",
    "LPAREN",
    "RPAREN",
    "LBRACK",
    "RBRACK",
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
        

t_DOT = r'\.'
t_STAR = r'\*'
t_PLUS = r'\+'
t_LPAREN= r"\("
t_RPAREN= r"\)"
t_LBRACK= r"\["
t_RBRACK= r"\]"
t_BAR = r"\|"
t_CARET = r"\^"
t_TILDE = r"\~"
t_AND = r"\&"
t_DASH = r"\-"
t_OPT  = r"\?"
t_EMPTY = r"@"
t_TICK = r"`"
t_CHAR = r"."

def t_error(t):
    print("Wut token", t);

lexer = lex.lex();

def p_RE(p):
    '''RE : union
          | simple_RE'''
    p[0] = p[1]

def p_union(p):
    '''union : RE BAR simple_RE
             | intersection
             | xor'''
    if len(p) == 4:
        p[0] = ['Union', p[1], p[3]]
    else:
        p[0] = p[1]

def p_intersection(p):
    '''intersection : RE AND simple_RE'''
    p[0] = ['Intersection', p[1], p[3]]

def p_xor(p):
    '''xor : RE CARET simple_RE'''
    p[0] = ['Xor', p[1], p[3]]
    
def p_simple_RE(p):
    '''simple_RE : concatenation
                 | basic_RE'''
    p[0] = p[1]

def p_concatenation(p):
    '''concatenation : simple_RE basic_RE'''
    p[0] = ['Concat', p[1], p[2]]

def p_basic_RE(p):
    '''basic_RE : star
                | plus
                | opt
                | not
                | reverse
                | elementary_RE'''
    p[0] = p[1]

def p_star(p):
    '''star : elementary_RE STAR'''
    p[0] = ['Star', p[1]]

def p_plus(p):
    '''plus : elementary_RE PLUS'''
    p[0] = ['Plus', p[1]]

def p_opt(p):
    '''opt : elementary_RE OPT'''
    p[0] = ['Option', p[1]]
    
def p_not(p):
    '''not : TILDE elementary_RE'''
    p[0] = ['Not', p[2]]

def p_reverse(p):
    '''reverse : TICK elementary_RE'''
    p[0] = ['Reverse', p[2]]
    
def p_elementary_RE(p):
    '''elementary_RE : group
                     | any
                     | char
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
            | EMPTY
            | BACK BACK
            | BACK DOT
            | BACK STAR
            | BACK PLUS
            | BACK LPAREN
            | BACK RPAREN
            | BACK LBRACK
            | BACK RBRACK
            | BACK BAR
            | BACK CARET
            | BACK DASH
            | BACK TILDE
            | BACK AND
            | BACK TICK
            | BACK EMPTY'''
    if len(p) == 2:
        if p[1] == '@':
            p[0] = ['Empty']
        else:
            p[0] = ['Range', (ord(p[1]), ord(p[1]))]
    else:
        p[0] = ['Range', (ord(p[2]), ord(p[2]))]

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
