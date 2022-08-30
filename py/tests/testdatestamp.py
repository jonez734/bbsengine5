import bbsengine5 as bbsengine

print(bbsengine.datestamp())

buf = "2022-03-30 06:55pm EDT"
print("buf=%s" % (buf))
res = bbsengine.datestamp(buf)
print("res=%s" % (res))

