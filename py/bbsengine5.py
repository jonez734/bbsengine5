import argparse
import ttyio4 as ttyio
import libbbsengine5 as libbbsengine

def members(args):
    ttyio.echo("[N]ew member")
    ttyio.echo("[E]dit member")
    ttyio.echo("[D]elete member")
    ttyio.echo("{f6}[Q]uit")
    return

def main():
    # parser = OptionParser(usage="usage: %prog [options] projectid")
    parser = argparse.ArgumentParser("bbsengine5")

    # parser.add_option("--verbose", default=True, action="store_true", help="run %prog in verbose mode")
    parser.add_argument("--verbose", action="store_true", dest="verbose")

    # parser.add_option("--debug", default=False, action="store_true", help="run %prog in debug mode")
    parser.add_argument("--debug", action="store_true", dest="debug")

    defaults = {"databasename": "zoidweb5", "databasehost":"localhost", "databaseuser": None, "databaseport":15433, "databasepassword":None}
    bbsengine.buildargdatabasegroup(parser, defaults)
    
    args = parser.parse_args()
    # ttyio.echo("args=%r" % (args), level="debug")

    locale.setlocale(locale.LC_ALL, "")

    libbbsengine.inittopbar()

    done = False
    while not done:
        libbbsengine.updatetopbar("engine5 main menu")
        ttyio.echo("[M]embers")
        ttyio.echo("[S]igs")
        ttyio.echo("{f6}[Q]uit")
        
        ch = ttyio.inputchar("engine5 [MSQ]: ", "MSQ", "")
        if ch == "M":
            members(args)
        elif ch == "Q":
            done = True
            ttyio.echo("Q -- quit")

if __name__ == "__main__":
    main()
