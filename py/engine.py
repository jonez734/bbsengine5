import argparse
import json

import ttyio5 as ttyio
import bbsengine5 as bbsengine

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

def email(args, **kwargs):
  def _edit(args, **kwargs):
    if "prompt" in kwargs:
      prompt = kwargs["prompt"]
    else:
      prompt = "email._edit"

    attributes = {}
    if "attributes" in kwargs:
      attributes = kwargs["attributes"]
    done = False
    while not done:
      if "address" in attributes:
        address = attributes["address"]
        if address is not None:
          ttyio.echo("[A]ddress: %s" % (address))
      else:
        ttyio.echo("[A]ddress")
      ttyio.echo("[P]assword")
      if "status" in attributes:
        status = attributes["status"]
        ttyio.echo("[S]tatus: %s" % (status), end="")
        if status == "suspend" and "suspenduntil" in attributes:
          suspenduntil = attributes["suspenduntil"]
          ttyio.echo(" until: %s" % (bbsengine.datestamp(suspenduntil)))
        else:
          ttyio.echo()
      else:
          ttyio.echo("[S]tatus")
      ttyio.echo("[H]ost")
      ttyio.echo("{f6}[Q]uit")
      ch = ttyio.inputchar("%s [AEDSQ]: " % (prompt), "ASMHQ", "Q")
      if ch == "Q":
        ttyio.echo("quit")
        done = True
        break
      elif ch == "P":
        p = bbsengine.inputpassword("password: ", mask="X")
        attributes["password"] = p
      elif ch == "A":
        if "address" in attributes:
          address = attributes["address"]
        else:
          address = None
        attributes["address"] = ttyio.inputstring("address: ", address, noneok=True)
      elif ch == "H":
        if "host" in attributes:
          default = attributes["host"]
        else:
          default = "merlin.zoidtechnologies.com"
        host = ttyio.inputstring("host: ", default)
        attributes["host"] = host

      elif ch == "S":
        ch = ttyio.inputchar("Status [S]uspend [A]ctive: ", "SA", noneok=True)
        if ch == "S":
          suspenduntil = bbsengine.inputdate("Suspend until: ")
          attributes["suspenduntil"] = suspenduntil
          attributes["status"] = "suspend"
        elif ch == "A":
          ttyio.echo("Active")
          attributes["status"] = "active"
          if "suspenduntil" in attributes:
            del attributes["suspenduntil"]

    ttyio.echo("_editemail.100: attributes=%r" % (attributes), interpret=False)
    return
  def delete():
    pass
  def edit():
    pass
  def add():
    newattributes = _editemail(args, attributes={}, prompt="email.add")
    ttyio.echo("email.add.100: newattributes=%r" % (newattributes), interpret=False)
    return
  def summary():
    pass

  done = False
  while not done:
    bbsengine.title("email")
    ttyio.echo("[A]dd")
    ttyio.echo("[E]dit")
    ttyio.echo("[D]elete")
    ttyio.echo("[S]ummary")
    ttyio.echo("{f6}[Q]uit")
    ch = ttyio.inputchar("email [AEDSQ]: ", "AEDSQ", "Q")
    if ch == "Q":
      ttyio.echo("Quit")
      done = True
      break
    elif ch == "A":
      ttyio.echo("Add")
      add()
    elif ch == "E":
      ttyio.echo("Edit")
      edit()
    elif ch == "D":
      ttyio.echo("Delete")
      delete()
    elif ch == "L":
      ttyio.echo("List")
      summary()

  return

