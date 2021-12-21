import os
import argparse
import importlib

import ttyio5 as ttyio

import bbsengine5 as bbsengine
# from bbsengine5 import runcallback

#
# @see https://sites.google.com/site/xiangyangsite/home/technical-tips/software-development/python/python-readline-completions
# @see https://docs.python.org/3.3/howto/argparse.html#introducing-positional-arguments
# @see https://docs.python.org/3.3/library/argparse.html#module-argparse
# @see https://pymotw.com/3/importlib/
#

def setarea(args, left):
  def right():
    currentmember = bbsengine.getcurrentmember(args)
    if currentmember is None:
      return ""
    rightbuf = "| %s | %s" % (currentmember["name"], bbsengine.pluralize(currentmember["credits"], "credit", "credits"))
    return rightbuf
  bbsengine.setarea(left, right)

def updatetopbar(args, area):
    currentmember = bbsengine.getcurrentmember(args)
    terminalwidth = bbsengine.getterminalwidth()
    leftbuf = area
    buf = ""
    if currentmember is not None:
      buf = "{bggray}{white} %s %s " % (leftbuf.ljust(terminalwidth-len(rightbuf)-3, "-"), rightbuf)
    bbsengine.updatetopbar(buf)
    return

def runprg(args, **kwargs):
#  print("runprg.100: trace")
  command = kwargs["command"] if "command" in kwargs else None
  if command is None:
    return None
  module = command["prg"] if "prg" in command else None
#  ttyio.echo("runprg.120: module=%r" % (module))
  if module is None:
    return None
  x = module.split(".")
  m = x[0]
  if len(x) == 1:
    f = "main"
  else:
    f = x[1]
  a = importlib.import_module(m)
#  ttyio.echo("a=%r" % (a), interpet=False, level="debug")
  res = eval("a.%s" % (f), {"a": a})
#  print(res)
  if callable(res) is True:
    res()
  else:
    ttyio.echo("programming error", level="error")
  return

def shellout(args, **kwargs):
  if "command" in kwargs:
#    ttyio.echo("shellout.100: command=%r" % (kwargs["command"]), level="debug", interpret=False)
    if "shell" in kwargs["command"]:
      shell = kwargs["command"]["shell"]
      ttyio.echo("shellout.120: shell=%r" % (shell), level="debug")
      setarea(args, shell)
      res = os.system(shell)
      bbsengine.poparea()
      return res
    else:
      ttyio.echo("command does not have a 'shell' key. failed.", level="error")
      return

commands = (
    {"command": "teos",     "callback": runprg, "prg": "teos",     "help": "sig view"},
    {"command": "socrates", "callback": runprg, "prg": "socrates", "help": "forums"},
    {"command": "ogun",     "callback": runprg, "prg": "ogun",     "help": "link database"},
    {"command": "glossary", "callback": runprg, "prg": "aolbonics", "help": "glossary of terms"},
    {"command": "empyre",   "callback": runprg, "prg": "empyre",   "help": "run the game empyre"},
    {"command": "achilles", "callback": runprg, "prg": "achilles", "help": "achilles: a study of msg and related food additives"},
    {"command": "engine",   "callback": runprg, "prg": "engine",   "help": "manage engine (members, sessions, etc)"},
    {"command": "weather",  "callback": runprg, "prg": "weather",  "help": "weather report"},
    {"command": "help",     "callback": help},
    # socrates.addpost()?
)

# @since 20201125
class shellCommandCompleter(object):
  def __init__(self:object, args:object):
#    ttyio.echo("init shellCommandCompleter object", level="debug")
    pass

  @classmethod
  def complete(self:object, text:str, state:int):
#    ttyio.echo("commands=%r", interpret=False)
    vocab = []
    for c in commands:
      vocab.append(c["command"])
    results = [x for x in vocab if x.startswith(text)] + [None]
    return results[state]


def help():
  maxlen = 0
  for c in commands:
    l = len(c["command"])+2
    if l > maxlen:
      maxlen = l

  ttyio.echo("help.100: l=%r" % (maxlen))
  bbsengine.title("shell commands", hrcolor="{green}", titlecolor="{bggray}{white}")
  for c in commands:
    n = c["command"].ljust(maxlen)
    if "help" in c:
      ttyio.echo("{bggray}{white}%s{/bgcolor}{green} %s" % (n, c["help"]))
    else:
      ttyio.echo("{bggray}{white}%s{/bgcolor}{green}" % (n))
  ttyio.echo("{/all}")
  return

def main():
  ttyio.setvariable("engine.areacolor", "{bggray}{white}")
