import sys
import ttyio4 as ttyio

done = False
buf = ""
while not done:
    ch = ttyio.getch(timeout=1.000, echoch=False, noneok=True)
    ttyio.echo("ch=%r" % (ch))
    # ttyio.echo("%r" % (ch))
    if ch == '\n':
        break
    elif ch is None:
        pass
    elif ch.isalnum() or ch.isspace():
        buf += ch
        ttyio.echo("%r" % (ch), interpret=False, flush=True, end="")  # print(ch)
    else:
        ttyio.echo("{BELL}", end="", flush=True)

ttyio.echo("{f6}"+buf+"{f6}", interpret=True, end="")

