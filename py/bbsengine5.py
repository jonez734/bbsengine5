from __future__ import generators    # needs to be at the top of your module
#
# Copyright (C) 2008-2021 zoidtechnologies.com. All Rights Reserved.
#

import re, os, sys, pwd, time, random

import psycopg2, psycopg2.extras
from psycopg2.extras import Json
from psycopg2.extensions import parse_dsn, make_dsn

from datetime import datetime, timedelta, tzinfo

from syslog import *

from argparse import Namespace

import ttyio5 as ttyio

import importlib

from typing import Any, List, NamedTuple

try:
  import getdate
except ImportError:
  usegetdate = False
else:
  usegetdate = True

class Node(object):
  def __init__(self, prg="node", table=""):
    self.prg = prg
    self.table = table
  def load(self, id:int):
    sql = "select * from %s where id=%%s" % (self.table)
    dat = (id,)
    cur = self.dbh.cursor()
    cur.execute(sql, dat)
    res = cur.fetchone()
    if res is None:
        return False

    attributes = res["attributes"] if "attributes" in res else {}
    if self.args.debug is True:
        ttyio.echo("attributes=%r" % (attributes), level="debug")

    for a in self.attributes:
        ttyio.echo("Node.load.120: a=%r" % (a), level="debug")

        name = a["name"]
        default = a["default"]

        if name not in attributes:
            if self.args.debug is True:
                ttyio.echo("name %r not in database record, using default" % (name), level="warning")
            value = default
        else:
            value = attributes[name]

        if self.args.debug is True:
            ttyio.echo("Node.load.140: name=%s default=%s value=%s" % (name, default, value), level="debug")
        setattr(self, name, value)

    self.id = id

  def __update(self):
      if self.id < 1:
          ttyio.echo("invalid id passed to update().", level="error")
          return

      attributes = {}
      for a in self.attributes:
          name = a["name"]
          attr = self.getattribute(name)
          if attr is None:
              ttyio.echo("invalid attribute %r" % (name))
              continue
          attributes[name] = attr["value"] # self.getattribute(name) # getattr(self, name)

      return bbsengine.updatenodeattributes(self.dbh, self.args, self.id, attributes)

  def isdirty(self):
      def getattrval(name):
          for a in self.attributes:
              if a["name"] == name:
                  return a["value"] if "value" in a else a["default"]

      for a in self.attributes:
          name = a["name"]
          curval = getattr(self, name)
          oldval = getattrval(name)
          if curval != oldval:
              if "debug" in self.args and self.args.debug is True:
                  ttyio.echo("Node.isdirty.100: name=%r oldval=%r curval=%r" % (name, oldval, curval))
              return True
      return False

  def save(self, updatecredits=False):
      if self.args.debug is True:
          ttyio.echo("Node.save.100: id=%r" % (self.id), level="debug")
      if self.id is None:
          ttyio.echo("id is not set. aborted.", level="error")
          return None

      if self.memberid is None:
          ttyio.echo("Node: memberid is not set. aborted.", level="error")
          return None

      if self.isdirty() is False:
          if "debug" in self.args and self.args.debug is True:
              ttyio.echo("%s: clean. no save." % (self.name))
          return
      ttyio.echo("%s: dirty. saving." % (self.name))

      # self.dbh = bbsengine.databaseconnect(self.args)
      try:
          self.update()
          if updatecredits is True:
              # corruption if credits are updated after player.load()
              bbsengine.setmembercredits(self.dbh, self.memberid, self.credits)
      except:
          ttyio.echo("exception saving casino record")
      else:
          ttyio.echo("Node.save.100: running commit()", level="debug")
          self.dbh.commit()
          ttyio.echo("Node saved", level="success")
      return

  def __insert(self):
      attributes = {}
      for a in self.attributes:
          name = a["name"]
          attr = self.getattribute(name)
          value = attr["value"]
          ttyio.echo("Node.insert.100: %r=%r" % (name, value))
          attributes[name] = value
          ttyio.echo("attributes.name=%r" % (attributes["name"]))

      node = {}
      node["prg"] = self.prg
      node["attributes"] = attributes
      # self.dbh = bbsengine.databaseconnect(self.args)
      nodeid = bbsengine.insertnode(self.dbh, self.args, node, mogrify=False)
      ttyio.echo("Node.insert.100: id=%r" % (self.id), level="debug")
      return nodeid

def verifyprimarykey(dbh, args, table, primarykey, value):
  sql = "select 1 as verified from %s where %s=%%s" % (table, primarykey)
  dat = (value,)
  cur = dbh.cursor()
  # ttyio.echo("verifyprimarykey.100: mogrify=%s" % (cur.mogrify(sql, dat)), level="debug")
  if args.debug is True:
    ttyio.echo("verifyprimarykey.100: mogrify=%s" % (cur.mogrify(sql, dat)), level="debug")
  cur.execute(sql, dat)
  res = cur.fetchone()
  if args.debug is True:
    ttyio.echo("verifyprimarykey.105: res=%s" % (res), level="debug")
  if res is None:
    if args.debug is True:
      ttyio.echo("verifyprimarykey.108: res is none", level="debug")
    return False

  rec = res["verified"]
  if rec == 1:
    if args.debug is True:
      ttyio.echo("verifyprimarykey.110: returning True", level="debug")
    return True

  if args.debug is True:
    ttyio.echo("verifyprimarykey.120: returning False", level="debug")
  return False

class inputcompleter(object):
  def __init__(self, dbh, args, table, primarykey):
    ttyio.echo("inputcompleter.__init__", level="debug")
    self.args = args
    self.matches = []
    self.dbh = dbh
    self.table = table
    self.primarykey = primarykey

  def getmatches(self, text):
    if self.args.debug is True:
      ttyio.echo("inputcompleter.200: matches=%r table=%r primarykey=%r" % (self.matches, self.table, self.primarykey), level="debug")
    sql = "select distinct %s from %s where %s::text" % (self.primarykey, self.table, self.primarykey)
    sql += " ilike %s"
    dat = []
    if text == "":
      dat += ["%%"]
    else:
      dat += [text+"%"]
    if self.args.debug is True:
      ttyio.echo("inputcompleter.getmatches.110: sql=%s dat=%s" % (sql, dat), level="debug")
    
    cur = self.dbh.cursor()
    cur.execute(sql, dat)
    res = cur.fetchall()
    self.matches = []
    for rec in res:
      self.matches.append(str(rec[self.primarykey]))
    cur.close()
    return self.matches

  def completer(self, text, state):
    if state == 0:
      if text:
        self.matches = self.getmatches(text)
      else:
        self.matches = []

    if state < len(self.matches):
      return self.matches[state]
    
    return None

