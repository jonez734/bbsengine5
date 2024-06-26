from __future__ import generators    # needs to be at the top of your module

#
# Copyright (C) 2008-2023 zoidtechnologies.com. All Rights Reserved.
#

import re, os, sys, pwd, time, random, copy, socket, json
import importlib.resources as resource

import psycopg2, psycopg2.extras
from psycopg2.extras import Json
from psycopg2.extensions import parse_dsn, make_dsn

from datetime import datetime, timedelta, tzinfo

import syslog

import argparse
# from argparse import Namespace

import ttyio5 as ttyio

import importlib

from typing import Any, List, NamedTuple

# @since 20220406
def checkeros(args, memberid:int=None) -> bool:
  if memberid is None:
    memberid = getcurrentmemberid(args)

  if checkflag(args, "EROS", memberid) is True and args.eros is True:
    return True
  return False

# @since 20220420
def checkmagic(args, memberid:int=None) -> bool:
  if memberid is None:
    memberid = getcurrentmemberid(args)

  if checkflag(args, "MAGIC", memberid):
    return True
  return False

# @since 20220609
def checksysop(args, memberid:int=None) -> bool:
  if memberid is None:
    memberid = getcurrentmemberid(args)

  if checkflag(args, "SYSOP", memberid) is True:
    return True
  return False

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
                ttyio.echo(f"name {name!r} not in database record, using default", level="warning")
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

  def save(self, updatecredits=False) -> None:
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

def verifyprimarykey(dbh, args: argparse.Namespace, table, primarykey, value) -> bool:
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
  def __init__(self, dbh, args:argparse.Namespace, table, primarykey):
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
    self.matches = []
    for rec in resultiter(cur):
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

def verifyprimarykey(args, table, primarykey, value):
  ttyio.echo("call to zoidbo.primarykey()", level="debug")
  bbsengine.verifyprimarykey(args, table, primarykey, value)
  return

def inputprimarykey(args:argparse.Namespace, table, primarykey, prompt, default, completer=None, verify=None, noneok=False, multi=False, delims=None):
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
    c = completer(args, table, primarykey)
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
      ttyio.echo(f"verify={v!r}", level="debug")
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
    if dbh.closed == 0:
      return databasehandles[dsn]
#    else:
#      ttyio.echo("dbh handle closed")

  dbh = psycopg2.connect(connection_factory=psycopg2.extras.DictConnection, cursor_factory=psycopg2.extras.RealDictCursor, **kw)
  databasehandles[dsn] = dbh
  return dbh

def databaseconnect(args):
#  ttyio.echo(f"databaseconnect.100: args={args!r}", level="debug")
  kw = {}
  if type(args) == dict:
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

# import time as _time

# from http://docs.python.org/release/2.5.2/lib/datetime-tzinfo.html
ZERO = timedelta(0)
HOUR = timedelta(hours=1)

STDOFFSET = timedelta(seconds = -time.timezone)
if time.daylight:
    DSTOFFSET = timedelta(seconds = -time.altzone)
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
        return time.tzname[self._isdst(dt)]

    def _isdst(self, dt):
        tt = (dt.year, dt.month, dt.day,
              dt.hour, dt.minute, dt.second,
              dt.weekday(), 0, -1)
        stamp = time.mktime(tt)
        tt = time.localtime(stamp)
        return tt.tm_isdst > 0

# @since 20120126
def inputdate(prompt, origvalue=None, **kw):
  from getdate import getdate, error

  if origvalue is None:
    buf = ttyio.inputstring(prompt, **kw)
  elif type(origvalue) == int:
    buf = ttyio.inputstring(prompt, datestamp(origvalue), **kw)
  else:
    buf = ttyio.inputstring(prompt, origvalue, **kw)
  
  if buf is None:
    return None

  time.tzset()
#  print(type(buf))
  epochseconds = getdate(buf)
  return datetime.fromtimestamp(epochseconds)

#  try:
#    epoch = getdate(buf)
#  except:
#    return None
#  else:
#    return epoch

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

# @since 20220321
def buildsiglist(sigs:str) -> list:
  if type(sigs) == str:
    sigs = re.split("[, ]", sigs)

  sigs = [s.strip() for s in sigs]
  sigs = [s for s in sigs if s]

  return sigs

# @fix: check access to a given sig (eros.*) @done 20220321
def verifysigpath(args: argparse.Namespace, sigpaths):
  ttyio.echo("bbsengine5.verifysigpath.100: sigpaths=%r" % (sigpaths), level="debug")

  erosflag = checkflag(args, "EROS")
  erosarg = args.eros if 'eros' in args else False
  sql = "select distinct path from engine.sig where path ~ %s"
  if erosflag is False or erosarg is False:
    sql += " and not path ~ 'top.eros.*'"

  dbh = databaseconnect(args)
  cur = dbh.cursor()

#  sql = "select 't' from engine.sig where path=%s"
  sigpaths = buildsiglist(sigpaths)
  for s in sigpaths:
    dat = (s,)
    cur.execute(sql, dat)
    if cur.rowcount == 0:
      ttyio.echo("invalid sig %r" % (s))
      return False

  return True

def inputsig(args: argparse.Namespace, prompt="sig: ", oldvalue="", multiple=True, verify=verifysigpath, **kw):
  ttyio.echo("inputsig entered. multiple=%r verify=%r" % (multiple, verify), level="debug")

  return ttyio.inputstring(prompt, oldvalue, args=args, verify=verify, multiple=multiple, completer=sigcompleter(args), returnseq=True, **kw)

#def getsignamefromid(args, id):
#  if id is None:
#    return None
#
#  dbh = databaseconnect(args)
#  sql = "select name from engine.sig where id=%s"
#  dat = (int(id),)
#  cur = dbh.cursor()
#  cur.execute(sql, dat)
#  res = cur.fetchone()
#  cur.close()
#  dbh.close()
#  if res is not None and "name" in res:
#    return res["name"]
#  return None

def update(dbh, table, key, items:dict, primarykey="id", mogrify=False):
#  ttyio.echo(f"bbsengine5.update.100: items={items!r}", level="debug") # interpret=False)
#  ttyio.echo(f"bbsengine5.update.120: items['attributes']={items['attributes']!r} type={type(items['attributes'])}", level="debug")
  for k, v in items.items():
    if type(items[k]) == dict:
      items[k] = json.dumps(items[k])
    if k == "datecreatedepoch":
      del items[k]

  i = copy.deepcopy(items)
  if primarykey in i:
    del i[primarykey]

  sql = "update %s set " % (table)
  params = []
  dat = []
  for k, v in i.items():
    params.append("%s=%%s" % (k),)
    dat.append(v)

  sql += ", ".join(params)
  sql += " where %s=%%s" % (primarykey)
  dat.append(key)

  cur = dbh.cursor()
  cur.execute(sql, dat)

  if mogrify is True:
    ttyio.echo(cur.mogrify(sql, dat), level="debug")

  cur.close()
  return cur.rowcount

