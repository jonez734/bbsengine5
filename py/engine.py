import argparse

import ttyio4 as ttyio
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

def member(args, **kwargs):
    def edit():
      bbsengine.updatetopbar("edit member")
      name = ttyio.inputstring("name: ", "", verify=verifyMemberFound, noneok=True, multiple=False, args=args)
      if name is None:
        ttyio.echo("aborted.")
        return
      ttyio.echo("begin editing member.")
      dbh = bbsengine.databaseconnect(args)
      member = bbsengine.getmemberbyname(dbh, args, name)
      ttyio.echo("member=%r" % (member), interpret=False)
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

      if ttyio.inputboolean("save?: ", "", "YN") is False:
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
        ttyio.echo("N -- New{f6}")
        new()
      elif ch == "E":
        ttyio.echo("E -- Edit{f6}")
        edit()
    return

def main():
  parser = argparse.ArgumentParser("empyre")

  parser.add_argument("--verbose", action="store_true", dest="verbose")
  parser.add_argument("--debug", action="store_true", dest="debug")

  defaults = {"databasename": "zoidweb5", "databasehost":"localhost", "databaseuser": None, "databaseport":5432, "databasepassword":None}
  bbsengine.buildargdatabasegroup(parser, defaults)

  args = parser.parse_args()
  member(args)

if __name__ == "__main__":
  main()
