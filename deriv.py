import re_parse

meta = ("\\", ".", "*", "+", "(", ")", "[", "]", "|", "^", "~", "&", "-", "?", "@")

parser = re_parse.parser.parse

colors = ['\033[95m',
          '\033[94m',
          '\033[92m',
          '\033[93m',
          '\033[91m',
          '\033[1m',
          '\033[4m']
ENDC ='\033[0m'

color = 1
hits = set()
def colorize(s):
    result = s
    global color
#    c = colors[color]
#    color = (color + 1) % len(colors)
    c = "\033[38;5;{}m".format(str(color))
    color = ((color + 3) % 255) + 1
    result = str.replace(result, "(", c  + "(" + ENDC)
    result = str.replace(result, ")", c  + ")" + ENDC)
    return result

def is_null(re):
    return isinstance(re, Null)

def is_empty(re):
    return isinstance(re, Epsilon)

def is_sigstar(re):
    return isinstance(re, SigStar)

class RE:
    def derive(self, c):
        raise NotImplementedError()

    def simplify(self):
        raise NotImplementedError()
    
    def empty(self):
        raise NotImplementedError()

    def reverse(self):
        return self

class Intersection(RE):
    def __init__(self, left, right):
        self.left = left
        self.right = right
    
    def derive(self, c):
        return Intersection(self.left.derive(c), self.right.derive(c)).simplify()

    def simplify(self):
        left = self.left.simplify()
        right = self.right.simplify()
        if is_null(left) or is_null(right):
            return Null()
        if is_sigstar(right):
            return left
        if is_sigstar(left):
            return right
        return Intersection(left, right)
    
    def empty(self):
        return self.left.empty() & self.right.empty()

    def reverse(self):
        return Intersection(self.left.reverse(), self.right.reverse())
    
    def __str__(self):
        return colorize("({})&({})").format(str(self.left),str(self.right), color)

class Union(RE):
    def __init__(self, left, right):
        self.left = left
        self.right = right
    
    def derive(self, c):
        return Union(self.left.derive(c), self.right.derive(c)).simplify()

    def simplify(self):
        left = self.left.simplify()
        right = self.right.simplify()
        if is_null(left):
            return right
        if is_null(right):
            return left
        if is_empty(left) and is_empty(right):
            return Epsilon()
        if is_empty(left) and is_empty(right.empty()):
            return right
        if is_empty(right) and is_empty(left.empty()):
            return left
        if is_sigstar(right) or is_sigstar(left):
            return SigStar()
        return Union(left, right)
    
    def empty(self):
        return self.left.empty() | self.right.empty()

    def reverse(self):
        return Union(self.left.reverse(), self.right.reverse())

    def __str__(self):
        return colorize("({})|({})").format(str(self.left), str(self.right))

class Concat(RE):
    def __init__(self, left, right):
        self.left = left
        self.right = right
    
    def derive(self, c):
        return Union(Concat(self.left.empty(), self.right.derive(c)),
                     Concat(self.left.derive(c), self.right)).simplify()

    def simplify(self):
        left = self.left.simplify()
        right = self.right.simplify()
        if is_null(left) or is_null(right):
            return Null()
        if is_empty(left):
            return right
        if is_empty(right):
            return left
        if is_sigstar(left):
            return left
        return Concat(left, right)
    
    def empty(self):
        return self.left.empty() & self.right.empty()

    def reverse(self):
        return Concat(self.right.reverse(), self.left.reverse())
    
    def __str__(self):
        return colorize("(({})({}))").format(str(self.left), str(self.right))

class Star(RE):
    def __init__(self, re):
        self.r = re

    def derive(self, c):
        r = self.r.derive(c)
        return Concat(r, Star(self.r)).simplify()

    def simplify(self):
        r = self.r.simplify()
        if isinstance(r, Star):
            return r
        if is_null(r) or is_empty(r):
            return r
        if is_sigstar(r):
            return r
        return Star(r)

    def empty(self):
        return Epsilon()

    def reverse(self):
        return Star(self.r.reverse())
    
    def __str__(self):
        return colorize("({})*").format(str(self.r))

class SigStar(RE):
    def __init__(self):
        pass

    def derive(self, c):
        return self

    def simplify(self):
        return self

    def empty(self):
        return Epsilon()

    def __str__(self):
        return ".*"

def char_to_str(o):
    import string
    result = ""
    if chr(o) in string.printable:
        if chr(o) in meta:
            result = "\\" + chr(o)
        else:
            result = chr(o)
    else:
        result = "\\" + str(oct(o))
    return result
            
