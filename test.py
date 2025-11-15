import tkinter as tk

root = tk.Tk()
output1 = tk.Text(root)
output1.pack()
output2 = tk.Text(root)
output2.pack()

def write(text):
    output1.insert("end", text + "1" + "\n")
    output1.see("end")
    output2.insert("end", text + "2" + "\n")
    output2.see("end")

write("This feels like a console.")
from time import sleep
while True:
    write("This is a consle")
    root.update()