def insert(dbh, table:str, dict, returnid:bool=True, primarykey:str="id", mogrify:bool=False):
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

#  if mogrify is True:
#    ttyio.echo("bbsengine5.insert.100: %r" % (cur.mogrify(sql, dat)), level="debug")
#      ttyio.echo(cur.mogrify(sql, [tuple(v.values() for v in dat)]), level="debug")
  cur.execute(sql, dat)
  if returnid is True:
    res = cur.fetchone()
    if primarykey in res:
      return res[primarykey]
  cur.close()
  return None

def insertnode(dbh, args:argparse.Namespace, node:dict, table:str="engine.__node", returnid:bool=True, primarykey:str="id", mogrify:bool=False):
  node["attributes"] = Json(node["attributes"])
  node["datecreated"] = "now()"
  node["createdbyid"] = getcurrentmemberid(args)
  if args.debug is True:
    ttyio.echo("bbsengine.insertnode.100: node=%r table=%r" % (node, table), level="debug")
  return insert(dbh, table, node, returnid=returnid, primarykey=primarykey, mogrify=mogrify)

def updatenodesigs(dbh, args:argparse.Namespace, nodeid:int, sigpaths, completerdelims=", ", mogrify:bool=False):
  if sigpaths is None or len(sigpaths) == 0:
    return None

  ttyio.echo("bbsengine5.updatenodesigs.100: sigpaths=%r" % (sigpaths), level="debug")
  sigpaths = buildsiglist(sigpaths)
#  if type(sigpaths) == str:
#    sigpaths = re.split("|".join(completerdelims), sigpaths)
#    sigpaths = [s.strip() for s in sigpaths]
#    sigpaths = [s for s in sigpaths if s]
  
  # dbh is first arg
  cur = dbh.cursor()
  sql = "delete from engine.map_node_sig where nodeid=%s"
  dat = (nodeid,)
  if mogrify is True:
    ttyio.echo(cur.mogrify(sql, dat), level="debug")

  cur.execute(sql, dat)
  for sigpath in sigpaths:
    ttyio.echo("bbsengine5.updatenodesigs.100: sigpath=%r" % (sigpath))
    sigmap = { "nodeid": nodeid, "sigpath": sigpath }
    insert(dbh, "engine.map_node_sig", sigmap, returnid=False, mogrify=mogrify)
#  dbh.commit()
  return None

def updatenodeattributes(dbh, args:argparse.Namespace, nodeid:int, attributes:dict, reset:bool=False, table:str="engine.__node", mogrify:bool=False):
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
  if mogrify is True:
    ttyio.echo("updatenodeattributes.100: %r" % (cur.mogrify(sql, dat)), level="debug")
  return cur.execute(sql, dat)

def updatenode(dbh, args:argparse.Namespace, id:int, node:dict, reset=False, mogrify=False):
  node["dateupdated"] = "now()"
  node["updatedbyid"] = getcurrentmemberid(args)
  attr = node["attributes"] if "attributes" in node else {}
  if len(attr) > 0:
    updatenodeattributes(dbh, args, id, attr, reset=reset, mogrify=mogrify)
    del node["attributes"]
  return update(dbh, "engine.__node", id, node, mogrify=mogrify)

# @since 20221114
def setmemberflag(args, flag, value, memberid=None, mogrify=False):
  if memberid is None:
    memberid = getcurrentmemberid(args)
  logentry(f"setmemberflag({flag}, {value}, {memberid})")
  if flag == "AUTHENTICATED":
    return

  sql = "delete from engine.map_member_flag where memberid=%s and name=%s"
  dat = (memberid, flag)
  dbh = databaseconnect(args)
  cur = dbh.cursor()

  if mogrify is True:
    ttyio.echo(cur.mogrify(sql, dat), level="debug")

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
from engine.flag left outer join engine.map_member_flag as mmf on flag.name = mmf.name
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
  if cur.rowcount == 0:
    return None
  res = cur.fetchall()
  cur.close()
#  print "getflag.0: %r" % (type(res))
  if res is not None and len(res) == 1:
    return res[0]["value"]
#    return res[0]
  return None

def updateflag(dbh, flag):
  sql = "update flag set defaultvalue=%s, description=%s where name=%s"
  dat = (flag["defaultvalue"], flag["description"], flag["name"])
  cur = dbh.cursor()
  cur.execute(sql, dat)
  cur.close()
  return

# @since 20210106
def checkflag(args, flag:str, memberid:int=None):
  if memberid is None:
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

def logentry(message, output=True, level=None, priority=syslog.LOG_INFO, stripcommands=False, datestamp=True):
  if level is not None:
    if level == "debug":
      message = "{blue}** debug ** "+message+"{/all}"
    elif level == "warn":
      message = "{yellow}** warn ** "+message+"{/all}"
    elif level == "error":
      message = "{red}** error ** "+message+"{/all}"

  message = ttyio.interpretecho(message, strip=True)
  syslog.syslog(priority, message)

  if output is True:
    ttyio.echo(message, stripcommands=stripcommands, datestamp=datestamp, interpret=False)

  return

def datestamp(t=None, format:str="%Y/%m/%d %I:%M%P %Z (%a)") -> str:
  from getdate import getdate, error

  from dateutil.tz import tzlocal
  from datetime import datetime
  from time import tzset

  # ttyio.echo("bbsengine.datestamp.100: type(t)=%r" % (type(t)), level="debug")

  tzset()

  if type(t) == int or type(t) == float:
    t = datetime.fromtimestamp(t, tzlocal())
  elif t is None:
    t = datetime.now(tzlocal())
  elif type(t) == str:
    epoch = getdate(t)
    t = datetime.fromtimestamp(epoch, tzlocal())

  stamp = t.strftime(format, t.timetuple())
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
  if args.debug is True:
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
def getcurrentmemberlogin(args: argparse.Namespace):
  # membermap = {"jam" : 1}
  loginid = pwd.getpwuid(os.geteuid())[0]

  dbh = databaseconnect(args)
  cur = dbh.cursor()
  sql = "select 1 from engine.member where attributes->>'loginid'=%s"
  dat = (loginid,)
  cur.execute(sql, dat)
  if cur.rowcount == 0:
    return None
  return loginid

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
  def __init__(self, title, items, args=None):
    self.items = items
    self.title = title
    self.args = args
  def __len__(self):
    return len(self.items)
  def __getitem__(self, index):
    return self.items[index]

menuitemresults = {}

class MenuItem(object):
  def __init__(self):
    self.result = None
    self.status = None
    self.description = None
    self.key = None
    self.name = None
    self.enabled = False

  def display(self):
    pass

class MenuItemCheckbox(MenuItem):
  def __init__(self):
    super().__init__()
    self.type = "CHECKBOX"

class MenuItemRadioButton(MenuItem):
  def __init__(self):
    super().__init__()
    self.type = "RADIO"
    self.value = None

class MenuItemTextbox(MenuItem):
  def __init__(self):
    super().__init__()
    self.type = "TEXT"