def inputprimarykey(dbh, args, table, primarykey, prompt, default, completer=None, verify=None, noneok=False, multi=False, delims=None):
  if completer is None:
    completer = inputcompleter(dbh, args, table, primarykey, prompt=prompt)
    ttyio.echo("completer is None", level="debug")

  if args.debug is True:
    ttyio.echo("inputprimarykey entered. primarykey=%s table=%s verify=%s, noneok=%s" % (primarykey, table, verify, noneok), level="debug")

  olddelims = readline.get_completer_delims()
  readline.set_completer_delims(", ")

  # c = customercodecompleter(dbh, opts)
  # c = zoidbo.inputcompleter(dbh, opts, "customer", "code")
  # result = zoidbo.inputprimarykey(dbh, opts, "customer", "code", completer=zoidbo.inputcompleter, verify=verify, noneok=noneok)
  # ttyio.echo("checking completer... %r" % (type(completer)), level="debug")
  if callable(completer) is True:
    # ttyio.echo("inputprimarykey.100: parse and bind", level="debug")
    c = completer(dbh, args, table, primarykey)
    readline.parse_and_bind("tab: complete")
    readline.set_completer(c.completer)
    ttyio.echo("completer set", level="debug")

  while True:
    if args.debug is True:
      buf = ttyio.inputstring(prompt, default, noneok=noneok)
      if buf is None or buf == "":
        if noneok is False:
          result = default
          break
        elif noneok is True:
          result = None
          break

    if verify is False or verify is None:
      result = buf
      break

    if callable(verify) is True:
      if args.debug is True:
        ttyio.echo("inputprimarykey.200: verify is callable", level="debug")
      v = verify(dbh, args, table, primarykey, buf)
      ttyio.echo("verify=%r" % (v), interpet=False)
      if v is True:
        if args.debug is True:
          ttyio.echo("verify returned true", level="debug")
        result = buf
        break
      else:
        ttyio.echo("%r is not valid." % (buf), level="error")
        continue
  
  readline.set_completer(oldcompleter)
  readline.set_completer_delims(olddelims)
    
  return result

databasehandles = {}
def _databaseconnect(**kw):
  dsn = make_dsn(**kw)
  if dsn in databasehandles:
    dbh = databasehandles[dsn]
    return databasehandles[dsn]

  dbh = psycopg2.connect(connection_factory=psycopg2.extras.DictConnection, cursor_factory=psycopg2.extras.RealDictCursor, **kw)
  databasehandles[dsn] = dbh
  return dbh

def databaseconnect(args):
    kw = {}
    if type(args) == type({}):
      if "databasekey" in args:
        kw["database"] = args["databasename"]
      if "databasehost" in args:
        kw["host"] = args["databasehost"]
      if "databaseuser" in args:
        kw["user"] = args["databaseuser"]
      if "databasepassword" in args:
        kw["password"] = args["databasepassword"]
      if "databaseport" in args:
        kw["port"] = args["databaseport"]
    else:
      if hasattr(args, "databasename"):
        kw["database"] = args.databasename
      if hasattr(args, "databasehost"):
        kw["host"] = args.databasehost
      if hasattr(args, "databaseuser"):
        kw["user"] = args.databaseuser
      if hasattr(args, "databasepassword"):
        kw["password"] = args.databasepassword
      if hasattr(args, "databaseport"):
        kw["port"] = args.databaseport
    
    return _databaseconnect(**kw)

import time as _time

# from http://docs.python.org/release/2.5.2/lib/datetime-tzinfo.html
ZERO = timedelta(0)
HOUR = timedelta(hours=1)

STDOFFSET = timedelta(seconds = -_time.timezone)
if _time.daylight:
    DSTOFFSET = timedelta(seconds = -_time.altzone)
else:
    DSTOFFSET = STDOFFSET

DSTDIFF = DSTOFFSET - STDOFFSET

class LocalTimezone(tzinfo):
    def utcoffset(self, dt):
        if self._isdst(dt):
            return DSTOFFSET
        else:
            return STDOFFSET

    def dst(self, dt):
        if self._isdst(dt):
            return DSTDIFF
        else:
            return ZERO

    def tzname(self, dt):
        return _time.tzname[self._isdst(dt)]

    def _isdst(self, dt):
        tt = (dt.year, dt.month, dt.day,
              dt.hour, dt.minute, dt.second,
              dt.weekday(), 0, -1)
        stamp = _time.mktime(tt)
        tt = _time.localtime(stamp)
        return tt.tm_isdst > 0

# @since 20120126
def inputdate(prompt, epoch=None, **kw):
  from getdate import getdate, error
  if epoch is None:
    buf = ttyio.inputstring(prompt, **kw)
  else:
    buf = ttyio.inputstring(prompt, datestamp(epoch), **kw)
  
  try:
    epoch = getdate(buf)
  except:
    return None
  else:
    return epoch

def areyousure(prompt="are you sure? ", default="N", options="YN") -> bool:
  res = inputboolean(prompt, default=default, options=options)
  if res is True:
    return 0
  return 1

# @since 20210223
def getsig(dbh, path):
  cur = dbh.cursor()
  sql = "select * from engine.sig where path ~ %s"
  dat = (path,)
  cur.execute(sql, dat)
  rec = cur.fetchone()
  sig = {}
  sig["title"] = rec["title"]
  sig["intro"] = rec["intro"]
  sig["path"] = rec["path"]
  for column in ("name", "lastmodified", "dateposted", "lastmodifiedbyid", "postedbyid", "dateupdated", "updatedbyid", "datecreated", "createdbyid", "attributes"):
    if column in rec:
      sig[column] = rec[column]
  return sig

def getsigpathfromid(dbh, id):
  sql = "select path from engine.sig where id=%s"
  dat = (id,)
  cur = dbh.cursor()
  cur.execute(sql, dat)
  res = cur.fetchone()
  cur.close()
  if res is None:
    return None
  if "path" in res:
    return res["path"]
  return None

def getsigidfrompath(dbh, path):
  if path is None:
    return None

  sql = "select id from engine.sig where path=%s"
  dat = (path,)
  cur = dbh.cursor()
  cur.execute(sql, dat)
  if cur.rowcount == 0:
    return None
  res = cur.fetchone()
  cur.close()
  return res["id"]

