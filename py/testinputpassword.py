import bbsengine5 as bbsengine
import ttyio4 as ttyio

def main():
    res = bbsengine.inputpassword("prompt: ")
    ttyio.echo("{f6}res=%r" % (res))

if __name__ == "__main__":
    main()
