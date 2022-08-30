import ttyio5 as ttyio
import bbsengine5 as bbsengine
from bbsengine5 import Menu

from argparse import Namespace

def preprompthook(args):
#  ttyio.echo("preprompthook")
  return

def main():
  def generic(args, **kwargs):
    if "label" not in kwargs:
      raise KeyError
    label = kwargs["label"]
    if label is None:
      raise ValueError
    return (True, ("yes", label, "anotherresultitem"))

  alphahelp = """Lorem ipsum dolor sit amet, consectetur adipiscing elit. Fusce ultricies diam metus, a interdum nisl dictum a. Praesent et magna finibus, elementum erat vel, lacinia diam. Phasellus a fermentum risus, ullamcorper semper purus. Nunc pellentesque lorem quis egestas consequat. Ut varius venenatis odio, a eleifend turpis euismod nec. Aliquam erat volutpat. Suspendisse vestibulum augue enim, ac facilisis elit tristique quis. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Morbi condimentum eros vitae feugiat pellentesque. Ut sed placerat est, eget pharetra dolor. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Nulla eget sagittis leo. Nullam a maximus lectus. Sed nec vulputate libero. In eu erat a purus ultricies feugiat eget sed nulla.
{f6}{f6}Integer neque lorem, eleifend in magna sit amet, cursus finibus risus. Duis rutrum est vehicula lorem vulputate, vitae consequat felis ultricies. In pretium felis vitae metus convallis auctor. Aenean sollicitudin porttitor ultrices. In hac habitasse platea dictumst. Sed maximus semper velit non sodales. Phasellus laoreet enim vitae laoreet cursus. Duis in consequat mi, vel interdum nisi. Aliquam blandit egestas sapien, nec aliquet nibh semper ut. Aliquam porttitor nulla suscipit, tempus dui sed, dignissim eros.
"""

  def alpha(args, **kwargs):
#    return False
    return generic(args, **kwargs)
  def bravo(args, **kwargs):
    return generic(args, **kwargs)
  def charlie(args, **kwargs):
    return generic(args, **kwargs)
  def delta(args, **kwargs):
    return generic(args, **kwargs)

  def foxtrot(args, **kwargs):
    menuitems = [
      { "name": "golf",    "label": "Golf",    "callback": golf, "description":"another description", "requires":["bravo"], "group":"foxtrot"},
    ]
    bbsengine.setarea("foxtrot")
    menu = bbsengine.Menu("foxtrot group", menuitems, args=args)
    menu.run("foxtrot: ", preprompthook)
    for m in menuitems:
      result = m["result"] if "result" in m else None
      name = m["name"]
      bbsengine.menuitemresults[name] = result
    bbsengine.poparea()
    return True
    
  def golf(args, **kwargs):
    return generic(args, **kwargs)
  def hotel(args, **kwargs):
    return generic(args, **kwargs)

  menuitems = [
 #      { "name": "golf",    "label": "Golf",    "callback": golf, "description":"another description", "requires":["bravo"], "group":"golf"},
#      { "name": "alpha",   "label": "Alpha",   "callback": alpha, "description":"{red}foo {green}bar {blue}baz{/all}", "help": alphahelp, "group":"mainmenu"},
      { "name": "alpha",   "label": "Alpha",   "callback": alpha, "description":"foo bar baz", "help": alphahelp, "result":(True, "testing!")},
      { "name": "bravo",   "label": "Bravo",   "callback": bravo },
      { "name": "charlie", "label": "Charlie", "callback": charlie, "requires": ("alpha", "bravo")},
      { "name": "delta",   "label": "Delta",   "callback": delta, "requires": ("alpha", "bravo", "charlie")},
      { "name": "echo",    "label": "Echo",    "callback": "echo"},
      { "name": "foxtrot", "label": "Foxtrot", "callback": foxtrot},
      { "name": "hotel",   "label": "Hotel",   "callback": hotel, "requires": ("golf",), "group":"mainmenu"},
  ]
    
#  ttyio.setvariable("engine.areacolor", "{bglightgray}{white}")

  ttyio.setvariable("engine.menu.boxcharcolor", "{bglightgray}{darkgreen}")
  ttyio.setvariable("engine.menu.color", "{bggray}")
  ttyio.setvariable("engine.menu.shadowcolor", "{bgdarkgray}")
  ttyio.setvariable("engine.menu.cursorcolor", "{bglightgray}{blue}")
  ttyio.setvariable("engine.menu.boxcolor", "{bgblue}{green}")
  ttyio.setvariable("engine.menu.itemcolor", "{blue}{bglightgray}")
  ttyio.setvariable("engine.menu.titlecolor", "{black}{bglightgray}")
  ttyio.setvariable("engine.menu.promptcolor", "")
  ttyio.setvariable("engine.menu.inputcolor", "{white}")
  ttyio.setvariable("engine.menu.disableditemcolor", "{darkgray}")
  ttyio.setvariable("engine.menu.resultfailedcolor", "{bgred}{white}")

  args = Namespace()

  ttyio.echo("{f6:3}{cursorup:3}")
  bbsengine.initscreen(bottommargin=1)
  bbsengine.setarea("bbsengine5.menu test")

  menu = Menu("test of bbsengine5.menu", menuitems, "test Menu")

  try:
    menu.run("testmenu: ", preprompthook)
  except EOFError:
    ttyio.echo("{/all}{decrc}{bold}EOF{/bold}")
  except KeyboardInterrupt:
    ttyio.echo("{/all}{decrc}{bold}INTR{/bold}")
  finally:
    ttyio.echo("{decsc}{curpos:%d,0}{el}{decrc}{reset}{/all}" % (ttyio.getterminalheight()))

if __name__ == "__main__":
  bbsengine.initscreen(bottommargin=1)
  main()
