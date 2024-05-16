import ttyio5 as ttyio
import bbsengine5 as bbsengine

foo = ["blue fish", "red fish", "salmon"]

ttyio.echo(bbsengine.oxfordcomma(foo, conjunction="or")+"{/all}")
