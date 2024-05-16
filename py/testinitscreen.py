import bbsengine5 as bbsengine
import ttyio5 as ttyio

bbsengine.initscreen()
bbsengine.setarea("bottom bar")
for x in range(0, 50):
    ttyio.echo("some intro stuff")

