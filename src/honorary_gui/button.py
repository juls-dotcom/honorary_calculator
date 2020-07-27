from tkinter import *

root = Tk()

def myClick():
    myLabel = Label(root,
                    text="Clicked a Button")
    myLabel.grid(row=1, column=1)

myButton = Button(root, text="Click Me!",
                  #state=DISABLED,
                  padx=50,
                  pady=100,
                  command=myClick,
                  fg="blue",
                  bg="red")
myButton.grid(row=1, column=1)

root.mainloop()
