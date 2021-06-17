import bbsengine5 as bbsengine
import ttyio4 as ttyio

for x in range(0, 20):
    ttyio.echo("%d: %d" % (x, bbsengine.diceroll(10)))
