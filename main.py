from tkinter import *
from tkinter import ttk
from ios_tkinter  import ios_tkinter
from android_apk_tkinter import android_apk_tkinter
from android_aab_tkinter import android_aab_tkinter

tk = Tk()

def init_tkinter():
    global tk
    tk.geometry("500x550")
    tk.title('Appdome Signatures tool')
    tk = ttk.Notebook(tk)
    android_apk_tkinter(tk)
    android_aab_tkinter(tk)
    ios_tkinter(tk)
    style_load()
    tk.mainloop()

def style_load():
    global tk
    style = ttk.Style(tk)
    tk.tk.eval("""
    set base_theme_dir awthemes-10.2.0
    package ifneeded awthemes 10.2.0 \
        [list source [file join $base_theme_dir awthemes.tcl]]
    package ifneeded colorutils 4.8 \
        [list source [file join $base_theme_dir colorutils.tcl]]
    package ifneeded awlight 7.6 \
        [list source [file join $base_theme_dir awlight.tcl]]
    """)
    tk.tk.call("package", "require", 'awthemes')
    style.theme_use('awdark')

if __name__ == '__main__':

    init_tkinter()