class sigcompleter(object):
  def __init__(self, args):
    self.dbh = databaseconnect(args)
    self.matches = []
    eros = checkflag(args, "EROS")
    self.eros = args.eros if "eros" in args else False
    if eros is True and self.eros is True:
      self.eros = True
    else:
      self.eros = False

    self.debug = args.debug
    if self.debug is True:
      print ("init sigcompleter object")

  def getmatches(self, text):
    sql = "select distinct path from engine.sig where path ~ %s"
    if self.eros is False:
      sql += " and not path ~ 'top.eros.*'"

    if text == "":
      dat = ("top.*{1}",)
    elif text[-1] == ".":
      dat = (text+"*{1}",)
    else:
      dat = (text+"*",)
    cur = self.dbh.cursor()
    if self.debug is True:
      print (sql, dat)
    cur.execute(sql, dat)
    res = cur.fetchall()
    foo = []
    for rec in res:
      foo.append(rec["path"])

    cur.close()
#    print foo
    return foo
  
  def complete(self, text, state):
#    print "state=",state,"text=",text
    if state == 0:
      self.matches = self.getmatches(text)
    
    return self.matches[state]
  
def buildlabel(label):
  return label

def normalizelabelpath(labelpath):
  if labelpath[:4] != "top." and labelpath != "top":
    labelpath = "top."+labelpath
  return labelpath

def buildsiglist(sigs:str) -> list:
  if type(sigs) == type([]):
    ttyio.echo("buildsiglist.100: type(sigs) == list", level="warning")
    return sigs
  res = re.split("[, ]", sigs)
  res = [s for s in res if s]
  return res

# @fix: check access to a given sig (eros.*)
def verifysigpath(args, sigpath):
  sql = "select 't' from engine.sig where path=%s"
  dat = (sigpath,)
  dbh = databaseconnect(args)
  cur = dbh.cursor()
  cur.execute(sql, dat)
  res = cur.fetchone()
  if res is None:
    return False
  return True

def inputsig(args, prompt="sig: ", oldvalue="", multiple=True, verify=verifysigpath, **kw):
  if args.debug is True:
    ttyio.echo("inputsig entered. multiple=%r verify=%r" % (multiple, verify), level="debug")

  return ttyio.inputstring(prompt, oldvalue, args=args, verify=verify, multiple=multiple, completer=sigcompleter(args), returnseq=True, **kw)

def getsignamefromid(dbh, id):
  if id is None:
    return None

#  dbh = dbconnect(cfgfile, "system")
  sql = "select name from engine.sig where id=%s"
  dat = (int(id),)
  cur = dbh.cursor()
  cur.execute(sql, dat)
  res = cur.fetchone()
  cur.close()
  dbh.close()
  if res is not None and "name" in res:
    return res["name"]
  return None

def update(dbh, table, key, values:dict, primarykey="id"):
  ttyio.echo("bbsengine5.update.100: values=%r" % (values), interpret=False)
  if primarykey in values:
    del values[primarykey]

  sql = "update %s set " % (table)
  params = []
  dat = []
  for k, v in values.items():
    params.append("%s=%%s" % (k),)
    dat.append(v)

  sql += ", ".join(params)
  sql += " where %s=%%s" % (primarykey)
  dat.append(key)

  cur = dbh.cursor()
  ret = cur.execute(sql, dat)
  cur.close()
  return ret

def insert(dbh, table, dict, returnid=True, primarykey="id", mogrify=False):
  columns = dict.keys()
  sql = "insert into %s(" % (table)
  sql += ", ".join(columns)
  sql += ") values ("
  params = []
  for x in range(len(columns)):
    params.append("%s")
  sql += ", ".join(params)
  sql += ")"

  dat = []
  for v in dict.values():
    dat.append(v)
  if returnid is True:
    sql += " returning %s.%s" % (table, primarykey)
  # ttyio.echo("bbsengine.insert.100: sql=%s dat=%s" % (sql, dat), level="debug")
  cur = dbh.cursor()
  if mogrify is True:
    print("bbsengine5.insert.mogrify.100: dat=%r" % (dat))
#      ttyio.echo(cur.mogrify(sql, [tuple(v.values() for v in dat)]), level="debug")
    ttyio.echo(cur.mogrify(sql, dat), level="debug", interpret=False)
  cur.execute(sql, dat)
  if returnid is True:
    res = cur.fetchone()
    if primarykey in res:
      return res[primarykey]
  cur.close()
  return None

def insertnode(dbh, args:object, node:dict, table:str="engine.__node", returnid:bool=True, primarykey:str="id", mogrify:bool=False):
  node["attributes"] = Json(node["attributes"])
  node["datecreated"] = "now()"
  node["createdbyid"] = getcurrentmemberid(args)
  if args.debug is True:
    ttyio.echo("bbsengine.insertnode.100: node=%r table=%r" % (node, table), level="debug")
  return insert(dbh, table, node, returnid=returnid, primarykey=primarykey, mogrify=mogrify)

def updatenodesigs(dbh, args:object, nodeid:int, sigpaths:str):
  # dbh is passed
  if sigpaths is None or len(sigpaths) == 0:
    return None

  cur = dbh.cursor()
  sql = "delete from engine.map_node_sig where nodeid=%s"
  dat = (nodeid,)
  cur.execute(sql, dat)
  for sigpath in sigpaths:
    sigmap = { "nodeid": nodeid, "sigpath": sigpath }
    insert(dbh, "engine.map_node_sig", sigmap, returnid=False, mogrify=False)
  dbh.commit()
  return None

def updatenodeattributes(dbh, args:object, nodeid:int, attributes:dict, reset:bool=False, table:str="engine.__node"):
  if reset is False:
    sql = "update %s set attributes=attributes||%%s where id=%s" % (table, nodeid)
  else:
    sql = "update %s set attributes=%%s where id=%s" % (table, nodeid)

  if args.debug is True:
    ttyio.echo("updatenodeattributes.120: sql=%s" % (sql), level="debug")

  dat = (Json(attributes),)
  if args.debug is True:
    ttyio.echo("bbsengine5.updatenodeattributes.100: dat=%r" % (dat), level="debug")
  cur = dbh.cursor()
  if args.debug is True:
    ttyio.echo("updatenodeattributes.100: %r" % (cur.mogrify(sql, dat)), level="debug")
  return cur.execute(sql, dat)

def updatenode(dbh, args:object, id:int, node:dict, reset=False):
  node["dateupdated"] = "now()"
  node["updatedbyid"] = getcurrentmemberid(args)
  attr = node["attributes"] if "attributes" in node else {}
  if len(attr) > 0:
    updatenodeattributes(dbh, args, id, attr, reset=reset)
    del node["attributes"]
  return update(dbh, "engine.__node", id, node)

def setflag(dbh, memberid, flag, value):
  logentry("setflag(%d, '%s', %s)" % (memberid, flag, value))
  sql = "delete from engine.map_member_flag where memberid=%s and name=%s"
  dat = (memberid, flag)
  cur = dbh.cursor()
  cur.execute(sql, dat)
  cur.close()

  mmf = {}
  mmf["memberid"] = memberid
  mmf["name"] = flag
  mmf["value"] = value
  
  insert(dbh, "engine.map_member_flag", mmf, returnid=False)

  return