#  ttyio.echo("{f6:3}{curpos:%d,0}" % (ttyio.getterminalheight()-2))

  parser = argparse.ArgumentParser(prog="bbs")
  parser.add_argument("--verbose", default=True, action="store_true", help="use verbose mode")
  parser.add_argument("--debug", default=False, action="store_true", help="run debug mode")
  parser.add_argument("--dry-run", dest="dryrun", action="store_true", default=True, help="dry run (no database changes)")

  defaults = {"databasename":"zoidweb5", "databasehost": "localhost", "databaseport":5432, "databaseuser": None, "databasepassword":None}
  bbsengine.buildargdatabasegroup(parser, defaults)

  subparsers = parser.add_subparsers(dest="command", help='sub-command help')
  p = subparsers.add_parser('post-add', help='post-add help (socrates)')
  p.add_argument('--freeze', action="store_true", required=False, default=False, help="marks a post so it cannot accept replies/subnodes")
  p.add_argument("--eros", action="store_true", required=False, default=False, help="marks a post as 'adult content'")
  p.add_argument("--draft", action="store_true", required=False, default=True, help="mark the post as 'draft'")
  p.add_argument("--body", type=argparse.FileType("r"), required=False, help="filename used for body of post")
  p.add_argument("--title", required=False, action="store", help="title of post")

  p = subparsers.add_parser("post-read-new", help="read new posts")
  # parser_b.add_argument('--baz', choices='XYZ', help='baz help')
  p = subparsers.add_parser("link-read-new", help="read new links")
  args = parser.parse_args()
#  ttyio.echo("args=%r" % (args), level="debug")

  bbsengine.initscreen(bottommargin=1)
  setarea(args, "gfd!")

  if args.command == "post-add":
    ttyio.echo("socrates post-add")
    buf = ["socrates"]
    for attr in ("databasehost", "databasename", "databaseport", "databaseuser", "databasepassword", "title", "freeze", "eros", "draft"):
      if attr in args:
        buf.append("--%s=%r" % (attr, getattr(args, attr)))
    buf.append("post-add")
    for attr in ("freeze", "draft", "eros"):
      if getattr(args, attr) is True:
        buf.append("--%s" % (attr))
    for attr in ("title", "body"):
      v = getattr(args, attr)
      if v is not None:
        buf.append("--%s=%r" % (attr, v))
    ttyio.echo("buf=%r" % (buf))
    return

  bbsengine.initscreen(bottommargin=1)

  done = False
  while not done:
    # @todo: handle subcommands as tab-complete
    # ttyio.echo("args=%r" % (args), level="debug")

#    bbsengine.inittopbar()
#    updatetopbar(args, "gfd3")

    # ttyio.echo(bbsengine.datestamp(format="%c %Z"))
    ttyio.setvariable("engine.areacolor", "{bggray}{white}")
  #  ttyio.echo("{f6:3}{curpos:%d,0}" % (ttyio.getterminalheight()-2))
    setarea(args, "gfd!")

    prompt = "{f6}{bggray}{white}%s{/bgcolor}{F6}{green}gf main: {lightgreen}" % (bbsengine.datestamp(format="%c %Z"))
    try:
      # ttyio.echo("prompt=%r" % (prompt))
      buf = ttyio.inputstring(prompt, multiple=False, returnseq=False, verify=None, completer=shellCommandCompleter(args), completerdelims=" ")
    except EOFError:
      ttyio.echo("EOF")
      return
    except KeyboardInterrupt:
      ttyio.echo("INTR")
      return

    if buf is None or buf == "":
      continue
    elif buf == "?" or buf == "help":
      help()
      continue
    elif buf == "logout" or buf == "lo" or buf == "quit" or buf == "q" or buf == "o!" or buf == "o":
      ttyio.echo("logout")
      done = True
      break

    found = False
    argv = buf.split(" ")
    for c in commands:
      command = c["command"]
      callback = c["callback"]
      if argv[0] == command:
        found = True
        bbsengine.runcallback(args, callback, command=c)
        break
    if found is False:
      ttyio.echo("command not found", level="error")
    # args = buf.split(" ")
    # parser.parse_known_args(args) -- this is for global args for the shell
  # return ttyio.inputstring(prompt, oldvalue, opts=opts, verify=verify, multiple=multiple, completer=sigcompleter(opts), returnseq=True, **kw)

if __name__ == "__main__":
  try:
      main()
  except KeyboardInterrupt:
      ttyio.echo("{/all}{bold}INTR{bold}")
  except EOFError:
      ttyio.echo("{/all}{bold}EOF{/bold}")
  finally:
      ttyio.echo("{decsc}{curpos:%d,0}{el}{decrc}{reset}{/all}" % (ttyio.getterminalheight()))