class Menu(object):
  def __init__(self, title:str, items, args=None, area:str=""):
    self.title = title
    self.items = items
    self.args = args
    self.area = area

  # @see https://stackoverflow.com/questions/11469025/how-to-implement-a-subscriptable-class-in-python-subscriptable-class-not-subsc
  def __getitem__(self, i:int) -> dict:
    return self.items[i]

  def __len__(self) -> int:
    return len(self.items)

  def find(self, name:str) -> bool:
    for m in self.items:
      if "name" in m and name == m["name"]:
        return m
    else:
      return None
    return False

  def resolverequires(self, menuitem) -> bool:
#    ttyio.echo("Menu.resolverequires.160: menuitem=%r" % (menuitem), interpret=False)
    if menuitem is None:
      # ttyio.echo("Menu.resolverequires.180: menuitem is None.")
      raise ValueError

    name = menuitem["name"]
    requires = menuitem["requires"] if "requires" in menuitem else ()
    if len(requires) == 0:
      # ttyio.echo("Menu.resolverequires.140: len(requires) == 0")
      return True
#    ttyio.echo("requires=%r" % (requires,), interpret=False)
    for r in requires:
      if r in menuitemresults:
#        ttyio.echo("menuitemresults[%s]=%r" % (r, menuitemresults[r]), interpet=False)
        if menuitemresults[r] is False or menuitemresults[r] is None:
#          ttyio.echo("returning False")
          return False
      else:
        return False
#    ttyio.echo("returning True")
    return True

    for r in requires:
      m = self.find(r)
      if m is None or m is False:
        return False

      if "result" in m:
        if m["result"] is False:
          return False
      else:
        return False

    return True

  def display(self):
    terminalwidth = ttyio.getterminalwidth()
    w = terminalwidth - 7

#    setarea(self.area)
#    ttyio.setvariable("engine.menu.resultfailedcolor", "{bgred}")

    maxlen = 0
    for i in self.items:
          l = len(i["label"])
          if l > maxlen:
              maxlen = l
#    ttyio.echo("menuitemresults=%r" % (menuitemresults), interpret=False)

#    ttyio.echo("{f6} {var:engine.menu.cursorcolor}{var:engine.menu.color}%s{/all}" % (" "*(terminalwidth-2)), wordwrap=False)
    ttyio.echo(" {var:engine.menu.cursorcolor}{var:engine.menu.color}%s{/all}" % (" "*(terminalwidth-2)), wordwrap=False)
    if self.title is None or self.title == "":
      ttyio.echo(" {var:engine.menu.cursorcolor}{var:engine.menu.color} {var:engine.menu.boxcharcolor}{acs:ulcorner}{acs:hline:%d}{var:engine.menu.boxcharcolor}{acs:urcorner}{var:engine.menu.color}  {/all}" % (terminalwidth - 7), wordwrap=False)
    else:
      ttyio.echo(" {var:engine.menu.cursorcolor}{var:engine.menu.color} {var:engine.menu.boxcharcolor}{acs:ulcorner}{acs:hline:%d}{acs:urcorner}{var:engine.menu.color}  {/all}" % (terminalwidth - 7), wordwrap=False)
      ttyio.echo(" {var:engine.menu.cursorcolor}{var:engine.menu.color} {var:engine.menu.boxcharcolor}{acs:vline}{var:engine.menu.titlecolor}%s{/all}{var:engine.menu.boxcharcolor}{acs:vline}{var:engine.menu.shadowcolor} {var:engine.menu.color} {/all}" % (self.title.center(terminalwidth-7)), wordwrap=False)
      ttyio.echo(" {var:engine.menu.cursorcolor}{var:engine.menu.color} {var:engine.menu.boxcharcolor}{acs:ltee}{acs:hline:%d}{acs:rtee}{var:engine.menu.shadowcolor} {var:engine.menu.color} {/all}" % (terminalwidth - 7), wordwrap=False)

    ch = ord("A")
    options = ""
    status = ""
    if len(self.items) > 0:
      for i in self.items:
        result = i["result"] if "result" in i else None
        if type(result) == tuple:
          result, status = result
        elif type(result) == bool:
          status = "%r" % (result)

        if ((type(status) == tuple or type(status) == list)) and len(status) > 0:
          status = " ".join(status)
        else:
          status = "(invalid type %r)" % (type(result))

        requires = i["requires"] if "requires" in i else ()

        name = i["name"] if "name" in i else None
        if result is False:
          ttyio.setvariable("engine.menu.ic", "{var:engine.menu.resultfailedcolor}")
        else:
          if self.resolverequires(i) is True:
            ttyio.setvariable("engine.menu.ic", "{var:engine.menu.itemcolor}")
          else:
            ttyio.setvariable("engine.menu.ic", "{var:engine.menu.disableditemcolor}")

        buf = "[%s] %s" % (chr(ch), i["label"].ljust(maxlen))
        if "description" in i:
          description = i["description"]
          # descriptionlen = len(ttyio.interpretmci(description, strip=True))
          buf += " %s" % (i["description"])
        if "requires" in i and len(i["requires"]) > 0:
          buf += " (requires: %s)" % (oxfordcomma(requires))
        if "result" in i:
          result = i["result"]
          if result is True:
            buf += " PASS"
          elif result is False:
            buf += " FAIL"
#          buf += " (result: %s)" % (i["result"])

