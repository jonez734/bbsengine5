import ttyio4 as ttyio
import bbsengine5 as bbsengine

def main():
  def alpha(args, **kwargs):
    if "label" not in kwargs:
      raise ValueError
    label = kwargs["label"]
    if label is None:
      raise ValueError

    if "menu" not in kwargs:
      raise ValueError
    menu = kwargs["menu"]

    menuitem = menu.find(label)
    if menuitem is None:
      raise ValueError

    menuitem["description"] = "yes - alpha"
    menuitem["result"] = True
    if "requires" in menuitem:
      requires = menuitem["requires"]
    if menu.resolverequires(menuitem) is True:
      ttyio.echo("all requirements resolved.")
    else:
      ttyio.echo("all requirements not resolved. proceed?")
    return menuitem["result"]

  def bravo(args, **kwargs):
    if "label" not in kwargs:
      raise ValueError
    label = kwargs["label"]
    if label is None:
      raise ValueError

    if "menu" not in kwargs:
      raise ValueError
    menu = kwargs["menu"]

    menuitem = menu.find(label)
    if menuitem is None:
      raise ValueError

    menuitem["description"] = "yes - bravo"
    menuitem["result"] = True
    if "requires" in menuitem:
      requires = menuitem["requires"]
    if menu.resolverequires(menuitem) is True:
      ttyio.echo("all requirements resolved.")
    else:
      ttyio.echo("all requirements not resolved. proceed?")
    return menuitem["result"]

  def golf(args, **kwargs):
    if "label" not in kwargs:
      raise ValueError
    label = kwargs["label"]
    if label is None:
      raise ValueError

    if "menu" not in kwargs:
      raise ValueError
    menu = kwargs["menu"]

    menuitem = menu.find(label)
    if menuitem is None:
      raise ValueError

    menuitem["description"] = "yes - golf"
    menuitem["result"] = True
    if "requires" in menuitem:
      requires = menuitem["requires"]
    if menu.resolverequires(menuitem) is True:
      ttyio.echo("all requirements resolved.")
    else:
      ttyio.echo("all requirements not resolved. proceed?")
    return menuitem["result"]

  menuitems = [
      { "label": "alpha",   "callback": alpha, "description":"foo bar baz", "help": "alphahelp"},
      { "label": "bravo",   "callback": bravo },
      { "label": "charlie", "callback": "charlie", "requires": ("alpha", "bravo") },
      { "label": "delta",   "callback": "delta"},
      { "label": "echo",    "callback": "echo"},
      { "label": "foxtrot", "callback": "foxtrot"},
      { "label": "golf",    "callback": golf, "description":"another description", "requires":["bravo"]}
  ]
    
  ttyio.setvariable("menu.boxcharcolor", "{bglightgray}{white}")
  ttyio.setvariable("menu.backgroundcolor", "{bggray}")
  ttyio.setvariable("menu.shadowbackgroundcolor", "{bgdarkgray}")
  ttyio.setvariable("menu.cursorcolor", "{bglightgray}{blue}")
  ttyio.setvariable("menu.boxcolor", "{bgblue}{green}")
  ttyio.setvariable("menu.itemcolor", "{blue}{bglightgray}")
  ttyio.setvariable("menu.titlecolor", "{black}{bglightgray}")
  ttyio.setvariable("menu.promptcolor", "{white}")
  ttyio.setvariable("menu.inputcolor", "{white}")
  ttyio.setvariable("menu.disableditemcolor", "{black}")

  menu = bbsengine.Menu("test title!", menuitems)
  done = False
  while not done:
    menu.display()
    res = menu.handle("{var:menu.promptcolor}prompt: {var:menu.inputcolor}")
    if res is None:
      return
    elif res == "KEY_FF":
      ttyio.echo("{decrc}refresh")
      continue
    elif type(res) == tuple:
      (op, i) = res
    else:
      ttyio.echo("invalid return type from handle menu %r!" % (type(res)), level="error")
      break

    if i < len(menuitems):
      if op == "select":
        ttyio.echo("{decrc}{var:menu.inputcolor}%s: %s{/all}" % (chr(ord('A')+i), menuitems[i]["label"]))
#        ttyio.echo("menu[i]=%r" % (menu[i]), interpret=False, level="debug", interpret=False)
        label = menuitems[i]["label"]
        callback = menuitems[i]["callback"]
        bbsengine.runcallback(None, callback, menu=menu, label=label) # menuitem=menuitems[i])
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

