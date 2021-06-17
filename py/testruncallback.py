import argparse
import bbsengine5 as bbsengine
from bbsengine5 import runcallback

def member(args, **kwargs):
    print("inside member")

def main():
    # parser = OptionParser(usage="usage: %prog [options] projectid")
    parser = argparse.ArgumentParser("testruncallback")

    # parser.add_option("--verbose", default=True, action="store_true", help="run %prog in verbose mode")
    parser.add_argument("--verbose", action="store_true", dest="verbose")

    # parser.add_option("--debug", default=False, action="store_true", help="run %prog in debug mode")
    parser.add_argument("--debug", action="store_true", dest="debug")

    defaults = {"databasename": "zoidweb5", "databasehost":"localhost", "databaseuser": None, "databaseport":5432, "databasepassword":None}
    bbsengine.buildargdatabasegroup(parser, defaults)

    args = parser.parse_args()
    # ttyio.echo("args=%r" % (args), level="debug")

    runcallback(args, member)

if __name__ == "__main__":
    main()
