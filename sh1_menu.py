import logging
from tkinter import *
from tkinter import ttk
import re

class sh1_menu():
    def __init__(self):
        self.__sha1=[]
        self.__lines=[]
        self.__read_key_file()
        self.__tk= Tk()
        self.__tk.geometry("370x370")
        self.__tk.title('Sha-1 Selection')
        self.__tk.config(bg="grey")
        logging.basicConfig(level=logging.INFO)
        style = ttk.Style(self.__tk)
        self.__tk.tk.eval("""
        set base_theme_dir awthemes-10.2.0
        package ifneeded awthemes 10.2.0 \
            [list source [file join $base_theme_dir awthemes.tcl]]
        package ifneeded colorutils 4.8 \
            [list source [file join $base_theme_dir colorutils.tcl]]
        package ifneeded awlight 7.6 \
            [list source [file join $base_theme_dir awlight.tcl]]
        """)
        self.__tk.tk.call("package", "require", 'awthemes')
        style.theme_use('awdark')
        self.__build_sha1_window()
        self.__tk.mainloop()

    def __read_key_file(self):
        with open('keychains.txt', 'r') as f:
            self.__lines = f.read().splitlines()
            self.__lines = list(dict.fromkeys(self.__lines))[:-1]

    def __build_sha1_window(self):
        for x in range(len(self.__lines)):
            self.__print_sh_button(x)


    def __print_sh_button(self,i):
        ttk.Button(self.__tk,text=self.__lines[i][:self.__lines[i].index(' ')]+'\r'+self.__lines[i][self.__lines[i].index(' '):],
                   width=40,command=lambda:self.__set_sh(self.__lines[i])).grid(row=i, column=0)

    def __set_sh(self,sh):
        self.selected_sh=sh[:sh.index(' ')]
        self.__tk.quit()
        logging.info('Sha1 selected,window ruined')
        self.__tk.destroy()


