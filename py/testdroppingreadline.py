import ttyio4

done = False
buf = ""
while not done:
    ch = ttyio4.getch(timeout=0.125)
    if ch == '\n':
        break

    if ch.isalnum() or ch.isspace():
        buf += ch
        print(ch)
    else:
        ttyio4.echo("{BELL}bell")
