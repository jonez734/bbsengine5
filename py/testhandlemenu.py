import ttyio4 as ttyio
import bbsengine5 as bbsengine

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

def displaymenu(menuitems:list, title:str=None):
  terminalwidth = ttyio.getterminalwidth()

  maxlen = 0
  for m in menuitems:
        l = len(m["label"])
        if l > maxlen:
            maxlen = l

  firstline = False
  ttyio.echo(" {white}{bggray}%s{/all}" % (" "*(terminalwidth-2)))
  if title is None or title == "":
    ttyio.echo(" {white}{bggray} {black}{acs:ulcorner}{acs:hline:%d}{black}{acs:urcorner}{bggray}  {/all}" % (terminalwidth - 7))
  else:
    ttyio.echo(" {white}{bggray} {black}{acs:ulcorner}{acs:hline:%d}{acs:urcorner}{bggray}  {/all}" % (terminalwidth - 7))
    ttyio.echo(" {white}{bggray} {black}{acs:vline}{black}%s{black[C}{acs:vline}{bgdarkgray} {bggray} {/all}" % (title.center(terminalwidth-7)))
    ttyio.echo(" {white}{bggray} {black}{acs:ltee}{acs:hline:%d}{acs:rtee}{bgdarkgray} {bggray} {/all}" % (terminalwidth - 7))

  ch = ord("A")
  options = ""
  for m in menuitems:
      buf = "[%s] %s" % (chr(ch), m["label"].ljust(maxlen))
      if "description" in m:
        buf += " %s" % (m["description"])
      if firstline is True:
          ttyio.echo(" {white}{bggray} {black}{black} %s {bggray}  {/all}" % (buf.ljust(terminalwidth-7)), wordwrap=False)
          firstline = False
      else:
          ttyio.echo(" {white}{bggray} {black}{acs:vline}{black}{black}%s {black}{acs:vline}{bgdarkgray} {bggray} {/all}" % (buf.ljust(terminalwidth-8)), wordwrap=False)
      options += chr(ch)
      ch += 1

  # ttyio.echo(" {white}{bggray} {black}{acs:vline}%s {black}{acs:vline}{bgblack} {bggray} {/all}" % (" "*(terminalwidth-8)), wordwrap=False)

  ttyio.echo(" {bggray} {black}{acs:vline}{black}%s {black}{acs:vline}{bgdarkgray} {bggray} {/all}" % ("[Q] quit".ljust(terminalwidth-8)), wordwrap=False)
  options += "Q"

  ttyio.echo(" {white}{bggray} {black}{acs:llcorner}{acs:hline:%d}{acs:lrcorner}{bgdarkgray} {bggray} {/all}" % (terminalwidth-7))

  ttyio.echo(" {white}{bggray}  {bgdarkgray}%s {bggray} {/all}" % (" "*(terminalwidth-6)), wordwrap=False)
  ttyio.echo(" {bggray}%s{/all}" % (" "*(terminalwidth-2)), wordwrap=False)
  return

#def handlemenu(prompt="menu:", menu=[], default="A"):
#  ttyio.echo("%s{decsc}{cha}{cursorright:4}{cursorup:%d}A{cursorleft}" % (prompt, 4+len(menu)), end="", flush=True)
#
#  res = None
#  pos = 0
#  done = False
#  while not done:
#    ch = ttyio.getch(noneok=False).upper()
#    oldpos = pos
#    if ch == "Q":
#      ttyio.echo("{decrc}Q: Quit")
#      break
#    elif ch == "\004":
#      raise EOFError
#    elif ch == "KEY_DOWN":
#      if pos < len(menu):
#        ttyio.echo("{black}{bggray}%s{cursorleft}{cursordown}" % (chr(ord('A')+pos)), end="", flush=True)
#        pos += 1
#      else:
#        ttyio.echo("{cursorup:%d}" % (pos), end="", flush=True)
#        pos = 0
#    elif ch == "KEY_UP":
#      if pos > 0:
#        ttyio.echo("{cursorup}", end="", flush=True)
#        pos -= 1
#      else:
#        ttyio.echo("{cursordown:%d}" % (len(menu)), end="", flush=True)
#        pos = len(menu)
#    elif ch == "\n":
#      # ttyio.echo("pos=%d len=%d" % (pos, len(menu)))
#      return pos
#    elif ch == "KEY_HOME":
#      if pos > 0:
#        ttyio.echo("{cursorup:%d}" % (pos-1), end="", flush=True)
#        pos = 0
#    elif ch == "KEY_END":
#      ttyio.echo("{cursordown:%d}" % (len(menu)-pos), end="", flush=True)
#      pos = len(menu)+1
#    elif ch == "KEY_LEFT" or ch == "KEY_RIGHT":
#      ttyio.echo("{bell}", flush=True, end="")
#    elif ch == "Q":
##      ttyio.echo("{decrc}Q: Quit")
#      return None
#    else:
#      if len(ch) > 1:
#        ttyio.echo("{bell}", end="", flush=True)
#        continue
#      i = ord(ch) - ord('A')
#      if i > len(menu)-1:
#        ttyio.echo("{bell}", end="", flush=True)
#        continue
#      return i
#  return res

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
  done = False
  while not done:
    displaymenu(menu, title="test of handlemenu")
    res = bbsengine.handlemenu("prompt!: ", menu)
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
        ttyio.echo("{decrc}%s: %s" % (chr(ord('A')+i), menu[i]["label"]))
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
      ttyio.echo("{decrc}Q: Quit")
      done = True
      break

#  ttyio.echo(repr(menu), interpret=False)

if __name__ == "__main__":
  try:
    main()
  except KeyboardInterrupt:
    ttyio.echo("{decrc}INTR")
  except EOFError:
    ttyio.echo("{decrc}EOF")
  finally:
    ttyio.echo("{/all}")
