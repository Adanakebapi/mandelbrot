import tkinter as tk
from PIL import Image, ImageTk
import zlib

def read_row(y,height):
    dcomp = zlib.decompressobj()
    totaldec = 0
    lastflush = 0
    dec = b""
    with open("mandelbrot.png",'rb') as f:
        f.seek(16)
        size = to_int(f.read(4))
        f.seek(13,1)
        while True:
            offset = f.tell()
            length = to_int(f.read(4))
            typ = f.read(4)
            data = f.read(length)
            crc = f.read(4)
            if typ == b"IEND":
                break
            elif typ == b"IDAT":
                new_dec = dcomp.decompress(data)
                dec += new_dec
                totaldec += len(new_dec)
                if y*(size+1) <= totaldec:
                    if totaldec >= (y+height)*(size+1):
                        dec = dec[y*(size+1)-lastflush:(y+height)*(size+1)-lastflush]
                        dec = bytes(j for i,j in enumerate(dec) if i%(size+1) != 0)
                        return dec, size
                else:
                    dec = b""
                    lastflush = totaldec

def get_image(x,y):
    data, size = read_row(y-360,720)
    nimg = Image.new("L",(size,720))
    nimg.putdata(data)
    del data
    return nimg.crop((x-360,0,x+360,720)).convert("RGB")

to_int = lambda x:sum(j*256**i for i,j in enumerate(x[::-1]))

z = None
zoomed = False

def on_mb1(e):
    global nimg, imgtk, z, zoomed
    if zoomed:
        return
    imgc = img.copy()
    imgc.putpixel((e.x,e.y),(255,0,0))
    imgtk = ImageTk.PhotoImage(imgc)
    lb.config(image=imgtk)
    z = (e.x,e.y)

def on_zoom():
    global img, nimg, imgtk, z, zoomed
    if zoomed:
        imgtk = ImageTk.PhotoImage(img)
        lb.config(image=imgtk)
        z = None
        zoomed = False
    elif z is not None:
        nimg = get_image(*tuple(int(i*65537/720) for i in z))
        imgtk = ImageTk.PhotoImage(nimg)
        lb.config(image=imgtk)
        z = None
        zoomed = True

root = tk.Tk()
root.title("Mandelbrot Viewer")
root.geometry("721x721")
root.resizable(0,0)

img = Image.open("mandelbrot_preview.png").convert("RGB")
nimg = img.copy()
imgtk = ImageTk.PhotoImage(img)

lb = tk.Label(root,image=imgtk)
lb.pack()

menu = tk.Menu(root)
menu.add_cascade(label="Zoom",command=on_zoom)

lb.bind("<Button-1>",on_mb1)

root.config(menu=menu)
root.mainloop()
