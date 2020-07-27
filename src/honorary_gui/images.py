from tkinter import *

root = Tk()
root.title("Test")

button_quit = Button(root, text = 'Exit Calculator', command=root.quit)
button_quit.pack()

root.mainloop()