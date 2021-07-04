import ttyio4 as ttyio
import bbsengine5 as bbsengine

def clocks(args, command=None):
  ttyio.echo("{red}clocks{/all}")

def displaymenu(menuitems:list, title:str=None):
  terminalwidth = ttyio.getterminalwidth()
  # ttyio.echo("terminalwidth=%r" % (terminalwidth), level="debug")

  maxlen = 0
  for m in menuitems:
        l = len(m["label"])
        if l > maxlen:
            maxlen = l

  firstline = False
  ttyio.echo(" {white}{bggray}%s{/all}" % (" "*(terminalwidth-2)), wordwrap=False)
  if title is None or title == "":
    ttyio.echo(" {white}{bggray} {black}{acs:ulcorner}{acs:hline:%d}{black}{acs:urcorner}{bggray}  {/all}" % (terminalwidth - 7))
  else:
    ttyio.echo(" {white}{bggray} {black}{acs:ulcorner}{acs:hline:%d}{acs:urcorner}{bggray}  {/all}" % (terminalwidth - 7))
    ttyio.echo(" {white}{bggray} {black}{acs:vline}{black}%s{black[C}{acs:vline}{bgblack} {bggray} {/all}" % (title.center(terminalwidth-7)))
    ttyio.echo(" {white}{bggray} {black}{acs:ltee}{acs:hline:%d}{acs:rtee}{bgblack} {bggray} {/all}" % (terminalwidth - 7))
  ch = ord("A")
  options = ""
  for m in menuitems:
      buf = "[%s] %s" % (chr(ch), m["label"])
      if firstline is True:
          ttyio.echo(" {white}{bggray} {black}{black} %s {bggray}  {/all}" % (buf.ljust(terminalwidth-7)), wordwrap=False)
          firstline = False
      else:
          ttyio.echo(" {white}{bggray} {black}{acs:vline}{black}{black}%s {black}{acs:vline}{bgblack} {bggray} {/all}" % (buf.ljust(terminalwidth-8)), wordwrap=False)
      options += chr(ch)
      ch += 1

  # ttyio.echo(" {white}{bggray} {black}{acs:vline}%s {black}{acs:vline}{bgblack} {bggray} {/all}" % (" "*(terminalwidth-8)), wordwrap=False)

  ttyio.echo(" {bggray} {black}{acs:vline}{black}%s {black}{acs:vline}{bgblack} {bggray} {/all}" % ("[Q] quit".ljust(terminalwidth-8)), wordwrap=False)
  options += "Q"

  ttyio.echo(" {white}{bggray} {black}{acs:llcorner}{acs:hline:%d}{acs:lrcorner}{bgblack} {bggray} {/all}" % (terminalwidth-7))

  ttyio.echo(" {white}{bggray}  {bgblack}%s {bggray} {/all}" % (" "*(terminalwidth-6)), wordwrap=False)
  ttyio.echo(" {bggray}%s{/all}" % (" "*(terminalwidth-2)), wordwrap=False)
  return

def main():
  menu = [
      { "label": "clocks", "callback": clocks},
      { "label": "storage", "callback": "storage" },
      { "label": "modem", "callback": "modem" },
      { "label": "foo", "callback": "foo"},
      { "label": "bar", "callback": "bar"},
      { "label": "baz", "callback": "baz"},
      { "label": "bing", "callback": "bing"}
  ]

  ttyio.echo(repr(menu), interpret=False)

  displaymenu(menu, title="")
  ttyio.echo("{CURSORUP:%d}{CURSORRIGHT:4}A{CURSORLEFT}" % (4+len(menu)), end="", flush=True)

  res = None
  pos = 0
  done = False
  while not done:
    ch = ttyio.getch(noneok=False)
    oldpos = pos
#    ch = ttyio.inputchar("setupimagebbs [ABCQ]: ", "ABCQ", "Q", noneok=True)
    if ch == "Q":
      ttyio.echo("Q: Quit")
      break
    elif ch == "KEY_DOWN":
      if pos < len(menu):
        ttyio.echo("{bggray}{red}%s{/all}" % (chr(ord('A')+pos)), end="", flush=True)
        ttyio.echo("{cursorleft}{cursordown}", end="", flush=True)
        pos += 1
        ttyio.echo("{bgwhite}{lightblue}%s{cursorleft}{/all}" % (chr(ord('A')+pos)), end="", flush=True)
      else:
        ttyio.echo("{cursorup:%d}" % (pos), end="", flush=True)
        pos = 0
    elif ch == "KEY_UP":
      if pos > 0:
        ttyio.echo("{cursorup}", end="", flush=True)
        pos -= 1
      else:
        ttyio.echo("{cursordown:%d}" % (len(menu)), end="", flush=True)
        pos = len(menu)
    elif ch == "\n":
      res = ord('A') + pos
      break
    else:
      ch = ch.upper()
      i = ord(ch.upper()) - ord("A")
      ttyio.echo("i=%d chr=%s" % (i, chr(i)))
      ttyio.echo("%s: %s" % (ch, menu[i]["label"]))
      bbsengine.runcallback(None, menu[i]["callback"])
      break
  ttyio.echo("res=%r" % (chr(res)))
  return

if __name__ == "__main__":
  main()
