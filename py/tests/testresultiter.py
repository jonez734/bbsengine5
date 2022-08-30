import time
import locale
import argparse

import bbsengine5 as bbsengine
import ttyio5 as ttyio

def filterfunc(result):
#  ttyio.echo("filterfunc.100: result=%r" % (result))
  return True

def ResultIter(cursor, arraysize=1000, filterfunc=None, **kw):
    'An iterator that uses fetchmany to keep memory usage down'
    while True:
        results = cursor.fetchmany(arraysize)
        if not results:
            break
        for result in results:
          if filterfunc is None:
            yield result
          elif callable(filterfunc) is True and filterfunc(result, **kw) is True:
            yield result

def main():
    parser = argparse.ArgumentParser("testresultiter")
    parser.add_argument("--verbose", action="store_true", dest="verbose")
    parser.add_argument("--debug", action="store_true", dest="debug")
    parser.add_argument("args", action="store", nargs="?")

    defaults = {"databasename": "zoidbo", "databasehost":"127.0.0.1", "databaseuser": None, "databaseport":5432, "databasepassword":None}
    bbsengine.buildargdatabasegroup(parser, defaults)

    args = parser.parse_args()

    locale.setlocale(locale.LC_ALL, "")
    time.tzset()

    if args is not None and "debug" in args and args.debug is True:
        ttyio.echo("testresultiter.main.100: args=%r" % (args))

    if args.args is None:
        ttyio.echo("no search terms specified", level="error")
        return

    dbh = bbsengine.databaseconnect(args)
    sql = "select * from zoidbo.pw where query ~ %s order by dateenteredepoch desc"
    dat = (args.args,)
    cur = dbh.cursor()
    cur.execute(sql, dat)
#    print(cur.mogrify(sql, dat))
    if cur.rowcount == 0:
      ttyio.echo("{f6}* no matches *{f6}")
    else:
    #    for rec in cur.fetchall():
      ttyio.echo("cur=%r" % (cur), level="debug")
      for rec in bbsengine.ResultIter(cur, arraysize=10, filterfunc=filterfunc):
#          print(rec)
          ttyio.echo("%s from \"%s\" (%s) #%s" % (rec["query"].strip(), rec["description"].strip(), bbsengine.datestamp(rec["dateentered"]), rec["projectid"]))
    cur.close()
    dbh.close()

if __name__ == "__main__":
    main()
