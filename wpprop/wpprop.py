from typing import Any, List, NamedTuple

class Token(NamedTuple):
    type: str
    value: str

# @see https://docs.python.org/3/library/re.html#writing-a-tokenizer
def __tokenizewpprop(buf:str):
    buf = buf.replace("\n", " ")
    token_specification = [
        ("OPEN",  	r'\[\['), 
        ("CLOSE", 	r'\]\]'),
        ("OPENCOMMAND", r'\[[^\]]+\]'),
        ("CLOSECOMMAND",r'\[/[^\]]+\]'),
        ('MISMATCH',   	r'.')            # Any other character
    ]
    tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
    for mo in re.finditer(tok_regex, buf):
        kind = mo.lastgroup
        # print("kind=%r mo.groups()=%r" % (kind, mo.groups()))
        value = mo.group()
          # print("whitespace. value=%r" % (value))
        elif kind == "COMMAND":
            
            pass
        elif kind == "OPEN":
          value = "["
        elif kind == "CLOSE":
          value = "]"
        yield Token(kind, value)