class Range(RE):
    def __init__(self, r):
        self.left  = r[0]
        self.right = r[1]

    def derive(self, c):
        if self.left <= ord(c) <= self.right:
            return Epsilon()
        else:
            return Null()

    def simplify(self):
        return self
        
    def empty(self):
        return Null()

    def __str__(self):
        ch_left = char_to_str(self.left)
        ch_right = char_to_str(self.right)
        if ch_left == ch_right:
            return ch_left
        return "[{}-{}]".format(ch_left, ch_right)

class Not(RE):
    def __init__(self, r):
        self.r = r;

    def derive(self, c):
        return Not(self.r.derive(c)).simplify()

    def simplify(self):
        r = self.r.simplify()
        if is_null(r):
            return SigStar()
        if is_sigstar(r):
            return Null()
        return Not(r)
    
    def empty(self):
        return Null() if isinstance(self.r.empty(), Epsilon) else Epsilon()

    def reverse(self):
        return Not(self.r.reverse())
    
    def __str__(self):
        return colorize("~({})").format(str(self.r))
    
class Epsilon(RE):
    def __init__(self):
        pass
    
    def derive(self, c):
        return Null()

    def simplify(self):
        return self
    
    def empty(self):
        return Epsilon()

    def __and__(self, other):
        return other

    def __or__(self, other):
        return self
    def __str__(self):
        return "@"
    
class Null(RE):
    def __init__(self):
        pass
    def derive(self, c):
        return Null()
    def simplify(self):
        return self
    def empty(self):
        return Null()
    def __and__(self, other):
        return self
    def __or__ (self, other):
        return other
    def __str__(self):
        return colorize("~(.*)")
    
def build_r(expr):
    if expr[0] == 'Union':
        return Union(build_r(expr[1]), build_r(expr[2]))
    elif expr[0] == 'Intersection':
        return Intersection(build_r(expr[1]), build_r(expr[2]))
    elif expr[0] == 'Concat':
        return Concat(build_r(expr[1]), build_r(expr[2]))
    elif expr[0] == 'Star':
        return Star(build_r(expr[1]))
    elif expr[0] == 'Plus':
        sub = build_r(expr[1]);
        return Concat(sub , Star(sub))
    elif expr[0] == 'Not':
        return Not(build_r(expr[1]))
    elif expr[0] == 'Range':
        return Range(expr[1])
    elif expr[0] == 'Option':
        return Union(build_r(expr[1]), Epsilon())
    elif expr[0] == 'Empty':
        return Epsilon()
    elif expr[0] == 'Difference':
        return Intersection(build_r(expr[1]), Not(build_r(expr[2])))
    elif expr[0] == 'Xor':
        l = build_r(expr[1])
        r = build_r(expr[2])
        return Union(Intersection(Not(l), r), Intersection(l, Not(r)))
    elif expr[0] == 'Reverse':
        inner = build_r(expr[1])
        return inner.reverse()
    else:
        raise Exception("El problemo")
    
    
def build(string):
    expr = parser(string)
    return build_r(expr).simplify()

if __name__ == '__main__':
#    re = build("~([a-g]+|[l-q])")
#    inp = "qabcd"

    re = build("[a-d]|[a-e]&[c-f]")
    print(re)
    
    integer_re = "[0-9]+"
    float_re = [integer_re, integer_re + "\.", "\.[0-9]*", integer_re + "\.[0-9]+", integer_re + "\.[0-9]*"]
    exp_re = r"((e|E)(\+|\-)?[0-9]+)?"
    float_re = ["("+f + exp_re + ")" for f in float_re]
    final_re = "|".join(float_re)
    re = build("`(" + final_re + ")")
    inp = "12389712897.11238971298e-1912379182"
    inp_t = ""
    for j in inp:
        inp_t = j + inp_t
    inp = inp_t

    i = 0
    re_c = re
    last = 1
    print("Initial RE  :", str(re_c))
    print("Nullable?   :", is_empty(re_c.empty()))
    while i < len(inp):
        re_c = re_c.derive(inp[i])
        print("RE after D_{}: {}".format(inp[i], str(re_c)))
        print("Nullable?   :", is_empty(re_c.empty()))
        i += 1
    print("Final RE    :", str(re_c))
    print("Nullable?   :", is_empty(re_c.empty()))
    if isinstance(re_c.empty(), Epsilon):
        print("Accepted")
    else:
        print("Rejected")
