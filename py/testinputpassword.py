import bbsengine5 as bbsengine
import ttyio4 as ttyio

def main():
    res = bbsengine.inputpassword()
    ttyio.echo("{f6}res=%r" % (res))

if __name__ == "__main__":
    main()
