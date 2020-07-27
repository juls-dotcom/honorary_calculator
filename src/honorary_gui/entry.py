from tkinter import *

root = Tk()

e = Entry(root,
          width=50,
          bg="black",
          fg='white',
          borderwidth=5)
e.pack()

def myClick():
    myLabel = Label(root,text=e.get() + " clicked a button")
    myLabel.pack()#grid(row=1, column=1)

myButton = Button(root,
                  text="Enter Your Name",
                  #state=DISABLED,
                 # padx=50,
                 # pady=100,
                  command=myClick,
                  fg="blue",
                  bg="red"
                  )
myButton.pack()
root.mainloop()
