import customtkinter
import tkinter as tk
from PIL import Image, ImageTk

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

app = customtkinter.CTk()
app.geometry("900x550")

btnPath = "assets/syncbutton.png"
syncBtn = Image.open(btnPath)
syncBtn = ImageTk.PhotoImage(syncBtn)

# Use standard tkinter Label for image display
label = tk.Label(app, image=syncBtn)
label.pack()

def button_function():
    print("button pressed")

# Use CTkButton instead of tkinter Button
arrow_button_text = "CTkButton \u2192"
button = customtkinter.CTkButton(master=app, text=arrow_button_text, command=button_function)
button.place(relx=0.95, rely=0.05, anchor=customtkinter.NE)

app.mainloop()
