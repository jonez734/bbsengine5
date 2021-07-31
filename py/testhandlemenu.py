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
  ttyio.setvariable("menu.boxcharcolor", "{bglightgray}{green}")
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
    displaymenu(menu, title="bing")
    res = bbsengine.handlemenu("{f6}{var:menu.promptcolor}prompt: {var:menu.inputcolor}", menu)
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
