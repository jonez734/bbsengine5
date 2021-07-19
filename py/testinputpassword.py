import ttyio4 as ttyio
import bbsengine5 as bbsengine

def main():
    buf = ""
    pos = 0

    ttyio.echo("password: ", end="", flush=True)

    mask = "*"

    done = False
    while not done:
        ch = ttyio.getch(echoch=False)
        if ch == "\n":
            done = True
            break
        elif ch == "KEY_HOME":
            if pos > 0:
                ttyio.echo("{cursorleft:%d}" % (pos), end="", flush=True)
                pos = 0
        elif ch == "KEY_END":
            ttyio.echo("{cursorright:%d}" % (len(buf)), end="", flush=True)
            pos = len(buf)+1
        elif ch == "KEY_LEFT":
            if pos > 0:
                pos -= 1
                ttyio.echo("{cursorleft}", end="", flush=True)
            else:
                ttyio.echo("{bell}", end="", flush=True)
            continue
        elif ch == "KEY_RIGHT":
            if pos < len(buf):
                pos += 1
                ttyio.echo("{cursorright}", end="", flush=True)
            else:
                ttyio.echo("{bell}", end="", flush=True)
        elif ch == "KEY_BACKSPACE":
            if pos == 0:
                ttyio.echo("{bell}")
                continue
            ttyio.echo("\x08 \x08", end="", flush=True)
            pos -= 1
            buf = buf[:pos]
        elif ch == chr(127): # backspace
            ttyio.echo(ch, flush=True, end="")
            if pos > 0:
                pos -= 1
                ttyio.echo(chr(8)+" "+chr(8), flush=True, end="")
                buf = buf[:len(buf)-1]
            else:
                ttyio.echo("{bell}", end="",flush=True)
                pos = 0
            continue
        elif ch == chr(21): # ^u ctrl-u
            ctrlu = ""
            while pos > 0:
                ctrlu += chr(8)+" "+chr(8)
                pos -= 1
            buf = ""
            ttyio.echo(ctrlu, flush=True, end="")
            continue
        elif len(ch) == 1:
            buf = buf[:pos] + ch + buf[pos+1:]
            pos += 1
            ttyio.echo(mask, end="", flush=True)
    ttyio.echo("{f6}buf=%s" % (buf))

if __name__ == "__main__":
    main()
