#!/usr/bin/env python3

import ttyio5 as ttyio
import bbsengine5 as bbsengine
import argparse

def buildargs(args=None):
    parser = argparse.ArgumentParser("empyre")
    parser.add_argument("--verbose", action="store_true", dest="verbose")
    parser.add_argument("--debug", action="store_true", dest="debug")

    defaults = {"databasename": "zoidweb5", "databasehost":"localhost", "databaseuser": None, "databaseport":5432, "databasepassword":None}
    bbsengine.buildargdatabasegroup(parser, defaults)

    return parser
    
def main(args):
    dbh = bbsengine.databaseconnect(args)
    dbh.close()
    dbh = bbsengine.databaseconnect(args)
    cur = dbh.cursor()
    cur.execute("select 1 from engine.member limit 1")

if __name__ == "__main__":
    parser = buildargs()
    args = parser.parse_args()

    ttyio.echo("{f6:5}{curpos:%d,0}" % (ttyio.getterminalheight()-5))
    bbsengine.initscreen(bottommargin=1)

    try:
        main(args)
    except KeyboardInterrupt:
        ttyio.echo("{/all}{bold}INTR{bold}")
    except EOFError:
        ttyio.echo("{/all}{bold}EOF{/bold}")
    finally:
        ttyio.echo("testdbh.200: areastack=%r" % (bbsengine.areastack), level="debug")
#        ttyio.inputboolean("continue? [Yn]: ", "Y")
        ttyio.echo("{decsc}{curpos:%d,0}{el}{decrc}{reset}{/all}" % (ttyio.getterminalheight()))
