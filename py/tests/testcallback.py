import importlib
import argparse

def addpost(args:object=None):
    print("inside addpost!")
    return

def main():
    args = argparse.Namespace()

    buf = "socrates.addpost"

    s = buf.split(".")
    print("s=%r" % (s))
    if len(s) > 1:
        modulepath = ".".join(s[:-1])
        functionname = s[len(s)-1:][0]
    else:
        modulepath = None
        functionname = s[0]

    print("modulepath=%r functionname=%r" % (modulepath, functionname))

    if modulepath is not None:
        try:
            m = importlib.import_module(modulepath)
        except ModuleNotFoundError:
            print("no module")
        else:
            print("m=%r" % (m))
            func = getattr(m, functionname)
            print("func=%r" % (func))
            if callable(func) is True:
                print("yes!")
                func(args)
    else:
        if callable(functionname) is True:
            print("callable")
        else:
            print("not callable")

    print("done.")

if __name__ == "__main__":
    main()
