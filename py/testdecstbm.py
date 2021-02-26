import time
import bbsengine5 as bbsengine
import ttyio4 as ttyio

# @see https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console
def updateprogress(iteration, total):
  terminalwidth = ttyio.getterminalwidth()
  decimals = 2
  fill = "#"
  length = terminalwidth-23
  percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
  filledLength = length * iteration // total
  bar = fill * filledLength + '.' * (length - filledLength)
  buf = "{lightgreen}Progress [% 6s%%]: [%s]{/fgcolor}" % (percent, bar)
  
  bbsengine.updatebottombar(buf)
  # Print New Line on Complete
  #if iteration == total: 
  #  print()

  #percent = int(iteration / total * 100.0)
  #ttyio.echo("percent=%d" % (percent))
  return

terminalheight = ttyio.getterminalheight()

ttyio.echo("{curpos:%d,0}" % (terminalheight-3))
bbsengine.initscreen(topmargin=2, bottommargin=1)
bbsengine.updatetopbar("this is a test")
bbsengine.updatebottombar("test here")
for x in range(0, 50):
    ttyio.echo("%d: %d" % (x, bbsengine.diceroll(20)), end="")
    time.sleep(0.050)
    updateprogress(x, 50)
bbsengine.updatebottombar("{el}")
ttyio.echo("{reset}done.")
# bbsengine.updatebottombar("{lightgreen}done.{/all}")
