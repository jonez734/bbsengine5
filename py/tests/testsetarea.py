import ttyio5 as ttyio
import bbsengine5 as bbsengine
import time

def rightside():
  return "YES! "+time.ctime(time.time())

def main():
  time.tzset()

  ttyio.echo("{f6:3}{curpos:%d,0}" % (ttyio.getterminalheight()-2))
#  ttyio.setvariable("engine.areacolor", "{bggray}{white}")
  bbsengine.initscreen(bottommargin=1)
  bbsengine.setarea("{var:doesnotexist} gfd!", rightside)
  ttyio.inputboolean("continue: ", "Y")
  bbsengine.setarea("something else!", rightside)
  ttyio.echo("area set", level="debug")
  ttyio.echo("fee{f6}pheye{f6}foh{f6}")
  bbsengine.setarea("1234567890"*30, "right hand side")
  ttyio.inputboolean("continue: ", "Y")
#  bbsengine.poparea()

#  ttyio.setvariable("engine.areacolor", "{bggray}{white}")
#  ttyio.echo("{f6:3}{curpos:%d,0}" % (ttyio.getterminalheight()-2))
#  bbsengine.initscreen(bottommargin=1)
#  bbsengine.setarea("gfd!")
#  ttyio.echo("area set", level="debug")

if __name__ == "__main__":
  try:
      main()
  except KeyboardInterrupt:
      ttyio.echo("{/all}{bold}INTR{bold}")
  except EOFError:
      ttyio.echo("{/all}{bold}EOF{/bold}")
  finally:
      ttyio.echo("{decsc}{curpos:%d,0}{el}{decrc}{reset}{/all}" % (ttyio.getterminalheight()))
