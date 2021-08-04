import ttyio4 as ttyio
import bbsengine5 as bbsengine

def main():
  menuitems = [
      { "label": "alpha",   "callback": "alpha", "description":"foo bar baz", "help": "alphahelp"},
      { "label": "bravo",   "callback": "bravo" },
      { "label": "charlie", "callback": "charlie" },
      { "label": "delta",   "callback": "delta"},
      { "label": "echo",    "callback": "echo"},
      { "label": "foxtrot", "callback": "foxtrot"},
      { "label": "golf",    "callback": "golf", "description":"another description"}
  ]
    
  ttyio.setvariable("menu.boxcharcolor", "{bglightgray}{white}")
  ttyio.setvariable("menu.backgroundcolor", "{bggray}")
  ttyio.setvariable("menu.shadowbackgroundcolor", "{bgdarkgray}")
  ttyio.setvariable("menu.cursorcolor", "{bglightgray}{blue}")
  ttyio.setvariable("menu.boxcolor", "{bgblue}{green}")
  ttyio.setvariable("menu.itemcolor", "{blue}{bglightgray}")
  ttyio.setvariable("menu.titlecolor", "{black}{bglightgray}")
  ttyio.setvariable("menu.promptcolor", "{white}{bgblack}")
  ttyio.setvariable("menu.inputcolor", "{white}{bgblack}")

  m = bbsengine.Menu(menuitems, title="test title!")
  done = False
  while not done:
    m.display()
    res = m.handle("{var:menu.promptcolor}prompt: {var:menu.inputcolor}")
    if res is None:
      return
    elif type(res) == tuple:
      (op, i) = res
    else:
      ttyio.echo("invalid return type from handle menu %r!" % (type(res)), level="error")
      break

    if i < len(menuitems):
      if op == "select":
        ttyio.echo("{decrc}{var:menu.inputcolor}%s: %s{/all}" % (chr(ord('A')+i), menuitems[i]["label"]))
#        ttyio.echo("menu[i]=%r" % (menu[i]), interpret=False, level="debug", interpret=False)
        bbsengine.runcallback(None, menuitems[i]["callback"], menuitem=menuitems[i])
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

if __name__ == "__main__":
    main()

