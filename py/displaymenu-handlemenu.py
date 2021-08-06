def displaymenu(menuitems:list, title:str=None):
  terminalwidth = ttyio.getterminalwidth()
  w = terminalwidth - 7

  maxlen = 0
  for m in menuitems:
        l = len(m["label"])
        if l > maxlen:
            maxlen = l

  firstline = False
  ttyio.echo("{f6} {var:menu.cursorcolor}{var:menu.backgroundcolor}%s{/all}" % (" "*(terminalwidth-2)), wordwrap=False)
  if title is None or title == "":
    ttyio.echo(" {var:menu.cursorcolor}{var:menu.backgroundcolor} {var:menu.boxcharcolor}{acs:ulcorner}{acs:hline:%d}{var:menu.boxcharcolor}{acs:urcorner}{var:menu.backgroundcolor}  {/all}" % (terminalwidth - 7), wordwrap=False)
  else:
    ttyio.echo(" {var:menu.cursorcolor}{var:menu.backgroundcolor} {var:menu.boxcharcolor}{acs:ulcorner}{acs:hline:%d}{acs:urcorner}{var:menu.backgroundcolor}  {/all}" % (terminalwidth - 7), wordwrap=False)
    ttyio.echo(" {var:menu.cursorcolor}{var:menu.backgroundcolor} {var:menu.boxcharcolor}{acs:vline}{var:menu.titlecolor}%s{var:menu.boxcharcolor}{acs:vline}{var:menu.shadowbackgroundcolor} {var:menu.backgroundcolor} {/all}" % (title.center(terminalwidth-7)), wordwrap=False)
    ttyio.echo(" {var:menu.cursorcolor}{var:menu.backgroundcolor} {var:menu.boxcharcolor}{acs:ltee}{acs:hline:%d}{acs:rtee}{var:menu.shadowbackgroundcolor} {var:menu.backgroundcolor} {/all}" % (terminalwidth - 7), wordwrap=False)

  ch = ord("A")
  options = ""
  for m in menuitems:
    if "result" in m:
      result = m["result"]
      if type(result) == tuple:
        resultbuf = ""
        r, s = result
        if r is True:
          resultbuf = s
        result = "%s" % (resultbuf)
      else:
        result = "(%r)" % (result)
    else:
      result = ""
    
    requires = m["requires"] if "requires" in m else ()

    if len(requires) == 0:
      requiresbuf = ""
    else:
      requiresbuf = "(requires: %s)" % (ttyio.readablelist(requires))
    name = m["name"] if "name" in m else None
    if resolverequires(args, menuitems, name) is True:
      buf = "[%s] %s %s %s" % (chr(ch), m["label"], result, requiresbuf)
      ttyio.echo(" {black}{bgblue} {lightblue}{acs:vline}{bgcyan}{black} %s {bgblue}{lightblue}{acs:vline}{bgblack} {bgblue} {/all}" % (buf.ljust(terminalwidth-9)), wordwrap=False)
    else:
      buf = "[%s] %s %s %s" % (chr(ch), m["label"], result, requiresbuf)
      ttyio.echo(" {black}{bgblue} {lightblue}{acs:vline}{bgcyan}{black} {bggray}{white}%s {bgblue}{lightblue}{acs:vline}{bgblack} {bgblue} {/all}" % (buf.ljust(terminalwidth-9)), wordwrap=False)

    buf = "[%s] %s" % (chr(ch), m["label"].ljust(maxlen))

    if "description" in m:
      buf += " %s" % (m["description"])
    if firstline is True:
        ttyio.echo(" {var:menu.cursorcolor}{var:menu.backgroundcolor} {var:menu.itemcolor} %s {var:menu.backgroundcolor}  {/all}" % (buf.ljust(terminalwidth-7)), wordwrap=False)
        firstline = False
    else:
        ttyio.echo(" {var:menu.cursorcolor}{var:menu.backgroundcolor} {var:menu.boxcharcolor}{acs:vline}{var:menu.itemcolor}%s {var:menu.boxcharcolor}{acs:vline}{var:menu.shadowbackgroundcolor} {var:menu.backgroundcolor} {/all}" % (buf.ljust(terminalwidth-8)), wordwrap=False)
    options += chr(ch)
    ch += 1

  # ttyio.echo(" {white}{bggray} {black}{acs:vline}%s {black}{acs:vline}{bgblack} {bggray} {/all}" % (" "*(terminalwidth-8)), wordwrap=False)

  ttyio.echo(" {var:menu.backgroundcolor} {var:menu.boxcharcolor}{acs:vline}{var:menu.itemcolor}%s {var:menu.boxcharcolor}{acs:vline}{var:menu.shadowbackgroundcolor} {var:menu.backgroundcolor} {/all}" % ("[Q] quit".ljust(terminalwidth-8)), wordwrap=False)
  options += "Q"

  ttyio.echo(" {var:menu.cursorcolor}{var:menu.backgroundcolor} {var:menu.boxcharcolor}{acs:llcorner}{acs:hline:%d}{acs:lrcorner}{var:menu.shadowbackgroundcolor} {var:menu.backgroundcolor} {/all}" % (terminalwidth-7), wordwrap=False)

  ttyio.echo(" {var:menu.cursorcolor}{var:menu.backgroundcolor}  {var:menu.shadowbackgroundcolor}%s {var:menu.backgroundcolor} {/all}" % (" "*(terminalwidth-6)), wordwrap=False)
  ttyio.echo(" {var:menu.backgroundcolor}%s{/all}" % (" "*(terminalwidth-2)), wordwrap=False)
  return