#        strippedbuf = ttyio.interpretmci(buf, strip=True)
        ttyio.echo(" {var:engine.menu.cursorcolor}{var:engine.menu.color} {var:engine.menu.boxcharcolor}{acs:vline}{var:engine.menu.ic}%s {/all}{var:engine.menu.boxcharcolor}{acs:vline}{var:engine.menu.shadowcolor} {var:engine.menu.color} {/all}" % (buf.ljust(terminalwidth-8))) # , " "*(terminalwidth-8)), wordwrap=False)

        options += chr(ch)
        ch += 1

    ttyio.echo(" {var:engine.menu.color} {var:engine.menu.boxcharcolor}{acs:vline}{var:engine.menu.itemcolor}%s {var:engine.menu.boxcharcolor}{acs:vline}{var:engine.menu.shadowcolor} {var:engine.menu.color} {/all}" % ("[Q] quit".ljust(terminalwidth-8)), wordwrap=False)
    options += "Q"

    ttyio.echo(" {var:engine.menu.cursorcolor}{var:engine.menu.color} {var:engine.menu.boxcharcolor}{acs:llcorner}{acs:hline:%d}{acs:lrcorner}{var:engine.menu.shadowcolor} {var:engine.menu.color} {/all}" % (terminalwidth-7), wordwrap=False)

    ttyio.echo(" {var:engine.menu.cursorcolor}{var:engine.menu.color}  {var:engine.menu.shadowcolor}%s {var:engine.menu.color} {/all}" % (" "*(terminalwidth-6)), wordwrap=False)
    ttyio.echo(" {var:engine.menu.color}%s{/all}" % (" "*(terminalwidth-2)), wordwrap=False)
    return

  def run(self, prompt="prompt: ", preprompthook=None):
    if len(self.items) == 0:
      ttyio.echo("no menu items defined.")
      return

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
          name = self.items[i]["name"]
          menuitem = self.items[i]
          if self.resolverequires(menuitem) is False:
            if ttyio.inputboolean("{f6}all requirements not resolved. proceed?: ", "N") is False:
              continue

          res = runcallback(self.args, callback, menu=self, label=label) # menuitem=menuitems[i])
          if type(res) == tuple:
            if len(res) == 2:
              r, s = res
              req = None
            if type(r) is not bool:
              raise TypeError
            self.items[i]["result"] = r
            menuitemresults[name] = r
            # ttyio.echo("Menu.run.100: s=%r" % (s), level="debug")
            if type(s) == str:
              description = s
            elif (type(s) == tuple or type(s) == list) and len(s) > 0:
              description = " ".join(s)
            menuitem["description"] = description
          else:
            self.items[i]["result"] = res
            menuitemresults[name] = res
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
    itemcount = len(self.items)
    ttyio.echo("{f6} %s{decsc}{cha}{cursorright:4}{cursorup:%d}{var:engine.menu.cursorcolor}A{cursorleft}" % (prompt, 5+itemcount), end="", flush=True)

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
      elif ch == "KEY_ENTER":
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
def getmembercredits(args, memberid:int=None) -> int:
  if memberid is None:
    memberid = getcurrentmemberid(args)

  dbh = databaseconnect(args)
  sql = "select credits from engine.member where id=%s" 
  dat = (memberid,)
  cur = dbh.cursor()
  cur.execute(sql, dat)
  res = cur.fetchone()
  if res is None:
    return None
  return res["credits"] if "credits" in res else None

#def getcurrentmembercredits(args:argparse.Namespace) -> int:
#  memberid = getcurrentmemberid(args)
#  return getmembercredits(args, memberid)

def getmembername(args:argparse.Namespace, memberid:int=None) -> str:
  if memberid is None:
    memberid = getcurrentmemberid(args)

  dbh = databaseconnect(args)
  sql = "select name from engine.member where id=%s"
  dat = (memberid,)
  cur = dbh.cursor()
  cur.execute(sql, dat)
  res = cur.fetchone()
  if res is not None and "name" in res:
    return res["name"]
  return None
  
#def getcurrentmembername(args:argparse.Namespace) -> str:
#  currentmemberid = getcurrentmemberid(args)
##  ttyio.echo(f"getcurrentmembername.100: currentmemberid={currentmemberid!r}", level="debug")
#  return getmembername(args, currentmemberid)

# @since 20200802
def setmembercredits(args, memberid:int, amount:int):
  if amount is None or amount < 0:
    return None

  dbh = databaseconnect(args)
  cur = dbh.cursor()
  sql = "update engine.__member set credits=%s where id=%s"
  dat = (amount, memberid)
  return cur.execute(sql, dat)

# @since 20221111
def updatemember(args, member, memberid=None):
  if memberid is None:
    memberid = getcurrentmemberid(args)

  m = buildmemberdict(member)
  dbh = databaseconnect(args)
  update(dbh, "engine.__member", memberid, m, mogrify=True)
  # setmemberflags(args, member["flags"], memberid)
  return

# @since 20210203
def getcurrentmember(args, fields="*") -> dict:
  currentmemberid = getcurrentmemberid(args)
  dbh = databaseconnect(args)
  return getmemberbyid(dbh, currentmemberid, fields)

# @since 20190924
# @since 20210203
def getmemberbyname(dbh:object, args:argparse.Namespace, name:str, fields="*") -> dict:
  sql = "select %s from engine.member where name=%%s" % (fields)
  dat = (name,)
  cur = dbh.cursor()
  cur.execute(sql, dat)
  res = cur.fetchone()
  cur.close()
  return buildmemberdict(res)

# @since 20200731
def getmemberbyid(dbh:object, memberid:int, fields="*") -> dict:
  sql = "select %s from engine.member where id=%%s" % (fields)
  dat = (memberid,)
  cur = dbh.cursor()
  cur.execute(sql, dat)
  res = cur.fetchone()
  cur.close()
  return buildmemberdict(res)

def pluralize(amount:int, singular:str, plural:str, quantity=True, emoji:str="") -> str:
  if amount is None or amount == 0:
    if quantity is True:
      return "no %s%s" % (emoji, plural)
    return plural

  if quantity is True:
    if amount == 1:
      return "%s%s %s" % (emoji, amount, singular)
    buf = "{:n}".format(amount)
    return "%s%s %s" % (emoji, buf, plural)
  if amount == 1:
    return "%s%s" % (emoji, singular)
  else:
    return "%s%s" % (emoji, plural)

def startsession():
  pass

def hr(color="{var:engine.title.hrcolor}", chars="-=", width=None):
  if width is None:
    width = ttyio.getterminalwidth()
  return f"{{/all}}{color}{{acs:hline:{width}}}{{/all}}" # % (color, width)

# titlecolor = "{reverse}"
# hrcolor = ""
# hrchars = "{acs:hline}"
# llcorner="{acs:llcorner}"
# lrcorner="{acs:lrcorner}"
# ulcorner="{acs:ulcorner}"
# urcorner="{acs:urcorner}"
def title(title:str, **kw): # hrchar:str="{acs:hline}", llcorner="{acs:llcorner}", lrcorner="{acs:lrcorner}", ulcorner="{acs:ulcorner}", urcorner="{acs:urcorner}", vline="{acs:vline}", width=None, fillchar=" ", center=True):
  if ttyio.getoption("style", "ttyio") == "noansi":
      width = 100
      hline="-"*width
      llcorner="+"
      lrcorner="+"
      ulcorner="+"
      urcorner="+"
      vline="|"
      boxcolor = ""
      titlecolor = ""
  else:
      width = ttyio.getterminalwidth()-2
      hline = f"{{acs:hline:{width}}}"
      llcorner = "{acs:llcorner}"
      lrcorner = "{acs:lrcorner}"
      vline = "{acs:vline}"
      urcorner = "{acs:urcorner}"
      ulcorner = "{acs:ulcorner}"
      boxcolor = "{darkgreen}" # var:engine.title.hrcolor}"
      titlecolor = "{white}{bggray}" # {var:engine.title.color}"

  reset = "{/all}"
  w = int((width-len(title)-4)/2)
  padding = " "*(int(w))
  if w % 2 == 0:
    extra = ""
  else:
    extra = " "

  ttyio.echo(f"{boxcolor}{ulcorner}{hline}{urcorner}", wordwrap=False)
  ttyio.echo(f"{boxcolor}{vline}{reset} {titlecolor}{padding} {title} {padding}{extra}{reset} {boxcolor}{vline}", wordwrap=False)
  ttyio.echo(f"{boxcolor}{llcorner}{hline}{lrcorner}{reset}", wordwrap=False)
  return

  style = ttyio.getoption("style", "ttyio")
  if style == "noansi":
    width = 100
    hrchar = "-"
    llcorner = "+"
    lrcorner = "+"
    ulcorner = "+"
    urcorner = "+"
    vline = "|"
  else:
    width = getterminalwidth()-2

  if width is None:
    width = ttyio.getterminalwidth()-2
