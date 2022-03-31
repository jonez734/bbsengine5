import bbsengine5 as bbsengine
import ttyio5 as ttyio

ttyio.echo("%r" % (bbsengine.diceroll(10, 10, mode="median")))
# for x in range(0, 20):
#    ttyio.echo("%d: %d" % (x, bbsengine.diceroll(10)))
