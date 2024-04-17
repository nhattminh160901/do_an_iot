from program import *
from PIL import Image, ImageTk

app = Application()
app.geometry("400x200")
app.title("PHAN MEM")
ico = Image.open("logo.png")
photo = ImageTk.PhotoImage(ico)
app.wm_iconphoto(False, photo)
app.mainloop()