#  buf = ttyio.center(title, width)
  buf = title.center(width) # ttyio.center(title, width)
#  b = title.center(width) # ttyio.center(title)

  ttyio.echo("{/all}{var:engine.title.hrcolor}%s{acs:hline:%s}%s" % (ulcorner, width, urcorner), wordwrap=False)
  ttyio.echo("{var:engine.title.hrcolor}{acs:vline}{/all}{var:engine.title.color}%s{/all}{var:engine.title.hrcolor}{acs:vline}{/all}" % (buf), wordwrap=False)
  # ttyio.echo("{f6}{acs:vline}{/all}%s%s{/all}%s{acs:vline}{/all}" % (titlecolor, i.center(width), hrcolor), end="")
  ttyio.echo("{var:engine.title.hrcolor}%s{acs:hline:%s}%s{/all}" % (llcorner, width, lrcorner), wordwrap=False)
  return

# @since 20200928
def postgres_to_python_list(arr:str) -> list:
  arr = arr.strip("}")
  arr = arr.strip("{")
  arr = arr.split(",")
  lst = [a.strip() for a in arr]
  return lst

def getsubnodelist(args: argparse.Namespace, nodeid):
  sql = "select id from engine.node where parentid=%s"
  dat = (nodeid,)
  dbh = databaseconnect(args)
  cur = dbh.cursor()
  cur.execute(sql, dat)
  res = cur.fetchall()
  cur.close()
  return res

# @since 20201228
def buildargdatabasegroup(parentparser:object, defaults:dict={}, label="database options"):
    databasename = defaults["databasename"] if "databasename" in defaults else "zoidweb5"
    databasehost = defaults["databasehost"] if "databasehost" in defaults else "localhost"
    databaseport = defaults["databaseport"] if "databaseport" in defaults else "5432"
    databaseuser = defaults["databaseuser"] if "databaseuser" in defaults else None
    databasepassword = defaults["databasepassword"] if "databasepassword" in defaults else None
    
    group = parentparser.add_argument_group(label)
#    group = argparse.ArgumentParser("database", parents=[parentparser], add_help=False)
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

# @since 20210222 use format strings, set bottommargin to 1
def initscreen(topmargin=0, bottommargin=1):
  ttyio.echo("{f6:3}{cursorup:3}", end="", flush=True)
  initbottombar(height=bottommargin)

#  terminalheight = ttyio.getterminalheight()
#  ttyio.echo(f"{{decsc}}{{decstbm:{topmargin},{terminalheight-bottommargin}}}{{decrc}}") #  % (topmargin, terminalheight-bottommargin)) #  % (topmargin, terminalheight-bottommargin))

  return

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
#  ttyio.echo("updatebottombar.100: buf=%r" % (buf), level="debug")
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
def insertsig(args: argparse.Namespace, dbh, sig, mogrify=False):
  attributes = sig["attributes"] if "attributes" in sig else {}
  sig["attributes"] = Json(attributes)
  sig["datecreated"] = "now()"
  sig["createdbyid"] = getcurrentmemberid(args)
  return insert(dbh, "engine.__sig", sig, returnid=True, primarykey="path", mogrify=mogrify)

# @since 20210220
def updatesig(dbh, path, sig):
  pass

# @since 20210301
# @see https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console
# @since 20240102 copied to bbsengine6
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

def verifyFileExistsReadable(args: argparse.Namespace, filename):
  filename = os.path.expanduser(filename)
  filename = os.path.expandvars(filename)
  ttyio.echo("filename=%r" % (filename))
  if os.path.exists(filename) is True and os.access(filename, os.R_OK) is True:
    return True
  return False

def verifyFileExistsReadableWritable(args: argparse.Namespace, filename):
  filename = os.path.expanduser(filename)
  filename = os.path.expandvars(filename)
  if args is not None and "debug" in args and args.debug is True:
    ttyio.echo("args=%r filename=%r" % (args, filename))

  if os.path.exists(filename) and os.access(filename, os.W_OK) is True and os.access(filename, os.R_OK) is True:
    return True
  return False

def inputfilename(args: argparse.Namespace, prompt, default, verify=verifyFileExistsReadable, **kw):
  path = os.path.expanduser(default)
  path = os.path.expandvars(path)
  dirname = os.path.dirname(path)
  if dirname is not None and dirname != "":
    os.chdir(dirname)
  return ttyio.inputstring(prompt, default, verify=verify, **kw)

def loadmodule(args:object, modulepath:str):
  try:
      m = importlib.import_module(modulepath)
  except ModuleNotFoundError:
      ttyio.echo("loadmodule.180: module %s not found" % (modulepath), level="error")
      raise
  except Exception as e:
      import traceback
      traceback.print_exc(file=sys.stdout)
  return m

def runcallback(args:object, callback, optional=False, **kwargs): # s:argparse.Namespace, callback, argparser=None, **kwargs):
  debug = args.debug if args is not None else False
  if debug is True:
    ttyio.echo("bbsengine5.runcallback.100: args=%r" % (args), level="debug")
    ttyio.echo("runcallback.120: kwargs=%r" % (kwargs), level="debug")# interpret=False)
#  if argparser is not None:
#    args = argparser.parse_args()

  if callback is None:
    if debug is True:
      ttyio.echo("runcallback.140: callback is None", level="debug")
    return None

  if callable(callback) is True:
    if debug is True:
      ttyio.echo("runcallback.160: callback is callable", level="debug")
    return callback(args, **kwargs)

  s = callback.split(".")
  if len(s) > 1:
    modulepath = ".".join(s[:-1])
    funcname = s[len(s)-1:][0]
  else:
    modulepath = s[0] # None
    funcname = "main" # s[0]

  if debug is True:
    ttyio.echo("runcallback.160: modulepath=%r funcname=%r" % (modulepath, funcname), level="debug")

  if modulepath is None:
    try:
      func = eval(funcname)
      ttyio.echo("runcallback.320: func=%r" % (func))
    except NameError:
      ttyio.echo("runcallback.340: %r not found." % (funcname), level="error")
      return None

    if callable(func) is True:
      if debug is True:
        ttyio.echo("runcallback.260: callable", level="debug")
      return func(args, **kwargs)
    else:
      if debug is True:
        ttyio.echo("runcallback.280: not callable", level="debug")
      return None

  m = loadmodule(args, modulepath)
  if debug is True:
    ttyio.echo("runcallback.200: m=%r funcname=%r" % (m, funcname), level="debug")

  try:
    func = getattr(m, funcname)
  except AttributeError:
#    ttyio.echo("runcallback.240: function %s.%s() not found" % (modulepath, funcname))
    return None
  else:
    if debug is True:
      ttyio.echo("runcallback.220: func=%r" % (func), level="debug")
    if callable(func) is True:
      return func(args, **kwargs)

  return None

def inputpassword(prompt:str="password: ", mask="X") -> str:
  buf = ""
  done = False
  ttyio.echo(prompt, end="", flush=True)
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
def oxfordcomma(seq: List[Any], conjunction="and") -> str:
    """Return a grammatically correct human readable string (with an Oxford comma)."""
    if seq is None:
      return None

    seq = [str(s) for s in seq]

#    ttyio.echo("seq=%r" % (seq))
    if len(seq) == 0:
      return ""

    if len(seq) < 3:
      buf = f"{{var:sepcolor}} {conjunction} {{var:valuecolor}}"
      return f"{{var:valuecolor}}{buf.join(seq)}" # itemcolor+buf.join(seq) # " and ".join(seq)

    buf = f"{{var:sepcolor}}, {{var:valuecolor}}"
    return f"{{var:valuecolor}}{buf.join(seq[:-1])}{{var:sepcolor}}, {conjunction} {{var:valuecolor}}{seq[-1]}"

readablelist = oxfordcomma

# @see https://gist.github.com/sirpengi/5045885 2013-feb-27 in oftcphp sirpengi
# @since 20140529
# @since 20200719
# @since 20230502 renamed
def oldrangecollapse(elle:list) -> str:
    def chunk(elle):
        ret = [elle[0],]
        for i in elle[1:]:
            if ord(i) == ord(ret[-1]) + 1:
                pass
            else:
                yield ret
                ret = []
            ret.append(i)
        yield ret
    chunked = chunk(elle)
    ranges = ((min(l), max(l)) for l in chunked)
    return ", ".join("{0}-{1}".format(*l) if l[0] != l[1] else l[0] for l in ranges)

# @since 20230502
# @see https://rosettacode.org/wiki/Range_extraction#Python
def rangecollapse(lst:list):
    'Yield 2-tuple ranges or 1-tuple single elements from list of increasing ints'
    lenlst = len(lst)
    i = 0
    while i < lenlst:
        low = lst[i]
        while i <lenlst-1 and lst[i]+1 == lst[i+1]: i +=1
        hi = lst[i]
        if   hi - low >= 2:
            yield (low, hi)
        elif hi - low == 1:
            yield (low,)
            yield (hi,)
        else:
            yield (low,)
        i += 1


# @since 20230502
def rangeexpand(txt:str) -> list:
  "accepts an str with a range expression, returns a list"
  elle = []
  for r in txt.split(','):
    if '-' in r[1:]:
      r0, r1 = r[1:].split('-', 1)
      elle += range(int(r[0] + r0), int(r1) + 1)
    else:
      elle.append(int(r))
  return list(set(elle))

def printr(ranges):
    print( ','.join( (('%i-%i' % r) if len(r) == 2 else '%i' % r)
                     for r in ranges ) )

# @since 20211101
# @see https://code.activestate.com/recipes/137270-use-generators-for-fetching-large-db-record-sets/
def resultiter(cursor, arraysize=1000, filterfunc=None, **kw:dict):
    'An iterator which accepts a psycopg2 cursor to keep memory usage down'
    while True:
        results = cursor.fetchmany(arraysize)
        if not results:
            break
        for result in results:
          if filterfunc is None:
            yield result
          elif callable(filterfunc) is True and filterfunc(result, **kw) is True:
            yield result

areastack = []

def setarea(left, right=None, stack=False):
  global areastack

  terminalwidth = ttyio.getterminalwidth()-2

  if callable(left):
    leftbuf = left()
  elif type(left) == str:
    leftbuf = left
  else:
    leftbuf = type(left) # "ERROR"

  l = ttyio.interpretecho(leftbuf, strip=True)

  if callable(right):
    rightbuf = right()
  elif type(right) == str:
    rightbuf = right
  elif right is None:
    rightbuf = ""
  else:
    ttyio.echo("setarea.100: type(right)=%r" % (right), level="debug")
    rightbuf = "ERROR" # type(right)
  r = ttyio.interpretecho(rightbuf, strip=True)
  t = terminalwidth - len(r) - 4
  leftbuf = leftbuf[:t] + (leftbuf[t:] and '...')

#  ttyio.echo("r=%r rightbuf=%r" % (r, rightbuf), interpret=False)

#  buf = "%s%s" % (ttyio.ljust(leftbuf, terminalwidth-len(r)), rightbuf) # leftbuf.ljust(terminalwidth-len(r), " "), rightbuf)
  buf = " %s%s " % (leftbuf.ljust(terminalwidth-len(r)), rightbuf)
  #ttyio.ljust(leftbuf, terminalwidth-len(r)), rightbuf) # leftbuf.ljust(terminalwidth-len(r), " "), rightbuf)
  updatebottombar("{var:areacolor}%s{/all}" % (buf))
  if stack is True:
    areastack.append(buf)
  return

def poparea():
  global areastack

#  ttyio.echo("poparea.120: areastack=%r" % (areastack), level="debug") # interpret=False)
  if len(areastack) == 0:
    return

  terminalwidth = ttyio.getterminalwidth()

  if len(areastack) > 0:
    buf = areastack.pop()
#    ttyio.echo("poparea.140: buf=%r" % (buf), level="debug")
#    buf = areastack[-1]
    if buf != "":
      updatebottombar("{var:areacolor}%s{/all}" % (buf.ljust(terminalwidth-2, " ")))
#    areastack.pop()

  return

# @since 20201013
class genericInputCompleter(object):
  def __init__(self:object, args:argparse.Namespace, tablename:str, primarykey:str):
    self.matches = []
    self.dbh = databaseconnect(args)
    self.debug = args.debug if "debug" in args else False
    self.tablename = tablename
    self.primarykey = primarykey

    if self.debug is True:
      ttyio.echo("init genericInputCompleter object", level="debug")

  @classmethod
  def getmatches(self, text):
    if self.debug is True:
      ttyio.echo("genericInputCompleter.110: called getmatches()", level="debug")
    sql = "select %s from %s where %s ilike %%s" % (self.primarykey, self.tablename, self.primarykey)
    dat = (text+"%",)
    cur = self.dbh.cursor()
    if self.debug is True:
      ttyio.echo("getmatches.140: mogrify=%r" % (cur.mogrify(sql, dat)), level="debug")
    cur.execute(sql, dat)
    res = cur.fetchall()
    if self.debug is True:
      ttyio.echo("getmatches.130: res=%r" % (res), level="debug")
    matches = []
    for rec in res:
      matches.append(rec[self.primarykey])

    cur.close()

    if self.debug is True:
      ttyio.echo("getmatches.120: matches=%r" % (matches), level="debug")

    return matches

  @classmethod
  def complete(self:object, text:str, state):
    if state == 0:
      self.matches = self.getmatches(text)

    return self.matches[state]
