from tkinter import *
root = Tk()

def click():
	label = Label(root, text="Button clicked.")
	label.pack()

b = Button(root, text="Click Here", padx = 50, pady = 20, command = click)
b.pack()
root.mainloop()