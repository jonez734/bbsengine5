import argparse

import tkinter as tk
from tkinter import ttk

import ttyio5 as ttyio
import bbsengine5 as bbsengine


class App(tk.Tk):
    def __init__(self, args):
        super().__init__()

        self.args = args

        self.geometry('300x110')
        self.resizable(0, 0)
        self.title('Login')
        # UI options
        paddings = {'padx': 5, 'pady': 5}
        entry_font = {'font': ('Helvetica', 11)}

        # configure the grid
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=3)

        self.username = tk.StringVar()
        self.password = tk.StringVar()

        # username
        username_label = ttk.Label(self, text="Username:")
        username_label.grid(column=0, row=0, sticky=tk.W, **paddings)

        username_entry = ttk.Entry(self, textvariable=self.username, **entry_font)
        username_entry.grid(column=1, row=0, sticky=tk.E, **paddings)

        # password
        password_label = ttk.Label(self, text="Password:")
        password_label.grid(column=0, row=1, sticky=tk.W, **paddings)

        password_entry = ttk.Entry(self, textvariable=self.password, show="*", **entry_font)
        password_entry.grid(column=1, row=1, sticky=tk.E, **paddings)

        # login button
        login_button = ttk.Button(self, text="Login", command=self.check)
        login_button.grid(column=1, row=3, sticky=tk.E, **paddings)

        # configure style
        self.style = ttk.Style(self)
        self.style.configure('TLabel', font=('Helvetica', 11))
        self.style.configure('TButton', font=('Helvetica', 11))
        self.bind('<Escape>', lambda e: self.close(e))

    def check(self):
        username = self.username.get()
        password = self.password.get()
        ttyio.echo(f"username={username!r}", level="debug")
        ttyio.echo(f"password={password!r}", level="debug")
        memberid = bbsengine.getmemberidfromloginid(self.args, username)
        if memberid is False:
            ttyio.echo("you do not exist! go away!")
            return

        if bbsengine.checkpassword(args, password, memberid) is True:
            ttyio.echo("password is correct")
        else:
            ttyio.echo("password is wrong")
        ttyio.echo(f"memberid={memberid!r}", level="debug")

    def close(self, e):
       self.destroy()

def buildargs(args=None, **kw):
    parser = argparse.ArgumentParser("tklogin")
    parser.add_argument("--verbose", action="store_true", dest="verbose")
    parser.add_argument("--debug", action="store_true", dest="debug")

    defaults = {"databasename": "zoidweb5", "databasehost":"localhost", "databaseuser": None, "databaseport":15433, "databasepassword":None} # port=5432
#    defaults = {"databasename": "zoidweb5", "databasehost":"localhost", "databaseuser": None, "databaseport":5432, "databasepassword":None} # port=5432
    bbsengine.buildargdatabasegroup(parser, defaults)

    return parser

if __name__ == "__main__":
    parser = buildargs()
    args = parser.parse_args()

    app = App(args)
    app.mainloop()