def getflag(dbh, name, memberid=None):
  sql = """
select flag.name as name, coalesce(mmf.value, flag.defaultvalue) as value
from flag left outer join map_member_flag as mmf on flag.name = mmf.flagname
where flag.name=%s
"""
  dat = [name]
  if memberid is not None:
    sql +="  and mmf.memberid=%s"
    dat.append(memberid)

  sql += "limit 1"
#  print sql, dat
  
  cur = dbh.cursor()
  cur.execute(sql, dat)
  res = cur.fetchall()
  cur.close()
#  print "getflag.0: %r" % (type(res))
  if res is not None and len(res) == 1:
    return res[0]
  return None

def updateflag(dbh, flag):
  sql = "update flag set defaultvalue=%s, description=%s where name=%s"
  dat = (flag["defaultvalue"], flag["description"], flag["name"])
  cur = dbh.cursor()
  cur.execute(sql, dat)
  cur.close()
  return

# @since 20210106
def checkflag(args:object, flag:str, memberid:int=None):
  memberid = getcurrentmemberid(args)

  dbh = databaseconnect(args)
  sql = "select f.name, coalesce(mmf.value, f.defaultvalue) as value from engine.flag as f left outer join engine.map_member_flag as mmf on (f.name=mmf.name and mmf.memberid=%s) where f.name=%s"
  dat = (memberid, flag)
  cur = dbh.cursor()
  cur.execute(sql, dat)
  res = cur.fetchone()
  # ttyio.echo("bbsengine.checkflag.100: %s=%s" % (flag, res), level="debug")
  if res is None:
    return None
  return res["value"]

def logentry(message, output=True, level=None, priority=LOG_INFO, stripcommands=False, datestamp=True):
  if level is not None:
    if level == "debug":
      message = "{blue}** debug ** "+message+"{/all}"
    elif level == "warn":
      message = "{yellow}** warn ** "+message+"{/all}"
    elif level == "error":
      message = "{red}** error ** "+message+"{/all}"

  message = ttyio.interpretmci(message, strip=True)
  syslog(priority, message)

  if output is True:
    ttyio.echo(message, stripcommands=stripcommands, datestamp=datestamp, interpret=False)

  return

def datestamp(t=None, format:str="%Y/%m/%d %I:%M%P %Z (%a)") -> str:
  from dateutil.tz import tzlocal
  from datetime import datetime
  from time import strftime, tzset

  # ttyio.echo("bbsengine.datestamp.100: type(t)=%r" % (type(t)), level="debug")

  time.tzset()

  if type(t) == int or type(t) == float:
    t = datetime.fromtimestamp(t, tzlocal())
  elif t is None:
    t = datetime.now(tzlocal())

  stamp = strftime(format, t.timetuple())
  return stamp

currentmemberid = None
# @since 20120306
def getcurrentmemberid(args):
  global currentmemberid

  if currentmemberid is not None:
    return currentmemberid

  loginid = pwd.getpwuid(os.geteuid())[0]
  sql = "select id from engine.member where loginid=%s" 
  dat = (loginid,)
  dbh = databaseconnect(args)
  cur = dbh.cursor()
  cur.execute(sql, dat)
  if cur.rowcount == 0:
    return None
  res = cur.fetchone()

  # if args.debug is True:
  currentmemberid = res["id"]
  ttyio.echo("getcurrentmemberid.100: currentmemberid=%r" % (currentmemberid), level="debug")
  return currentmemberid

  if res is None:
    return None
  #if loginid in membermap:
  #  currentmemberid = membermap[loginid]
  #else:
  #  currentmemberid = None
  #return currentmemberid

# @since 20170303
def getcurrentmemberlogin(args):
  # membermap = {"jam" : 1}
  loginid = pwd.getpwuid(os.geteuid())[0]

  dbh = databaseconnect(args)
  cur = dbh.cursor()
  sql = "select 1 where attributes->>'loginid'=%s"
  dat = (loginid,)
  cur.execute(sql, dat)
  if cur.rowcount == 0:
    return None
  return loginid
  
  if loginid in membermap:
    return loginid
  return None

def buildname(txt):
  if txt is None:
    return None

  txt = txt.lower() # lowercase the string
  txt = re.sub(r"[^A-Za-z0-9\/_-]", "-", txt) # replace anything that is not alphanumeric or '_' or '-' with '-'
  txt = re.sub(r"[-]{2,}", "-", txt) # replace two or more '-' with a single '-'
  txt = re.sub(r"-$", "", txt) # trim '-' from end of string
  txt = re.sub(r"^-", "", txt) # trim '-' from beginning of string
  return txt

# http://www.brandonrubin.me/2014/03/18/python-snippet-get-terminal-width/
# moved to ttyio
def getterminalwidth():
  import subprocess
 
  command = ['tput', 'cols']
 
#  if sys.stdout.isatty() is False:
#    return False

  try:
    width = int(subprocess.check_output(command))
  except OSError as e:
    print("Invalid Command '{0}': exit status ({1})".format(command[0], e.errno))
    return False
  except subprocess.CalledProcessError as e:
    print("Command '{0}' returned non-zero exit status: ({1})".format(command, e.returncode))
    return False
  else:
    return int(width)

def explodesigpaths(paths):
  pass

def implodesigpaths(siglist):
  pass

class Form(object):
  def __init__(self, t, i, args=None):
    self.items = i
    self.title = t
    self.args = args
  def __len__(self):
    return len(self.items)
  def __getitem__(self, index):
    return self.items[index]

class MenuItem(object):
  def __init__(self):
    self.result = None
    self.description = None

  def display(self):
    pass

class Menu(object):
  def __init__(self, t, i, args=None, area=""):
    self.title = t
    self.items = i
    self.args = args
    self.area = area

  # @see https://stackoverflow.com/questions/11469025/how-to-implement-a-subscriptable-class-in-python-subscriptable-class-not-subsc
  def __getitem__(self, i):
    return self.items[i]

  def __len__(self):
    return len(self.items)

  def find(self, name):
#    ttyio.echo("Menu.find.180: name=%r" % (name))
    for m in self.items:
#      ttyio.echo("Menu.find.160: m.name=%r" % (m["name"]))
      if "name" in m and name == m["name"]:
#        ttyio.echo("Menu.find.120: %s found." % (name), level="debug")
        return m
      if "label" in m and name == m["label"]:
        return m
    else:
