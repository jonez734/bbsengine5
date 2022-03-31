import bbsengine5 as bbsengine
import ttyio5 as ttyio

import argparse

from argparse import Namespace

def main():
  parser = argparse.ArgumentParser("ogun")
  
  parser.add_argument("--verbose", action="store_true", dest="verbose")
  parser.add_argument("--debug", default=False, action="store_true", dest="debug")
  parser.add_argument("--eros", default=False, action="store_true", dest="eros")

  defaults = {"databasename": "zoidweb5", "databasehost":"localhost", "databaseuser": None, "databaseport":5432, "databasepassword":None}
  bbsengine.buildargdatabasegroup(parser, defaults)

  args = parser.parse_args()

  res = bbsengine.inputsig(args, "prompt: ", multiple=False)
  print(res,type(res))
if __name__ == "__main__":
    main()

