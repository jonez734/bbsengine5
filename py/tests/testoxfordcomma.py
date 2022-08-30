import bbsengine5 as bbsengine
import ttyio4 as ttyio

sigs = []
res = bbsengine.oxfordcomma(sigs, sepcolor="{green}", itemcolor="{yellow}")

ttyio.echo("res=%r" % (res), interpret=False)
