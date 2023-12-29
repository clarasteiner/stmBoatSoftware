from tkinter import *
from transformationCurves import main

a = False
values = [16, 12, 7.6, 6.0, 0.4, 1100, 0, 0]
list = ["Temperatur", "Sauerstoff", "pH", "Nitrat", "Ammonium", "Leitfähigkeit", "Phosphat", "BSB5"]

root = Tk()

root.title("Gewässergüteklasse")
root.geometry('350x250')

lbl_p = Label(root, text="Phosphat: ")
lbl_p.grid(column=0, row=0, sticky=W)

txt1 = Entry(root, width=10)
txt1.grid(column=1, row=0, sticky=W)

lbl_b = Label(root, text="BSB5: ")
lbl_b.grid(column=0, row=1, sticky=W)

txt2 = Entry(root, width=10)
txt2.grid(column=1, row=1, sticky=W)

lbl1 = []
lbl2 = []
lbl3 = []


def clicked():
    if len(txt1.get()) != 0 and len(txt1.get()) != 0:
        btn.grid_forget()
        txt1.grid_forget()
        txt2.grid_forget()
        lbl_b.grid_forget()
        lbl_p.grid_forget()

        values[-2] = float(txt1.get())
        values[-1] = float(txt2.get())
        index, ci, quality_class = main(values)

        for i in range(8):
            lbl1.append(Label(root, text=list[i] + ": "))
            lbl2.append(Label(root, text=str(index[i])))
            lbl3.append(Label(root, text="⬛" * (int(index[i]) // 10) + "⬜" * (10 - (int(index[i]) // 10))))
            lbl1[i].grid(column=0, row=i, sticky=W)
            lbl2[i].grid(column=1, row=i, sticky=W)
            lbl3[i].grid(column=2, row=i, sticky=W)

        lbl = Label(root, text="Gewässergüteklasse: " + str(ci))
        lbl.grid(column=0, row=8, sticky=W)
        lbl = Label(root, text=quality_class)
        lbl.grid(column=0, row=9, sticky=W)


btn = Button(root, text="Fertig", command=clicked)
btn.grid(column=1, row=3)

root.mainloop()
