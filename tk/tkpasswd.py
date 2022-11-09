import argparse

import tkinter as tk
from tkinter import ttk

import ttyio5 as ttyio
import bbsengine5 as bbsengine


class App(tk.Tk):
    def __init__(self, args):
        super().__init__()

        self.args = args

#        self.geometry('300x110')
#        self.resizable(0, 0)
        self.title('Reset Password')
        # UI options
        paddings = {'padx': 5, 'pady': 5}
        entry_font = {'font': ('monospace', 11)}

        # configure the grid
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=3)

        self.username = tk.StringVar()
        self.new_password = tk.StringVar()
        self.old_password = tk.StringVar()
        self.repeat_password = tk.StringVar()

        # username
        username_label = ttk.Label(self, text="Username:")
        username_label.grid(column=0, row=0, sticky=tk.W, **paddings)

        username_entry = ttk.Entry(self, textvariable=self.username, **entry_font)
        username_entry.grid(column=1, row=0, sticky=tk.E, **paddings)

        self.sysop = False # bbsengine.checksysop(self.args)

        row = 1
        # old_password
        if self.sysop is False:
            old_password_label = ttk.Label(self, text="Old Password:")
            old_password_label.grid(column=0, row=row, sticky=tk.W, **paddings)

            old_password_entry = ttk.Entry(self, textvariable=self.old_password, show="*", **entry_font)
            old_password_entry.grid(column=1, row=row, sticky=tk.E, **paddings)

            row += 1

        new_password_label = ttk.Label(self, text="New Password:")
        new_password_label.grid(column=0, row=row, sticky=tk.W, **paddings)

        new_password_entry = ttk.Entry(self, textvariable=self.new_password, show="*", **entry_font)
        new_password_entry.grid(column=1, row=row, sticky=tk.E, **paddings)

        row += 1
        repeat_password_label = ttk.Label(self, text="Repeat Password:")
        repeat_password_label.grid(column=0, row=row, sticky=tk.W, **paddings)

        repeat_password_entry = ttk.Entry(self, textvariable=self.repeat_password, show="*", **entry_font)
        repeat_password_entry.grid(column=1, row=row, sticky=tk.E, **paddings)
        
        row += 1

        # change button
        change_button = ttk.Button(self, text="change password", command=self.change)
        change_button.grid(column=1, row=row, sticky=tk.E, **paddings)

        # configure style
        self.style = ttk.Style(self)
        self.style.configure('TLabel', font=('Helvetica', 11))
        self.style.configure('TButton', font=('Helvetica', 11))

    def change(self):
        username = self.username.get()
        new_password = self.new_password.get()
        old_password = self.old_password.get()
        repeat_password = self.repeat_password.get()

        if self.sysop is False:
            if bbsengine.checkpassword(args, old_password) is False:
                ttyio.echo("password mismatch (oldpassword)", level="error")
                return

        if new_password != repeat_password:
            ttyio.echo("enter your new password twice", level="error") # dialog box?
            return

        ttyio.echo(f"username={username!r}", level="debug")
        ttyio.echo(f"new_password={new_password!r}", level="debug")
        memberid = bbsengine.getmemberidfromloginid(self.args, username)
        if memberid is False:
            ttyio.echo("you do not exist! go away!", level="error")
            return

        bbsengine.setpassword(args, new_password)

        dbh = bbsengine.databaseconnect(args)
        dbh.commit()
#        if bbsengine.checkpassword(args, username, memberid) is True:
#            ttyio.echo("password is correct")
#        else:
#            ttyio.echo("password is wrong")
#        ttyio.echo(f"memberid={memberid!r}", level="debug")

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
    app.bind('<Escape>', lambda e: app.close(e))
    app.mainloop()
