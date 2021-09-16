import ttyio4 as ttyio
import bbsengine5 as bbsengine

from argparse import Namespace

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
    return generic(args, **kwargs)
  def bravo(args, **kwargs):
    return generic(args, **kwargs)
  def charlie(args, **kwargs):
    return generic(args, **kwargs)
  def delta(args, **kwargs):
    return generic(args, **kwargs)
  def golf(args, **kwargs):
    return generic(args, **kwargs)

  menuitems = [
      { "label": "alpha",   "callback": alpha, "description":"foo bar baz", "help": alphahelp},
      { "label": "bravo",   "callback": bravo },
      { "label": "charlie", "callback": charlie, "requires": ("alpha", "bravo") },
      { "label": "delta",   "callback": delta},
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
  ttyio.setvariable("menu.disableditemcolor", "{darkgray}")

  args = Namespace()

  menu = bbsengine.Menu("test of bbsengine.Menu", menuitems)
  menu.run()

if __name__ == "__main__":
    main()
