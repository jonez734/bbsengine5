#!/usr/bin/env python

import time
import locale
import argparse

import ttyio5 as ttyio
import bbsengine5 as bbsengine

def init(args=None):
    ttyio.setvariable("promptcolor", "{/bgcolor}{lightgray}")
    ttyio.setvariable("inputcolor", "{/bgcolor}{green}")

    ttyio.setvariable("optioncolor", "{white}{bggray}")
    ttyio.setvariable("currentoptioncolor", "{bgwhite}{gray}")
    return

def buildargs(args=None):
    parser = argparse.ArgumentParser("testfiledisplay")
    parser.add_argument("--verbose", action="store_true", dest="verbose")
    parser.add_argument("--debug", action="store_true", dest="debug")
    
    return parser

def main(args=None):
    bbsengine.setarea("test setarea()")
    bbsengine.filedisplay(None, "s.explain-1.txt")
    return

if __name__ == "__main__":
    locale.setlocale(locale.LC_ALL, "")
    time.tzset()

    parser = buildargs()
    args = parser.parse_args()

    ttyio.echo("{f6:3}{cursorup:3}") # curpos:%d,0}" % (ttyio.getterminalheight()-3))
    bbsengine.initscreen(bottommargin=1)

    init(args)

    try:
        main(args)
    except KeyboardInterrupt:
        ttyio.echo("{/all}{bold}INTR{bold}")
    except EOFError:
        ttyio.echo("{/all}{bold}EOF{/bold}")
    finally:
        ttyio.echo("{decsc}{curpos:%d,0}{el}{decrc}{reset}{/all}" % (ttyio.getterminalheight()))
