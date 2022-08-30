import time
import locale
import argparse

import ttyio5 as ttyio
import bbsengine5 as bbsengine

def init(args=None):
  ttyio.setvariable("menuoption", "{white}{bggray}")
  ttyio.setvariable("menudesc", "{/bgcolor}{white}")
  ttyio.setvariable("menuvalue", "{/bgcolor}{green}")
#  ttyio.setvariable("promptcolor", "{/bgcolor}{lightgray}")
#  ttyio.setvariable("inputcolor", "{/bgcolor}{green}")
  return

def buildargs(args=None):
    parser = argparse.ArgumentParser("testchecksubmodule")
    parser.add_argument("--verbose", action="store_true", dest="verbose")
    parser.add_argument("--debug", action="store_true", dest="debug")

    defaults = {"databasename": "zoidweb5", "databasehost":"localhost", "databaseuser": None, "databaseport":15433, "databasepassword":None} # port=5432
    bbsengine.buildargdatabasegroup(parser, defaults)

    return parser

def main(args=None):
    x = bbsengine.runmodule(args, "module", op="run", buildargs=False)
    print(x)

if __name__ == "__main__":
    locale.setlocale(locale.LC_ALL, "")
    time.tzset()

    parser = buildargs()
    args = parser.parse_args()

    ttyio.echo("{f6:3}{cursorup:3}")
    bbsengine.initscreen(bottommargin=1)

    init(args)

    try:
        main(args)
    except KeyboardInterrupt:
        ttyio.echo("{/all}{bold}INTR{bold}")
    except EOFError:
        ttyio.echo("{/all}{bold}EOF{/bold}")
    finally:
        ttyio.echo("{decsc}{curpos:%d,0}{eraseline}{decrc}{reset}{/all}" % (ttyio.getterminalheight()))