# @since 20220509
def buildargcommon(parents=[]):
    argparser = argparse.ArgumentParser("common", parents=parents, add_help=False)
    argparser.add_argument("--verbose", action="store_true", dest="verbose")
    argparser.add_argument("--debug", action="store_true", dest="debug")
    return argparser

def verifyfloat(args, buf):
  ttyio.echo("verifyfloat.100: buf=%s" % (buf), level="debug")
  res = False
  try:
    res = float(buf)
  except ValueError:
    ttyio.echo("value error converting to float", level="debug")
    res = False
  else:
    res = True

  ttyio.echo("verifyfloat.1110: res=%s" % (res))
  return res

def inputfloat(args, prompt, default=None, strip=None, verify=verifyfloat, noneok=True):
  while True:
    buf = ttyio.inputstring(prompt, default, noneok=noneok)
    ttyio.echo("inputfloat.14: buf=%r strip=%r" % (buf, strip), level="debug")
    if strip is not None:
      buf = buf.strip(strip)
      ttyio.echo("stripped. strip=%r" % (strip), level="debug")
    ttyio.echo("inputfloat.12: buf=%r" % (buf), level="debug")
    if buf == "" or buf is None:
      if noneok is True:
        res = None
        break
      else:
        res = default
        break
    elif callable(verify) is True:
      if verify(args, buf) is True:
        res = float(buf)
        break
  # if opts.debug is True:
  ttyio.echo("inputfloat.10: res=%r" % (res), level="debug")
  return res

# @since 20220724
# @see https://stackoverflow.com/a/66950540
def buildfilepath(*args) -> str:
  q = []
  for a in args:
#    ttyio.echo("buildfilepath.100: a=%r" % (a), level="debug")
    p = os.path.relpath(os.path.normpath(os.path.join("/", a)), "/")
    p = os.path.expandvars(p)
    p = os.path.expanduser(p)
    q.append(p)
  return "/".join(q)

def pager(f, **kw):
  width = kw["width"] if "width" in kw else ttyio.getterminalwidth()
  height = kw["height"] if "height" in kw else ttyio.getterminalheight()
  indent = kw["indent"] if "indent" in kw else ""

  row = 1
  for line in f:
    ttyio.echo(line, wordwrap=True)
    line = line.replace("\n", "{f6}")
    row += ttyio.interpretecho(line, width=width).count("\n")
    if row >= height-2:
      ch = ttyio.inputboolean("{curpos:%d,1}{eraseline}{var:promptcolor}more? [{var:currentoptioncolor}Y{var:optioncolor}n{var:promptcolor}]: {var:inputcolor}" % (height), "Y")
      ttyio.echo("{cursorup}{eraseline}{/all}", end="")
      if ch is False:
        break
      else:
        row = 1
    ttyio.echo(line, wordwrap=True, end="", width=width, indent=indent)
  return

# @since 20220718
def filedisplay(filename, **kw) -> None: #more=True, width=None) -> None:
  more = kw["more"] if "more" in kw else True
  width = kw["width"] if "width" in kw else None
  indent = kw["indent"] if "indent" in kw else ""
  args = kw["args"] if "args" in kw else None

#  ttyio.echo("filename=%r" % (filename), level="debug")
  if width is None:
    width = ttyio.getterminalwidth()

  height = ttyio.getterminalheight()-1
  ttyio.echo("filedisplay.100: filename=%r type=%r" % (filename, type(filename)), level="debug")
  with filename as f:
    for line in f:
      ttyio.echo(line)

#    pager(f, width=width, height=height, indent=indent)
  ttyio.echo("{/all}{f6}")

#  ttyio.inputchar("{curpos:%d,1}{eraseline}{var:promptcolor}press enter key to end: {var:inputcolor}" % (height), "", noneok=True)
#  ttyio.echo("{cursorhpos:1}{eraseline}{/all}")

# @since 20220826
def checkmodule(args, module, op="run", buildargs=False, **kw):
  if args.debug is True:
    ttyio.echo(f"bbsengine.checkmodule.120: module={module!r}", level="debug")

  try:
    m = importlib.import_module(module)
  except Exception as e:
    if args.debug is True:
      ttyio.echo(repr(e), level="error")
    return False

  if args.debug is True:
    ttyio.echo("bbsengine5.checkmodule.100: m=%r" % (m), level="debug")

  # required
  if (hasattr(m, "init") and callable(m.init)) is False:
    if args.debug is True:
      ttyio.echo("no init function", level="warn")
    return False

  # optional
  if hasattr(m, "access") is False:
    if args.debug is True:
      ttyio.echo("no access function, returning True anyway")
    return True
  if (hasattr(m, "access") and callable(m.access)) is False:
    if args.debug is True:
      ttyio.echo("no callable access function", level="debug")
    return False

  if m.access(args, op) is True:
    if args.debug is True:
      ttyio.echo("access check passed", level="debug")
  else:
    ttyio.echo("access check failed", level="error")
    return False

  if (hasattr(m, "buildargs") and callable(m.buildargs)) is False:
    if args.debug is True:
      ttyio.echo("no callable buildargs function", level="debug")
    if buildargs is True:
      return False

  # required
  if (hasattr(m, "main") and callable(m.main)) is False:
    ttyio.echo("no main function", level="error")
    return False

  return True

# @since 20220727
def runmodule(args, module, **kwargs):
  buildargs = kwargs["buildargs"] if "buildargs" in kwargs else True
  if checkmodule(args, module, buildargs=buildargs) is False:
    ttyio.echo("permission denied", level="error")
    return False

  if args.debug is True:
    ttyio.echo("bbsengine5.runmodule.100: args=%r" % (args), level="debug")

  res = runcallback(args, module + ".init", **kwargs)
  if args.debug is True:
    ttyio.echo("%s.init() result=%r" % (module, res), level="debug")

  if buildargs is True:
    argv = kwargs["argv"] if "argv" in kwargs else []
    if args.debug is True:
      ttyio.echo("bbsengine5.runmodule.120: argv=%r" % (argv), level="debug")
    prgargparser = runcallback(args, module + ".buildargs", **kwargs)
    if prgargparser is not None:
      try:
        argv = [a.strip() for a in argv[1:]]
        prgargs = prgargparser.parse_args(argv) # argv[1:])
#        prgargs = [s.strip() for s in prgargs]
      except SystemExit:
        return
      except argparse.ArgumentError:
        ttyio.echo("argument error", level="error")
        return

      if args.debug is True:
        ttyio.echo("bbsengine.runmodule.220: prgargs=%r" % (prgargs), level="debug")

      return runcallback(prgargs, module+".main", **kwargs)
#  else:
#    res = runcallback(args, module+".main", **kwargs)
  res = runcallback(args, module+".main", **kwargs)

  if args.debug is True:
    ttyio.echo("%s.main() result=%r" % (module, res), level="debug")
  return res