#      ttyio.echo("Menu.find.140: self.items is empty.")
      return None
    return False

  def resolverequires(self, menuitem):
    # ttyio.echo("Menu.resolverequires.160: menuitem=%r" % (menuitem), interpret=False)
    if menuitem is None:
      # ttyio.echo("Menu.resolverequires.180: menuitem is None.")
      raise ValueError

    requires = menuitem["requires"] if "requires" in menuitem else ()
    if len(requires) == 0:
      # ttyio.echo("Menu.resolverequires.140: len(requires) == 0")
      return True

    for r in requires:
#      ttyio.echo("Menu.resolverequires.120: r=%r" % (r), level="debug")
      m = self.find(r)
      if m is None:
#        ttyio.echo("Menu.resolverequires.140: self.find(%r) returned None, returning False." % (r))
        return False
      if m is False:
#        ttyio.echo("Menu.resolverequires.160: self.find(%r) returned False, returning False." % (r))
        return False

      if "result" in m:
        if m["result"] is False:
#          ttyio.echo("Menu.resolverequires.160: m.result is False")
          return False
      else:
#        ttyio.echo("Menu.resolverequires.200: menuitem.result does not exist, returning False")
        return False
#    ttyio.echo("Menu.resolverequires.220: returning True")
    return True

  def display(self):
    terminalwidth = ttyio.getterminalwidth()
    w = terminalwidth - 7

    setarea(self.area)

    maxlen = 0
    for i in self.items:
          l = len(i["label"])
          if l > maxlen:
              maxlen = l

    ttyio.echo("{f6} {var:engine.menu.cursorcolor}{var:engine.menu.color}%s{/all}" % (" "*(terminalwidth-2)), wordwrap=False)
    if self.title is None or self.title == "":
      ttyio.echo(" {var:engine.menu.cursorcolor}{var:engine.menu.color} {var:engine.menu.boxcharcolor}{acs:ulcorner}{acs:hline:%d}{var:engine.menu.boxcharcolor}{acs:urcorner}{var:engine.menu.color}  {/all}" % (terminalwidth - 7), wordwrap=False)
    else:
      ttyio.echo(" {var:engine.menu.cursorcolor}{var:engine.menu.color} {var:engine.menu.boxcharcolor}{acs:ulcorner}{acs:hline:%d}{acs:urcorner}{var:engine.menu.color}  {/all}" % (terminalwidth - 7), wordwrap=False)
      ttyio.echo(" {var:engine.menu.cursorcolor}{var:engine.menu.color} {var:engine.menu.boxcharcolor}{acs:vline}{var:engine.menu.titlecolor}%s{/all}{var:engine.menu.boxcharcolor}{acs:vline}{var:engine.menu.shadowcolor} {var:engine.menu.color} {/all}" % (self.title.center(terminalwidth-7)), wordwrap=False)
      ttyio.echo(" {var:engine.menu.cursorcolor}{var:engine.menu.color} {var:engine.menu.boxcharcolor}{acs:ltee}{acs:hline:%d}{acs:rtee}{var:engine.menu.shadowcolor} {var:engine.menu.color} {/all}" % (terminalwidth - 7), wordwrap=False)

    ch = ord("A")
    options = ""
    for m in self.items:
      if "result" in m:
        result = m["result"]
        resultbuf = ""
        if type(result) == tuple:
          r, s = result
          if type(s) == str:
            resultbuf = s
          elif (type(s) == tuple or type(s) == list) and len(s) > 0:
            resultbuf = " ".join(s)
        elif type(result) == bool:
          resultbuf = "%r" % (result)
        else:
          resultbuf = "!*!"
      else:
        resultbuf = "**"

#      ttyio.echo("resultbuf=%r" % (resultbuf))

      requires = m["requires"] if "requires" in m else ()

#      if len(requires) == 0:
#        requiresbuf = ""
#      else:
#        requiresbuf = "(requires: %r)" % (oxfordcomma(requires))

      name = m["name"] if "name" in m else None
      if self.resolverequires(m) is True:
        ttyio.setvariable("engine.menu.ic", "{var:engine.menu.itemcolor}")
      else:
        ttyio.setvariable("engine.menu.ic", "{var:engine.menu.disableditemcolor}")
#        buf = "[%s] %s %s %s" % (chr(ch), m["label"], result, requiresbuf)
#        ttyio.echo(" {black}{bgblue} {lightblue}{acs:vline}{bgcyan}{black} %s {bgblue}{lightblue}{acs:vline}{bgblack} {bgblue} {/all}" % (buf.ljust(terminalwidth-9)), wordwrap=False)
#      else:
#        buf = "[%s] %s %s %s" % (chr(ch), m["label"], result, requiresbuf)

