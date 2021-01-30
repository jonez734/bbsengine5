import argparse
import ttyio4 as ttyio
import libbbsengine5 as bbsengine
import locale

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

def members(args):
    ttyio.echo("[N]ew")
    ttyio.echo("[E]dit")
    ttyio.echo("[D]elete")
    ttyio.echo("{f6}[Q]uit")
    ch = ttyio.inputchar("member [NEDQ]: ", "NEDQ", "Q")
    if ch == "Q":
        ttyio.echo("Q -- Quit")
        return
    elif ch == "N":
        ttyio.echo("N -- New{f6}")
        name = ttyio.inputstring("name: ", "", verify=verifyMemberNotFound, noneok=False, multiple=False, opts=args)
        email = ttyio.inputstring("email: ", "", noneok=False, multiple=False, opts=args)
        plaintextpassword = ttyio.inputstring("password: ", "", noneok=False, multiple=False, opts=args)
        loginid = ttyio.inputstring("loginid: ", "", noneok=True, multiple=False, opts=args)
        shell = ttyio.inputstring("shell: ", "", noneok=True, multiple=False, opts=args)

        # $sql = "update engine.__member set password=crypt(".$dbh->quote($plaintext, "text").", gen_salt('bf')) where id=".$dbh->quote($memberid);
        member = {}
        member["name"] = name
        member["email"] = email
        # member["password"] = "crypt(%s, gen_salt('bf'))" % (password)
        member["datecreated"] = "now()"
        member["dateapproved"] = "now()"
        dbh = bbsengine.databaseconnect(args)
        memberid = bbsengine.insert(dbh, "engine.__member", member, mogrify=True)
        ttyio.echo("memberid=%r" % (memberid), level="debug")
        attributes = {}
        attributes["loginid"] = loginid
        attributes["shell"] = shell
        bbsengine.setmemberattributes(dbh, memberid, attributes, reset=True)
        bbsengine.setmemberpassword(dbh, memberid, plaintextpassword)
        dbh.commit()
        ttyio.echo("member added.")
        return
    return

def main():
    # parser = OptionParser(usage="usage: %prog [options] projectid")
    parser = argparse.ArgumentParser("bbsengine5")

    # parser.add_option("--verbose", default=True, action="store_true", help="run %prog in verbose mode")
    parser.add_argument("--verbose", action="store_true", dest="verbose")

    # parser.add_option("--debug", default=False, action="store_true", help="run %prog in debug mode")
    parser.add_argument("--debug", action="store_true", dest="debug")

    defaults = {"databasename": "zoidweb5", "databasehost":"localhost", "databaseuser": None, "databaseport":5432, "databasepassword":None}
    bbsengine.buildargdatabasegroup(parser, defaults)
    
    args = parser.parse_args()
    # ttyio.echo("args=%r" % (args), level="debug")

    locale.setlocale(locale.LC_ALL, "")

#    bbsengine.inittopbar()

    done = False
    while not done:
#        bbsengine.updatetopbar("engine5 main menu")
        ttyio.echo("[M]embers")
        ttyio.echo("[S]igs")
        ttyio.echo("{f6}[Q]uit")
        
        ch = ttyio.inputchar("engine5 [MSQ]: ", "MSQ", "")
        if ch == "M":
            ttyio.echo("M -- member")
            members(args)
        elif ch == "Q":
            done = True
            ttyio.echo("Q -- quit")

if __name__ == "__main__":
    main()
