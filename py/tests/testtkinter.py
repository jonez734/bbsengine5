#from tkinter import *
#import time

#root= Tk()
#root.geometry("400x100")
#root.config(bg='black')

#def update():
#    clock.config(text=time.strftime("%I:%M:%S"))
#    clock.after(1000,update)


#clock = Label(root, background = 'black',foreground = 'white', font = ('arial', 40, 'bold'))
#clock.pack()
#update()
#root.title('clock')
#root.mainloop()


# importing tkinter gui
import tkinter as tk
 
#creating window
window=tk.Tk()
 
#getting screen width and height of display
width= window.winfo_screenwidth()
height= window.winfo_screenheight()
#setting tkinter window size
window.geometry("%dx%d" % (width*0.55, height*0.80))
window.title("The Galaxy Federation BBS")
label = tk.Label(window, text="greetings!")
label.pack()
 
window.mainloop()