#        ttyio.echo(" {black}{bgblue} {lightblue}{acs:vline}{bgcyan}{black} {bggray}{white}%s {bgblue}{lightblue}{acs:vline}{bgblack} {bgblue} {/all}" % (buf.ljust(terminalwidth-9)), wordwrap=False)

      buf = "[%s] %s" % (chr(ch), m["label"].ljust(maxlen))
      if "description" in m:
        buf += " %s" % (m["description"])
      if "requires" in m and len(m["requires"]) > 0:
        buf += " (requires: %s)" % (oxfordcomma(requires))
      if "result" in m:
        buf += " (result: %s)" % (m["result"])

      strippedbuf = ttyio.interpretmci(buf, strip=True)
      ttyio.echo(" {var:engine.menu.cursorcolor}{var:engine.menu.color} {var:engine.menu.boxcharcolor}{acs:vline}{var:engine.menu.ic}%s {/all}{var:engine.menu.boxcharcolor}{acs:vline}{var:engine.menu.shadowcolor} {var:engine.menu.color} {/all}" % (buf.ljust(terminalwidth-8))) # , " "*(terminalwidth-8)), wordwrap=False)

      options += chr(ch)
      ch += 1

    # ttyio.echo(" {white}{bggray} {black}{acs:vline}%s {black}{acs:vline}{bgblack} {bggray} {/all}" % (" "*(terminalwidth-8)), wordwrap=False)

    ttyio.echo(" {var:engine.menu.color} {var:engine.menu.boxcharcolor}{acs:vline}{var:engine.menu.itemcolor}%s {var:engine.menu.boxcharcolor}{acs:vline}{var:engine.menu.shadowcolor} {var:engine.menu.color} {/all}" % ("[Q] quit".ljust(terminalwidth-8)), wordwrap=False)
    options += "Q"

    ttyio.echo(" {var:engine.menu.cursorcolor}{var:engine.menu.color} {var:engine.menu.boxcharcolor}{acs:llcorner}{acs:hline:%d}{acs:lrcorner}{var:engine.menu.shadowcolor} {var:engine.menu.color} {/all}" % (terminalwidth-7), wordwrap=False)

    ttyio.echo(" {var:engine.menu.cursorcolor}{var:engine.menu.color}  {var:engine.menu.shadowcolor}%s {var:engine.menu.color} {/all}" % (" "*(terminalwidth-6)), wordwrap=False)
    ttyio.echo(" {var:engine.menu.color}%s{/all}" % (" "*(terminalwidth-2)), wordwrap=False)
    return

  def run(self, prompt="prompt: ", preprompthook=None):
    done = False
    while not done:
      self.display()
      if callable(preprompthook):
        preprompthook(self.args)
      res = self.handle("{var:engine.menu.promptcolor}%s{var:engine.menu.inputcolor}{decsc}" % (prompt))
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

      if i < len(self.items):
        if op == "select":
          ttyio.echo("{decrc}{var:engine.menu.inputcolor}%s: %s{/all}" % (chr(ord('A')+i), self.items[i]["label"]))
  #        ttyio.echo("menu[i]=%r" % (menu[i]), interpret=False, level="debug", interpret=False)
          label = self.items[i]["label"]
          callback = self.items[i]["callback"]
          menuitem = self.items[i]
          if self.resolverequires(menuitem) is False:
            if ttyio.inputboolean("all requirements not resolved. proceed?: ", "N") is False:
              continue

          res = runcallback(self.args, callback, menu=self, label=label) # menuitem=menuitems[i])
          if type(res) == tuple:
            r, s = res
            if type(r) is not bool:
              raise TypeError

            self.items[i]["result"] = r

            if type(s) == str:
              description = s
            elif (type(s) == tuple or type(s) == list) and len(s) > 0:
              description = " ".join(s)
            menuitem["description"] = description
          else:
            self.items[i]["result"] = res
          continue
        elif op == "help":
          m = self.items[i]
          ttyio.echo("{decrc}display help for %s" % (m["label"]))
          if "help" in m:
            ttyio.echo(m["help"]+"{f6:2}")
          else:
            ttyio.echo("{f6}no help defined for this option{f6}")
          continue
      else:
        ttyio.echo("{decrc}Q: Quit{/all}")
        done = True
        break

  def handle(self, prompt="menu: ", default="Q"):
    ttyio.echo("{f6} %s{decsc}{cha}{cursorright:4}{cursorup:%d}{var:engine.menu.cursorcolor}A{cursorleft}" % (prompt, 5+len(self.items)), end="", flush=True)

    res = None
    self.pos = 0
    self.oldpos = 0
    done = False
    while not done:
      ch = ttyio.getch(noneok=False)
      if ch is None:
        time.sleep(0.125)
        continue
      ch = ch.upper()
      self.oldpos = self.pos
      if ch == "Q":
        ttyio.echo("{decrc}{var:engine.menu.inputcolor}Q: Quit{/all}")
        break
      elif ch == "\004":
        raise EOFError
      elif ch == "\014": # ctrl-l (form feed)
        return "KEY_FF"
      elif ch == "KEY_DOWN":
        if self.pos < len(self.items):
          # ttyio.echo("{black}{bggray}%s{cursorleft}{cursordown}" % (chr(ord('A')+pos)), end="", flush=True)
          # ttyio.echo("{var:menu.cursorcolor}{var:menu.boxcolor}%s{cursorleft}{cursordown}" % (chr(ord('A')+pos)), end="", flush=True)
          ttyio.echo("{var:engine.menu.cursorcolor}%s{cursorleft}{cursordown}" % (chr(ord('A')+self.pos)), end="", flush=True)
          self.pos += 1
        else:
          ttyio.echo("{cursorup:%d}" % (self.pos), end="", flush=True)
          self.pos = 0
      elif ch == "KEY_UP":
        if self.pos > 0:
          ttyio.echo("{cursorup}", end="", flush=True)
          self.pos -= 1
        else:
          ttyio.echo("{cursordown:%d}" % (len(self.items)), end="", flush=True)
          self.pos = len(self.items)
      elif ch == "\n":
        # ttyio.echo("pos=%d len=%d" % (pos, len(menu)))
        return ("select", self.pos)
      elif ch == "KEY_HOME":
        if self.pos > 0:
          ttyio.echo("{cursorup:%d}" % (self.pos-1), end="", flush=True)
          self.pos = 0
      elif ch == "KEY_END":
        ttyio.echo("{cursordown:%d}" % (len(self.items)-self.pos), end="", flush=True)
        self.pos = len(self.items)+1
      elif ch == "KEY_LEFT" or ch == "KEY_RIGHT":
        ttyio.echo("{bell}", flush=True, end="")
      elif ch == "Q":
        return ("quit", None)
      elif ch == "?" or ch == "KEY_F1":
        return ("help", self.pos)
      else:
        if len(ch) > 1:
          ttyio.echo("{bell}", end="", flush=True)
          continue
        i = ord(ch) - ord('A')
        if i > len(self.items)-1:
          ttyio.echo("{bell}", end="", flush=True)
          continue
        return ("select", i)
    return None

# @since 20200819
def getmembercredits(args:object, memberid:int=None) -> int:
  dbh = databaseconnect(args)
  sql = "select credits from engine.member where id=%s" 
  dat = (memberid,)
  cur = dbh.cursor()
  cur.execute(sql, dat)
  res = cur.fetchone()
  if res is None:
    return None
  return res["credits"] if "credits" in res else None

def getcurrentmembercredits(args) -> int:
  memberid = getcurrentmemberid(args)
  return getmembercredits(args, memberid)

def getmembername(args:object, memberid:int) -> str:
  dbh = databaseconnect(args)
  sql = "select name from engine.member where id=%s"
  dat = (memberid,)
  cur = dbh.cursor()
  cur.execute(sql, dat)
  res = cur.fetchone()
  if res is not None and "name" in res:
    return res["name"]
  return None
  
def getcurrentmembername(args) -> str:
  currentmemberid = getcurrentmemberid(args)
  return getmembername(args, currentmemberid)

# @since 20200802
def setmembercredits(dbh:object, memberid:int, amount:int):
  if amount is None or amount < 0:
    return None
  # dbh = databaseconnect(args)
  cur = dbh.cursor()
  sql = "update engine.__member set credits=%s where id=%s"
  dat = (amount, memberid)
  return cur.execute(sql, dat)

# @since 20200802
def updatememberattribute(dbh:object, args:object, memberid:int, field:str, amount):
  pass

# @since 20210203
def getcurrentmember(args:object, fields="*") -> dict:
  currentmemberid = getcurrentmemberid(args)
  dbh = databaseconnect(args)
  return getmemberbyid(dbh, currentmemberid, fields)

# @since 20190924
# @since 20210203
def getmemberbyname(dbh:object, args:object, name:str, fields="*") -> dict:
  sql = "select %s from engine.member where name=%%s" % (fields)
  dat = (name,)
  cur = dbh.cursor()
  cur.execute(sql, dat)
  res = cur.fetchone()
  cur.close()
  return res

