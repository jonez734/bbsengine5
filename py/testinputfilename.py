import bbsengine5 as bbsengine
import ttyio4 as ttyio
from argparse import Namespace

#res = ttyio.inputstring("prompt: ", "default")
#ttyio.echo("res=%r" % (res))
res = bbsengine.inputfilename(Namespace(), "filename: ", "foo", noneok=True)
ttyio.echo("res=%r" % (res))

