import ttyio5 as ttyio
import bbsengine5 as bbsengine

def poparea():

  ttyio.echo("poparea.120: areastack=%r" % (bbsengine.areastack), interpret=False)
  if len(bbsengine.areastack) < 1:
    return

  width = ttyio.getterminalwidth()

  bbsengine.areastack.pop()
  if len(bbsengine.areastack) > 0:
    buf = bbsengine.areastack[-1]
    ttyio.echo("poparea.100: areastack=%r buf=%r" % (bbsengine.areastack, buf), interpret=False)
    bbsengine.updatebottombar("{var:engine.areacolor} %s {/all}" % (buf.ljust(width-2, " ")))
  ttyio.echo("poparea.140: areastack=%r" % (bbsengine.areastack), interpret=False)
  return

def main():
  ttyio.setvariable("engine.areacolor", "{bggray}{white}")
  ttyio.echo("{f6:3}{curpos:%d,0}" % (ttyio.getterminalheight()-2))
  bbsengine.initscreen(bottommargin=1)
  bbsengine.setarea(":smile: test alpha")
  ttyio.inputboolean("continue: ", "Y")
  bbsengine.setarea("test bravo")
  ttyio.inputboolean("continue: ", "Y")
  bbsengine.setarea("test charlie")
  ttyio.inputboolean("continue: ", "Y")

  ttyio.echo(bbsengine.hr())

#  ttyio.echo("areastack=%r" % (bbsengine.areastack), interpret=False)

  poparea()
  ttyio.echo("areastack=%r" % (bbsengine.areastack), interpret=False)
  ttyio.inputboolean("continue: ", "Y")

  poparea()
  ttyio.echo("areastack=%r" % (bbsengine.areastack), interpret=False)
  ttyio.inputboolean("continue: ", "Y")

  poparea()
  ttyio.echo("areastack=%r" % (bbsengine.areastack), interpret=False)
  if len(bbsengine.areastack) > 0:
    ttyio.inputboolean("continue: ", "Y")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        ttyio.echo("{/all}{bold}INTR{bold}")
    except EOFError:
        ttyio.echo("{/all}{bold}EOF{/bold}")
    finally:
        ttyio.echo("{decsc}{curpos:%d,0}{el}{decrc}{reset}{/all}" % (ttyio.getterminalheight()))