def member(args, **kwargs):
    def buildrecord(row):
      rec = {}
      for k in ("credits", "attributes", "id", "name", "email", "password", "datecreated", "createdbyid", "dateupdated", "updatedbyid", "approvedbyid", "dateapproved", "lastlogin", "lastloginfrom"): # , "datecreatedepoch", "lastloginepoch", "dateapprovedepoch", "dateupdatedepoch"): # attributes, datecreated, createdbyid
        if k == "attributes":
          rec[k] = json.dumps(row[k])
        else:
          rec[k] = row[k]
      return rec

    def edit():
      bbsengine.updatetopbar("edit member")
      name = ttyio.inputstring("name: ", "", verify=verifyMemberFound, noneok=True, multiple=False, args=args)
      if name is None:
        ttyio.echo("aborted.")
        return
      ttyio.echo("begin editing member.")
      dbh = bbsengine.databaseconnect(args)
      member = bbsengine.getmemberbyname(dbh, args, name)
      if member is None:
        ttyio.echo("%r not found." % (name), level="error")
        return

      memberid = member["id"]
      ttyio.echo("memberid=%r member=%r" % (memberid, member), interpret=False, level="debug")

      sysop = ttyio.inputboolean("sysop? [yN]: ", "N")
      bbsengine.setflag(dbh, memberid, "SYSOP", sysop)

      eros = ttyio.inputboolean("eros? [yN]: ", "N")
      bbsengine.setflag(dbh, memberid, "EROS", eros)

      magician = ttyio.inputboolean("magician? [yN]: ", "N")
      bbsengine.setflag(dbh, memberid, "MAGIC", magician)

      credits = ttyio.inputinteger("credits: ", member["credits"])
      member["credits"] = credits

      m = buildrecord(member)
      ttyio.echo("m=%r" % (m), interpret=False)
      bbsengine.update(dbh, "engine.__member", memberid, m)
      dbh.commit()
      ttyio.echo("member %r updated." % (name), level="success")
      return

    def new():
      bbsengine.updatetopbar("new member")
      name = ttyio.inputstring("name: ", "", verify=verifyMemberNotFound, noneok=False, multiple=False, args=args)
      email = ttyio.inputstring("email: ", "", noneok=False, multiple=False, args=args)
      plaintextpassword = ttyio.inputstring("password: ", "", noneok=False, multiple=False, args=args)
      loginid = ttyio.inputstring("loginid: ", "", noneok=True, multiple=False, args=args)
      shell = ttyio.inputstring("shell: ", "", noneok=True, multiple=False, args=args)
      sysop = ttyio.inputboolean("sysop?: ", "N", "YN")
      credits = ttyio.inputinteger("credits: ", "42", noneok=True, multiple=False, args=args)

      if ttyio.inputboolean("add?: ", "", "YN") is False:
        ttyio.echo("{f6}member not added.")
        return

      member = {}
      member["name"] = name
      member["email"] = email
      member["datecreated"] = "now()"
      member["dateapproved"] = "now()"
      dbh = bbsengine.databaseconnect(args)
      memberid = bbsengine.insert(dbh, "engine.__member", member)
      ttyio.echo("memberid=%r" % (memberid), level="debug")
      attributes = {}
      attributes["loginid"] = loginid
      attributes["shell"] = shell
      bbsengine.setmemberattributes(dbh, memberid, attributes, reset=True)
      bbsengine.setmemberpassword(dbh, memberid, plaintextpassword)
      bbsengine.setflag(dbh, memberid, "SYSOP", sysop)
      bbsengine.setmembercredits(dbh, memberid, credits)
      dbh.commit()
      ttyio.echo("member added.")

    done = False
    while not done:
      bbsengine.updatetopbar("member")

      ttyio.echo("{/all}")

      ttyio.echo("[N]ew")
      ttyio.echo("[E]dit")
#      ttyio.echo("[D]elete")
      ttyio.echo("{f6}[Q]uit")
      ch = ttyio.inputchar("member [NEQ]: ", "NEQ", "Q")
      if ch == "Q":
        ttyio.echo("Q -- Quit")
        done = True
      elif ch == "N":
        ttyio.echo("N -- New")
        new()
      elif ch == "E":
        ttyio.echo("E -- Edit")
        edit()
    return

def main():
  parser = argparse.ArgumentParser("bbsengine5")

  parser.add_argument("--verbose", action="store_true", dest="verbose")
  parser.add_argument("--debug", action="store_true", dest="debug")

  defaults = {"databasename": "zoidweb5", "databasehost":"localhost", "databaseuser": None, "databaseport":5432, "databasepassword":None}
  bbsengine.buildargdatabasegroup(parser, defaults)

  args = parser.parse_args()
  done = False
  while not done:
    bbsengine.title("engine")
    ttyio.echo("[M]embers")
    ttyio.echo("[E]mail")
    ttyio.echo("{f6}[Q]uit")
    ch = ttyio.inputchar("engine: ", "MEQ", "Q")
    if ch == "M":
      ttyio.echo("Members")
      member(args)
      continue
    elif ch == "E":
      ttyio.echo("E-Mail")
      email(args)
      continue
    else:
      ttyio.echo("Quit")
      done = True
      break

if __name__ == "__main__":
  main()
