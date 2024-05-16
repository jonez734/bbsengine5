import sys

import ttyio5 as ttyio
import bbsengine5 as bbsengine

#ttyio.setoption("style", "ttyio")
#bbsengine.title("this is a test")

ttyio.setoption("style", "noansi")
#bbsengine.title("this is another test")
#ttyio.echo("{acs:ulcorner}{acs:hline:10}{acs:urcorner}")

buf = "test title frame"

bbsengine.title("12345")
sys.exit(0)

width = 100

w = int((width-len(buf)-4)/2)
padding = " "*(int(w))

if ttyio.getoption("style", "ttyio") == "noansi":
#    width = 100
    hline="-"*width
    llcorner="+"
    lrcorner="+"
    ulcorner="+"
    urcorner="+"
    vline="|"
    boxcolor = ""
    titlecolor = ""
    reset = "{/all}"
else:
    hline = f"{{acs:hline:{width}}}"
    llcorner = "{acs:llcorner}"
    lrcorner = "{acs:lrcorner}"
    vline = "{acs:vline}"
    urcorner = "{acs:urcorner}"
    ulcorner = "{acs:ulcorner}"
    boxcolor = "{darkgreen}" # var:engine.title.hrcolor}"
    titlecolor = "{white}{bggray}" # {var:engine.title.color}"
    reset = "{/all}"

ttyio.echo(f"{boxcolor}{ulcorner}{hline}{urcorner}", wordwrap=False)
ttyio.echo(f"{boxcolor}{vline}{reset} {titlecolor}{padding} {buf} {padding}{reset} {boxcolor}{vline}", wordwrap=False)
ttyio.echo(f"{boxcolor}{llcorner}{hline}{lrcorner}{reset}", wordwrap=False)
sys.exit(0)

#hrchar="{acs:hline}"
#llcorner="{acs:llcorner}"
#lrcorner="{acs:lrcorner}"
#ulcorner="{acs:ulcorner}"
#urcorner="{acs:urcorner}"
#vline="{acs:vline}"

#width = 100
#ttyio.echo(f"{{var:engine.title.hrcolor}}{ulcorner}{{acs:hline:{width}}}{urcorner}", wordwrap=False)
#ttyio.echo("{var:engine.title.hrcolor}{acs:vline}{/all}{var:engine.title.color}%s{/all}{var:engine.title.hrcolor}{acs:vline}{/all}" % (buf), wordwrap=False)
# ttyio.echo("{f6}{acs:vline}{/all}%s%s{/all}%s{acs:vline}{/all}" % (titlecolor, i.center(width), hrcolor), end="")
#ttyio.echo("{var:engine.title.hrcolor}%s{acs:hline:%s}%s" % (llcorner, width, lrcorner), wordwrap=False)