# @since 20220828
def runsubmodule(args, module, **kw):
  if "buildargs" in kw:
    buildargs = kw["buildargs"]
    del kw["buildargs"]
  else:
    buildargs = False
  return runmodule(args, module, buildargs=buildargs, **kw)

def init(args, **kw):
#  logging.config.basicConfig()
#  logger = logging.get_logger("bbsengine5")
#  if args.debug is True:
#    logger.setLevel(logging.DEBUG)

  dbh = databaseconnect(args)

  if "REMOTEHOST" in os.environ:
    address = os.environ["REMOTEHOST"]
    hostname = socket.gethostbyaddr(address)[0]
  else:
    address = "127.0.0.1"
    hostname = socket.gethostname()

  d = {}
  d["memberid"] = getcurrentmemberid(args)
  d["address"] = address
  d["hostname"] = hostname
  d["datestamp"] = "now()"

  insert(dbh, "engine.map_memberid_inetaddr", d, mogrify=True, returnid=False)

  dbh.commit()

  return True

# moved from postoffice
# @since 20221001
def getencryptedpassword(args, plaintextpassword:str) -> str:
  ttyio.echo(f"getencryptedpassword.100: plaintextpassword={plaintextpassword!r}", level="debug")
  sql = "select crypt(%s, gen_salt('md5'))" # previously 'bf' which does not work with dovecot
  dat = (plaintextpassword,)
  dbh = databaseconnect(args)
  cur = dbh.cursor()
  cur.execute(sql, dat)
  if cur.rowcount == 0:
    return None

  res = cur.fetchone()
  return res["crypt"]

# copied from socrates
# @since 20221030
def runtexteditor(body="", restricted=False):
  import tempfile

  fn = tempfile.mktemp()

  try:
    fp = open(fn, "w")
  except PermissionError:
    ttyio.echo(f"permission error trying to open {fn!r}", level="error")
    return None
  else:
    with fp:
      fp.writelines(body)
  finally:
    fp.close()

  if "VISUAL" in os.environ:
      editor = os.environ["VISUAL"]
  elif "EDITOR" in os.environ:
      editor = os.environ["EDITOR"]
  else:
      editor = "joe"

  os.system("%s %s" % (editor, fn))

  if os.access(fn, os.F_OK|os.R_OK):
      fp = open(fn, "r")
      body = fp.readlines()
      fp.close()
  else:
      ttyio.echo(f"permission denied trying to read from {fn!r}", level="error")
      return None

  return "".join(body)

#
# @since 20140831 bbsengine5.php
# @since 20221107 bbsengine5.py
#
def checkpassword(args, plaintext, memberid=None):
  if memberid is None:
    memberid = getcurrentmemberid(args)

  logentry(f"checkpassword.200: memberid={memberid!r}")
  dbh = databaseconnect(args)
  sql = "select 't' as correct from engine.member where id=%s and crypt(%s, password) = password"
  dat = (memberid, plaintext)
  cur = dbh.cursor()
  cur.execute(sql, dat)
  ttyio.echo(f"checkpassword.180: {cur.mogrify(sql, dat)}", level="debug")
  if cur.rowcount == 0:
    ttyio.echo("checkpassword.140: no rows returned", level="debug")
    return False

  res = cur.fetchone()
  ttyio.echo(f"checkpassword.160: res={res!r}", level="debug")
  if res["correct"] == "t":
    return True
  return False

def getmemberidfromloginid(args, loginid:str) -> int:
  dbh = databaseconnect(args)
  cur = dbh.cursor()
  sql = "select id from engine.member where loginid=%s"
  dat = (loginid,)
  cur.execute(sql, dat)
  ttyio.echo(f"getmemberidfromloginid.140: mogrify={cur.mogrify(sql, dat)}", level="debug")
  if cur.rowcount == 0:
    ttyio.echo(f"getmemberidfromloginid.120: rowcount is zero", level="debug")
    return False
  res = cur.fetchone()
  ttyio.echo(f"getmemberidfromloginid.100: res={res!r}", level="debug")
  return res["id"]

def setpassword(args, plaintextpassword: str, memberid:int=None) -> None:
  if memberid is None:
    memberid = getcurrentmemberid(args)

  dbh = databaseconnect(args)
  m = {}
  m["password"] = getencryptedpassword(args, plaintextpassword)

  update(dbh, "engine.__member", memberid, m, mogrify=True)
  return None

# @since 20221108 us election day
def getmemberidfromname(args, name:str) -> int:
  dbh = databaseconnect(args)
  cur = dbh.cursor()
  sql = "select id from engine.member where name=%s or loginid=%s"
  dat = (name, name)
  cur.execute(sql, dat)
  ttyio.echo(f"getmemberidfromname.140: mogrify={cur.mogrify(sql, dat)}", level="debug")
  if cur.rowcount == 0:
    if args.debug is True:
      ttyio.echo(f"getmemberidfromloginid.120: rowcount is zero", level="debug")
    return False
  res = cur.fetchone()
  if args.debug is True:
    ttyio.echo(f"getmemberidfromloginid.100: res={res!r}", level="debug")
  return res["id"]

# @since 20221109
def getflags(args, memberid:int) -> dict:
  flags = {}
  if (memberid > 0):
    flags["AUTHENTICATED"] = { "value": True, "description": "Authenticated"}
  else:
    flags["AUTHENTICATED"] = { "value": False, "description": "Authenticated"}

  sql = """
select
  flag.name,
  coalesce(map_member_flag.value, flag.defaultvalue) as value,
  flag.description
from engine.flag
left outer join engine.map_member_flag on flag.name = engine.map_member_flag.name and engine.map_member_flag.memberid=%s
"""
  dat = (memberid,)
  dbh = databaseconnect(args)
  cur = dbh.cursor()
  cur.execute(sql, dat)
  ttyio.echo(f"cur.rowcount={cur.rowcount}", level="debug")
  if cur.rowcount > 0:
    res = cur.fetchall()
    ttyio.echo(f"res={res!r}", level="debug")
    for rec in res:
      k = rec["name"]
      v = rec["value"]
      d = rec["description"]
      if v == "t" or v == "1" or v == True:
        flags[k] = {"value": True, "description": d}
      else:
        flags[k] = {"value": False, "description": d}

  return flags;

# @since 20221112
def setmemberflags(args, flags, memberid=None):
  if memberid is None:
    memberid = getcurrentmemberid(args)
  for name, value in flags.items():
    v = value["value"]
    setmemberflag(args, name, v, memberid)
  return

# @since 20221113
def buildmemberdict(res):
  m = {}
  for k, v in res.items():
    if k in ("datecreatedepoch", "dateapprovedepoch", "dateupdatedepoch", "lastloginepoch", "flags"):
      continue
    if type(v) == dict:
      m[k] = json.dumps(v)
      continue
    m[k] = v
  return m

# @since 20230504
def inputpassword(prompt, mask="*", **kw):
  return ttyio.inputstring(prompt, mask=mask, **kw)
