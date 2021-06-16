import os
import argparse
import importlib

import ttyio4 as ttyio

import bbsengine5 as bbsengine
# from bbsengine5 import runcallback

#
# @see https://sites.google.com/site/xiangyangsite/home/technical-tips/software-development/python/python-readline-completions
# @see https://docs.python.org/3.3/howto/argparse.html#introducing-positional-arguments
# @see https://docs.python.org/3.3/library/argparse.html#module-argparse
# @see https://pymotw.com/3/importlib/
#

def updatetopbar(args, area):
    currentmember = bbsengine.getcurrentmember(args)
    terminalwidth = bbsengine.getterminalwidth()
    leftbuf = area
    rightbuf = ""
    if currentmember is not None:
        rightbuf += "| %s | %s" % (currentmember["name"], bbsengine.pluralize(currentmember["credits"], "credit", "credits"))
    buf = "{bggray}{white} %s %s " % (leftbuf.ljust(terminalwidth-len(rightbuf)-3, "-"), rightbuf)
    bbsengine.updatetopbar(buf)
    return

def verifyMemberNotFound(args, name):
    ttyio.echo("args=%r" % (args))
    dbh = bbsengine.databaseconnect(args)
    cur = dbh.cursor()
    sql = "select 1 from engine.member where name=%s"
    dat = (name,)
    cur.execute(sql, dat)
    if cur.rowcount == 0:
        return True
    return False

def verifyMemberFound(args, name):
    ttyio.echo("args=%r" % (args), level="debug")
    dbh = bbsengine.databaseconnect(args)
    cur = dbh.cursor()
    sql = "select 1 from engine.member where name=%s"
    dat = (name,)
    cur.execute(sql, dat)
    if cur.rowcount == 0:
        return False
    return True

def shellout(args, **kwargs):
  if "command" in kwargs and "shell" in kwargs["command"]["shell"]:
    shell = kwargs["command"]["shell"]
    updatetopbar(args, shell)
    return os.system(shell)
  else:
    ttyio.echo("command does not have a 'shell' key. failed.", level="error")
    return


commands = (
    {"command": "teos",     "callback": shellout, "shell": "teos", "help": "sig view"},
    {"command": "socrates", "callback": shellout, "shell": "socrates", "help": "post view"},
    {"command": "ogun",     "callback": shellout, "shell": "ogun", "help": "link view"},
    {"command": "glossary", "callback": shellout, "shell": "aolbonics", "help": "glossary"},
    {"command": "empyre",   "callback": shellout, "shell": "empyre", "help":"run the game empyre"},
    {"command": "achilles", "callback": shellout, "shell": "achilles", "help": "achilles: a study of msg"},
    {"command": "post-add", "callback": "socrates.addpost", "help":"add new post"},
    {"command": "engine",   "callback": shellout, "help":"manage engine (members, sessions, etc)"},
    {"command": "help",     "callback": help},
)

# @since 20201125
class shellCommandCompleter(object):
  def __init__(self:object, args:object):
    # ttyio.echo("init shellCommandCompleter object", level="debug")
    pass

  @classmethod
  def completer(self:object, text:str, state:int):
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
  ttyio.echo("args=%r" % (args), level="debug")
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

  done = False
  while not done:
    # @todo: handle subcommands as tab-complete
    # ttyio.echo("args=%r" % (args), level="debug")

    bbsengine.inittopbar()
    updatetopbar(args, "gfd3")

    # ttyio.echo(bbsengine.datestamp(format="%c %Z"))
    prompt = "{bggray}{white}%s{/bgcolor}{F6}{green}gfd3 main: {lightgreen}" % (bbsengine.datestamp(format="%c %Z"))
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
    elif buf == "logout" or buf == "lo" or buf == "quit" or buf == "q":
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
        bbsengine.runcallback(args, callback, command=command)
        break
    if found is False:
      ttyio.echo("command not found", level="error")
    # args = buf.split(" ")
    # parser.parse_known_args(args) -- this is for global args for the shell
  # return ttyio.inputstring(prompt, oldvalue, opts=opts, verify=verify, multiple=multiple, completer=sigcompleter(opts), returnseq=True, **kw)

if __name__ == "__main__":
  try:
    main()
  finally:
    ttyio.echo("{/all}{reset}")
