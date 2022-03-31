import bbsengine5 as bbsengine

value = 1647998166
while True:
    buf = bbsengine.inputdate("prompt: ", value, noneok=True)
    if buf is None:
        break
    print(bbsengine.datestamp(buf))
    
