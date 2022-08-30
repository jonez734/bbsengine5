import re

sigpaths = ""
#sigpaths = "top.entertainment"
#sigpaths = ["top.entertainment", "top"]

if type(sigpaths) == str:
    sigpaths = re.split("|".join(", "), sigpaths)
    sigpaths = [s.strip() for s in sigpaths]
    sigpaths = [s for s in sigpaths if s]

print(sigpaths)
for s in sigpaths:
    print("s=%r" % (s))
