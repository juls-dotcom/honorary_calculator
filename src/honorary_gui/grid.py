from tkinter import *

root = Tk()
# Creating a label widget
myLabel1 = Label(root, text=' Hello World!')
myLabel2 = Label(root, text=' My name is Juls')
# Shoving it onto the screen
myLabel1.grid(row=0, column=0)
myLabel2.grid(row=0, column=1)

root.mainloop()
