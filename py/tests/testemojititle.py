import ttyio5 as ttyio
import bbsengine5 as bbsengine

#title = "dante's inferno"
title = "- :smile: :fire: dante's inferno :fire: -"
interp = ttyio.interpretmci(title, wordwrap=False, strip=True)
ttyio.echo("interp=%r %d" % (interp, len(interp)), interpret=False)
ttyio.echo("title=%r %d" % (title, len(title)), interpret=False)
#ttyio.echo("interp=%r len=%d" % (interp, len(interp)))
bbsengine.title(title)

title = "a title without emojis"

bbsengine.title(title)