def handlemenu(prompt="menu:", menu=[], default="A"):
  ttyio.echo("{f6} %s{decsc}{cha}{cursorright:4}{cursorup:%d}{var:menu.cursorcolor}A{cursorleft}" % (prompt, 5+len(menu)), end="", flush=True)

  res = None
  pos = 0
  done = False
  while not done:
    ch = ttyio.getch(noneok=False)
    if ch is None:
      time.sleep(0.125)
      continue
    ch = ch.upper()
    oldpos = pos
    if ch == "Q":
      ttyio.echo("{decrc}{var:menu.inputcolor}Q: Quit{/all}")
      break
    elif ch == "\004":
      raise EOFError
    elif ch == "KEY_DOWN":
      if pos < len(menu):
        # ttyio.echo("{black}{bggray}%s{cursorleft}{cursordown}" % (chr(ord('A')+pos)), end="", flush=True)
        # ttyio.echo("{var:menu.cursorcolor}{var:menu.boxcolor}%s{cursorleft}{cursordown}" % (chr(ord('A')+pos)), end="", flush=True)
        ttyio.echo("{var:menu.cursorcolor}%s{cursorleft}{cursordown}" % (chr(ord('A')+pos)), end="", flush=True)
        pos += 1
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
      # ttyio.echo("pos=%d len=%d" % (pos, len(menu)))
      return ("select", pos)
    elif ch == "KEY_HOME":
      if pos > 0:
        ttyio.echo("{cursorup:%d}" % (pos-1), end="", flush=True)
        pos = 0
    elif ch == "KEY_END":
      ttyio.echo("{cursordown:%d}" % (len(menu)-pos), end="", flush=True)
      pos = len(menu)+1
    elif ch == "KEY_LEFT" or ch == "KEY_RIGHT":
      ttyio.echo("{bell}", flush=True, end="")
    elif ch == "Q":
      return ("quit", None)
    elif ch == "?" or ch == "KEY_F1":
      return ("help", pos)
    else:
      if len(ch) > 1:
        ttyio.echo("{bell}", end="", flush=True)
        continue
      i = ord(ch) - ord('A')
      if i > len(menu)-1:
        ttyio.echo("{bell}", end="", flush=True)
        continue
      return ("select", i)
  return None