# @since 20200731
def getmemberbyid(dbh:object, memberid:int, fields="*") -> dict:
  sql = "select %s from engine.member where id=%%s" % (fields)
  dat = (memberid,)
  cur = dbh.cursor()
  cur.execute(sql, dat)
  res = cur.fetchone()
  cur.close()
  return res

def pluralize(amount:int, singular:str, plural:str, quantity=True) -> str:
  if amount is None or amount == 0:
    return "no %s" % (plural)
  if quantity is True:
    if amount == 1:
      return "%s %s" % (amount, singular)
    buf = "{:n}".format(amount)
    return "%s %s" % (buf, plural)
  if amount == 1:
    return singular
  else:
    return plural

def startsession():
  pass

def hr(color="{var:engine.title.hrcolor}", chars="-=", width=None):
  if width is None:
    width = ttyio.getterminalwidth()
  buf = color+"{acs:hline:%d}{/all}" % (width-1)
  return buf
  
  charslen = len(chars)
  hr = " "*1 # charslen

  if color != "":
    hr += color
  hr += chars*((width//charslen)-charslen)
#    if color != "":
#        hr += "{/%s}" % (color)
  return hr

# titlecolor = "{reverse}"
# hrcolor = ""
# hrchars = "{acs:hline}"
# llcorner="{acs:llcorner}"
# lrcorner="{acs:lrcorner}"
# ulcorner="{acs:ulcorner}"
# urcorner="{acs:urcorner}"
def title(title:str, titlecolor:str="{var:engine.title.color}", hrcolor:str="{var:engine.title.hrcolor}", hrchars:str="{acs:hline}", llcorner="{acs:llcorner}", lrcorner="{acs:lrcorner}", ulcorner="{acs:ulcorner}", urcorner="{acs:urcorner}", width=None):
  if width is None:
    width = ttyio.getterminalwidth()-2

  ttyio.echo("{/all}%s%s{acs:hline:%s}%s" % (hrcolor, ulcorner, width, urcorner), end="")
  ttyio.echo("{f6}{acs:vline}{/all}%s%s{/all}%s{acs:vline}{/all}" % (titlecolor, title.center(width), hrcolor), end="")
  ttyio.echo("{f6}%s%s{acs:hline:%s}%s{/all}" % (hrcolor, llcorner, width, lrcorner))
  return

# @since 20200928
def postgres_to_python_list(arr:str) -> list:
  arr = arr.strip("}")
  arr = arr.strip("{")
  arr = arr.split(",")
  lst = [a.strip() for a in arr]
  return lst

def getsubnodelist(args, nodeid):
  sql = "select id from engine.node where parentid=%s"
  dat = (nodeid,)
  dbh = databaseconnect(args)
  cur = dbh.cursor()
  cur.execute(sql, dat)
  res = cur.fetchall()
  cur.close()
  return res

# @since 20201228
def buildargdatabasegroup(parser:object, defaults:dict={}, label="database"):
    databasename = defaults["databasename"] if "databasename" in defaults else "zoidweb5"
    databasehost = defaults["databasehost"] if "databasehost" in defaults else "localhost"
    databaseport = defaults["databaseport"] if "databaseport" in defaults else "5432"
    databaseuser = defaults["databaseuser"] if "databaseuser" in defaults else None
    databasepassword = defaults["databasepassword"] if "databasepassword" in defaults else None
    
    group = parser.add_argument_group(label)
    group.add_argument("--databasename", dest="databasename", action="store", default=databasename, type=str, help="database name (default: %(default)r)")
    group.add_argument("--databasehost", dest="databasehost", action="store", default=databasehost, type=str, help="database host (default: %(default)r)")
    group.add_argument("--databaseport", dest="databaseport", action="store", default=databaseport, type=int, help="database port (default: %(default)r)")
    group.add_argument("--databaseuser", dest="databaseuser", action="store", default=databaseuser, type=str, help="database user (default: %(default)r)")
    group.add_argument("--databasepassword", dest="databasepassword", action="store", default=databasepassword, type=str, help="database password (default: %(default)r)")
    return

# @since 20201229
# mode = single, average, mean, list, ....?
def diceroll(sides:int=6, count:int=1, mode:str="single"):
  if mode == "single":
    return random.randint(1, sides)

  result = []
  for x in range(1, count+1):
    result.append(random.randint(1, sides))

  if mode == "list":
    return result
  elif mode == "average":
    avg = 0.0
    total = 0
    for x in result:
      total += x
    return total/len(result)
  elif mode == "median":
    median = 0.0
    # ttyio.echo("result=%r" % (result))
    result.sort()
    # ttyio.echo("result=%r" % (result))
    middle = int(len(result)//2)
    if len(result) % 2 == 1:
      return result[middle]
    else:
      return int((result[middle-1] + result[middle]) / 2.0)
  else:
    return None

# @since 20210222
def initscreen(topmargin=0, bottommargin=0):
  terminalheight = ttyio.getterminalheight()
  # ttyio.echo("initscreen.100: terminalheight=%r" % (terminalheight))
  ttyio.echo("{decsc}{decstbm:%d,%d}{decrc}" % (topmargin, terminalheight-bottommargin))

# @since 20210129
def inittopbar(height:int=1):
  ttyio.echo("{decsc}{decstbm:%d}{decrc}" % (height+1), end="")
  return

# @since 20210129
def updatetopbar(buf:str):
  # terminalwidth = ttyio.getterminalwidth()
  # ttyio.echo("{decsc}{home}%s{decrc}" % (buf.ljust(terminalwidth)), end="")
  ttyio.echo("{decsc}{/all}{home}%s{eraseline}{decrc}" % (buf), wordwrap=False)
  return

# updatebottombar() - imported from bbsengine
# @since 20210222
def updatebottombar(buf:str) -> None:
  terminalheight = ttyio.getterminalheight()
  # ttyio.echo("updatebottombar.100: buf=%r" % (buf), interpret=False, level="debug")
  ttyio.echo("{decsc}{/all}{curpos:%d,0}%s{eraseline}{decrc}" % (terminalheight, buf), wordwrap=False, end="")
  return

def initbottombar(height:int=1):
  terminalheight = ttyio.getterminalheight()
  ttyio.echo("{decsc}{decstbm:0,%d}{decrc}" % (terminalheight-1))

# @since 20210129
def setmemberpassword(dbh, memberid, plaintextpassword):
  cur = dbh.cursor()
  sql = "update engine.__member set password=crypt(%s, gen_salt('bf')) where id=%s"
  dat = (plaintextpassword, memberid)
  cur.execute(sql, dat)
  if cur.rowcount == 0:
    return False
  return True

# @since 20210129
def setmemberattributes(dbh, memberid, attributes, reset=False):
  cur = dbh.cursor()
  if reset is False:
    sql = "update engine.__member set attributes=attributes||%%s where id=%s" % (memberid)
  else:
    sql = "update engine.__member set attributes=%%s where id=%s" % (memberid)

  dat = (Json(attributes),)
  return cur.execute(sql, dat)

# @since 20210220
def insertsig(args, dbh, sig):
  attributes = sig["attributes"] if "attributes" in sig else {}
  sig["attributes"] = Json(attributes)
  sig["datecreated"] = "now()"
  sig["createdbyid"] = getcurrentmemberid(args)
  return insert(dbh, "engine.__sig", sig, returnid=True, primarykey="path", mogrify=False)

# @since 20210220
def updatesig(dbh, path, sig):
  pass

# @since 20210301
# @see https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console
def updateprogress(iteration, total):
  terminalwidth = ttyio.getterminalwidth()
  decimals = 0
  fill = "#"
  length = terminalwidth-20
  percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
  filledLength = length * iteration // total
  bar = fill * filledLength + '.' * (length - filledLength)
  buf = "{lightgreen}Progress [% 3s%%]: [%s]{/fgcolor}" % (percent, bar)
  updatebottombar(buf)
  return

def verifyFileExistsReadable(args, filename):
  filename = os.path.expanduser(filename)
  filename = os.path.expandvars(filename)
  ttyio.echo("filename=%r" % (filename))
  if os.path.exists(filename) is True and os.access(filename, os.R_OK) is True:
    return True
  return False

def verifyFileExistsReadableWritable(args, filename):
  filename = os.path.expanduser(filename)
  filename = os.path.expandvars(filename)
  if args is not None and "debug" in args and args.debug is True:
    ttyio.echo("args=%r filename=%r" % (args, filename))

  if os.path.exists(filename) and os.access(filename, os.W_OK) is True and os.access(filename, os.R_OK) is True:
    return True
  return False

def inputfilename(args, prompt, default, verify=verifyFileExistsReadable, **kw):
  return ttyio.inputstring(prompt, default, verify=verify, **kw)

def runcallback(args:object, callback, **kwargs):
  # ttyio.echo("runcallback.120: kwargs=%r" % (kwargs), interpret=False)
  if callable(callback) is True:
    return callback(args, **kwargs)

# scoping issues
#  func = eval(callback)
#  if callable(func) is True:
#    return func(args, **kwargs)

  s = callback.split(".")
  if len(s) > 1:
    modulepath = ".".join(s[:-1])
    functionname = s[len(s)-1:][0]
  else:
    modulepath = None
    functionname = s[0]

  ttyio.echo("runcallback.160: modulepath=%r functionname=%r" % (modulepath, functionname), level="debug", interpret=False)

  rc = None
  if modulepath is not None:
    try:
        m = importlib.import_module(modulepath)
    except ModuleNotFoundError:
        ttyio.echo("runcallback.180: %s module not found" % (modulepath), level="error")
    else:
        ttyio.echo("runcallback.200: m=%r" % (m), level="debug")
        func = getattr(m, functionname)
        ttyio.echo("runcallback.220: func=%r" % (func), level="debug")
        if callable(func) is True:
            rc = func(args, **kwargs)
  else:
    ttyio.echo("runcallback.240: functionname=%r" % (functionname), level="debug")
    try:
      func = eval(functionname)
      ttyio.echo("runcallback.320: func=%r" % (func))
    except NameError:
      ttyio.echo("runcallback.320: %r not found." % (functionname), level="error")
      return False

    if callable(func) is True:
      ttyio.echo("runcallback.260: callable", level="debug")
      rc = func(args, **kwargs)
    else:
      ttyio.echo("runcallback.280: not callable", level="debug")
      rc = False

  ttyio.echo("runcallback.300: callback completed", level="debug")
  return rc

def inputpassword(prompt:str="password: ", mask="X"):
  buf = ""
  done = False
  while not done:
    ch = ttyio.getch()
#    ttyio.echo("ch=%r" % (ch))
    if ch == "\n":
      done = True
      break
    if len(ch) == 1:
      buf += ch
      ttyio.echo(mask, end="", flush=True)
  # ttyio.echo(buf)
  return buf

# @see https://stackoverflow.com/a/53981846
# @since 20210709 moved from ttyio4
def oxfordcomma(seq: List[Any], sepcolor:str="", itemcolor:str="") -> str:
    """Return a grammatically correct human readable string (with an Oxford comma)."""
    seq = [str(s) for s in seq]

#    ttyio.echo("seq=%r" % (seq))
    if len(seq) == 0:
      return ""

    if len(seq) < 3:
      buf = "%s and %s" % (sepcolor, itemcolor)
      return itemcolor+buf.join(seq) # " and ".join(seq)

    buf = "%s, %s" % (sepcolor, itemcolor)
    return itemcolor+buf.join(seq[:-1]) + '%s, and %s' % (sepcolor, itemcolor) + seq[-1]

readablelist = oxfordcomma

# @see https://gist.github.com/sirpengi/5045885 2013-feb-27 in oftcphp sirpengi
# @since 20140529
# @since 20200719
def collapselist(lst):
    def chunk(lst):
        ret = [lst[0],]
        for i in lst[1:]:
            if ord(i) == ord(ret[-1]) + 1:
                pass
            else:
                yield ret
                ret = []
            ret.append(i)
        yield ret
    chunked = chunk(lst)
    ranges = ((min(l), max(l)) for l in chunked)
    return ", ".join("{0}-{1}".format(*l) if l[0] != l[1] else l[0] for l in ranges)


# @since 20211101
# @see https://code.activestate.com/recipes/137270-use-generators-for-fetching-large-db-record-sets/
def ResultIter(cursor, arraysize=1000):
    'An iterator that uses fetchmany to keep memory usage down'
    while True:
        results = cursor.fetchmany(arraysize)
        if not results:
            break
        for result in results:
            yield result

areastack = []

def setarea(buf, push=True):
  global areastack

  width = ttyio.getterminalwidth()
  updatebottombar("{var:engine.areacolor} %s {/all}" % (buf.ljust(width-2, " ")))
  if push is True:
    areastack.append(buf)
  return

def poparea():
  global areastack

#  ttyio.echo("poparea.120: areastack=%r" % (areastack), interpret=False)
  if len(areastack) < 1:
    return

  width = ttyio.getterminalwidth()

  areastack.pop()
  if len(areastack) > 0:
    buf = areastack[-1]
    updatebottombar("{var:engine.areacolor} %s {/all}" % (buf.ljust(width-2, " ")))
  return
