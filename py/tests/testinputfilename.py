import bbsengine5 as bbsengine
import ttyio5 as ttyio
from argparse import Namespace

class completeFilename(object):
    pass

def inputfilename(args, prompt="filename: ", "", noneok=True):
    pass

#res = ttyio.inputstring("prompt: ", "default")
#ttyio.echo("res=%r" % (res))
res = inputfilename(Namespace(), "filename: ", "~jam/projects/bbsengine5/README.md", noneok=True)
ttyio.echo("res=%r" % (res))

