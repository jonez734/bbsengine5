import ttyio4 as ttyio
import bbsengine5 as bbsengine

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

def alpha(args, **kwargs):
  ttyio.echo("{red}alpha{/all}")
#  ttyio.echo("alpha.120: kwargs=%r" % (kwargs), interpret=False)
  if "menuitem" in kwargs:
    menuitem = kwargs["menuitem"]
    menuitem["description"] = "yes!"
  else:
    ttyio.echo("alpha.100: no menuitem")
  return

def bravo(args, **kwargs):
  ttyio.echo("bravo!")
  if "menuitem" in kwargs:
    menuitem = kwargs["menuitem"]
    menuitem["description"] = "yes!"
  else:
    ttyio.echo("bravo.100: no menuitem")

  return

def main():
  alphahelp = """Lorem ipsum dolor sit amet, consectetur adipiscing elit. Fusce ultricies diam metus, a interdum nisl dictum a. Praesent et magna finibus, elementum erat vel, lacinia diam. Phasellus a fermentum risus, ullamcorper semper purus. Nunc pellentesque lorem quis egestas consequat. Ut varius venenatis odio, a eleifend turpis euismod nec. Aliquam erat volutpat. Suspendisse vestibulum augue enim, ac facilisis elit tristique quis. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Morbi condimentum eros vitae feugiat pellentesque. Ut sed placerat est, eget pharetra dolor. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Nulla eget sagittis leo. Nullam a maximus lectus. Sed nec vulputate libero. In eu erat a purus ultricies feugiat eget sed nulla.
{f6}{f6}Integer neque lorem, eleifend in magna sit amet, cursus finibus risus. Duis rutrum est vehicula lorem vulputate, vitae consequat felis ultricies. In pretium felis vitae metus convallis auctor. Aenean sollicitudin porttitor ultrices. In hac habitasse platea dictumst. Sed maximus semper velit non sodales. Phasellus laoreet enim vitae laoreet cursus. Duis in consequat mi, vel interdum nisi. Aliquam blandit egestas sapien, nec aliquet nibh semper ut. Aliquam porttitor nulla suscipit, tempus dui sed, dignissim eros.
"""

  menu = [
      { "label": "alpha",   "callback": alpha, "description":"foo bar baz", "help": alphahelp},
      { "label": "bravo",   "callback": bravo },
      { "label": "charlie", "callback": "charlie" },
      { "label": "delta",   "callback": "delta"},
      { "label": "echo",    "callback": "echo"},
      { "label": "foxtrot", "callback": "foxtrot"},
      { "label": "golf",    "callback": "golf", "description":"another description"}
  ]
  # ttyio.setvariable("menu.boxcharcolor", "{black}")
  # ttyio.setvariable("menu.backgroundcolor", "{bggray}")
  # ttyio.setvariable("menu.shadowbackgroundcolor", "{bgdarkgray}")
  ttyio.setvariable("menu.boxcharcolor", "{bglightgray}{white}")
  ttyio.setvariable("menu.backgroundcolor", "{bggray}")
  ttyio.setvariable("menu.shadowbackgroundcolor", "{bgdarkgray}")
  ttyio.setvariable("menu.cursorcolor", "{bglightgray}{blue}")
  ttyio.setvariable("menu.boxcolor", "{bgblue}{green}")
  ttyio.setvariable("menu.itemcolor", "{blue}{bglightgray}")
  ttyio.setvariable("menu.titlecolor", "{black}{bglightgray}")
  ttyio.setvariable("menu.promptcolor", "{white}{bgblack}")
  ttyio.setvariable("menu.inputcolor", "{white}{bgblack}")

  done = False
  while not done:
    displaymenu(menu, title="testhandlemenu")
    res = handlemenu("{var:menu.promptcolor}prompt: {var:menu.inputcolor}", menu)
    if res is None:
      return
    elif type(res) == tuple:
      (op, i) = res
    else:
      ttyio.echo("invalid return type from handle menu %r!" % (type(res)), level="error")
      break

#    ttyio.echo("handlemenu.100: i=%r op=%r" % (i, op))

    if i < len(menu):
      if op == "select":
        ttyio.echo("{decrc}{var:menu.inputcolor}%s: %s{/all}" % (chr(ord('A')+i), menu[i]["label"]))
#        ttyio.echo("menu[i]=%r" % (menu[i]), interpret=False, level="debug", interpret=False)
        bbsengine.runcallback(None, menu[i]["callback"], menuitem=menu[i])
        continue
      elif op == "help":
        m = menu[i]
        ttyio.echo("{decrc}display help for %s" % (m["label"]))
        if "help" in m:
          ttyio.echo(m["help"]+"{f6:2}")
        else:
          ttyio.echo("{f6}no help defined for this option{f6}")
        continue
    else:
      ttyio.echo("{decrc}Q: Quit{/all}foo")
      done = True
      break
  return

#  ttyio.echo(repr(menu), interpret=False)

if __name__ == "__main__":
  ttyio.echo("testhandlemenu.py has been replace by handlemenu.py")
  try:
    main()
  except KeyboardInterrupt:
    ttyio.echo("{decrc}INTR")
  except EOFError:
    ttyio.echo("{decrc}EOF")
  finally:
    ttyio.echo("{/all}")
