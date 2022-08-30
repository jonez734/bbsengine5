import ttyio5 as ttyio

def init(args=None, **kw):
    print("init")

#def access(args, op, **kw):
#    print("access.100: op=%r" % (op))
#    return False
#    if op == "run":
#        return True
#    return False

def main(args=None, **kw):
    ttyio.echo("module.main.100: trace")
    return "fooo bar"

