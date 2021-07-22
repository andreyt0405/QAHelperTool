import logging
from future.moves.tkinter import filedialog, messagebox
from tkinter import ttk
from tkinter import *
from ios_activity import ios_activity

class ios_tkinter():
  def __init__(self,root):
      logging.basicConfig(level=logging.DEBUG)
      self.__var = IntVar()
      self.__provision_count=0
      self.__check_button_state='disabled'
      self.__data_collection = {"Active":'',"FilePath":'',"FileOut":'',"Provision":'',"P12":'',"ct":'',"Pass":''}
      self.__ios = ttk.Frame(root)
      root.add(self.__ios, text='iOS')
      root.pack(expand=1, fill="both")
      self.__prov_list = []
      self.__init_lables()
      self.__init_button()
      self.submit_button()

  def __init_lables(self):
    ttk.Label(self.__ios, text="Signatures IOS",font=("bold", 20), background='dodger blue4').place(x=60, y=30)
    ttk.Label(self.__ios, text="Upload IPA",font=("bold", 14)).place(x=60, y=100)
    ttk.Label(self.__ios, text="Upload Provision File", font=("bold", 14)).place(x=60, y=150)
    ttk.Label(self.__ios, text="Upload P12 File", font=("bold", 14)).place(x=60, y=200)
    ttk.Label(self.__ios, text="P12 Password", font=("bold", 14)).place(x=60, y=250)
    ttk.Label(self.__ios, text="Select Activty", font=("bold", 14)).place(x=60, y=290)
    ttk.Label(self.__ios, text="Logging Provisioning Listbox", font=("bold", 8)).place(x=90, y=335)
    self.__checkb=ttk.Checkbutton(self.__ios, text="-cs",variable=self.__var
     ,state = self.__check_button_state,onvalue=1,offvalue=0,command=lambda:self.__set_checkbox_value())
    self.__checkb.place(x=400,y=290)
    ttk.Button(self.__ios, text="Del", width=3,state='disabled' if not self.__prov_list else 'normal',
               command=lambda:self.__prov_list.pop() and self.__pop_out_listbox()).place(x=400, y=150)

  def __init_button(self):
      sv = StringVar()
      self.__listbox = Listbox(self.__ios, height=3, width=35, bg="grey30")
      self.__listbox.place(x=90, y=350)
      ativity_list= ['Sign-Ipa(*.ipa)SignIPA', 'DEV-Sign\n(*.ipa,*.sh" File)', 'Antamp Resign\n(AuthVerifer)']
      activity_box = ttk.Combobox(self.__ios, values=ativity_list, width=17)
      activity_box.place(x=220, y=290)
      activity_box.bind("<<ComboboxSelected>>", lambda x: self.__activity_selection(activity_box.current()))
      activity_box.set('Activity Selection')

      ttk.Button(self.__ios, text="Select File..", width=17,command= lambda: self.__file_dialogs("ipa")).place(x=220, y=100)
      ttk.Button(self.__ios, text="Provision File..", width=17,command= lambda: self.__file_dialogs("prov")).place(x=220, y=150)
      ttk.Button(self.__ios, text="Upload P12 File..", width=17,command= lambda: self.__file_dialogs("p12")).place(x=220, y=200)
      sv.trace("w", lambda name, index, mode, sv=sv: self.__set_p12password(sv))
      keypass = ttk.Entry(self.__ios,width=17,show="\u2022",textvariable=sv)
      keypass.place(x=220, y=250)

  def __file_dialogs(self, value):
      if value == "ipa":
          ipa = filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("IPA Files","*.ipa"),("Bash Files","*.sh")))
          if ipa!='':
           self.__data_collection.update(FilePath=ipa)
      elif value == "prov":
          filename=filedialog.askopenfilename(initialdir="/", title=" Select file", filetypes=(("All", "*.*"),("mobileprovision","*.mobileprovision")))
          if filename != '':
              self.__prov_list.append(filename)
              self.__list_box_append(self.__prov_list[-1])
      else:
          p12 = filedialog.askopenfilename(initialdir="/", title="Select file", filetypes=(("All", "*.*"),("p12", "*.p12")))
          if p12 != '':
              self.__data_collection.update(P12=p12)

  def __check_valid_field(self):
      self.__data_collection.update(Provision=self.__prov_list if self.__prov_list else '')
      if self.__data_collection.get("FilePath") == '':
          return messagebox.showinfo(title="Warring", message="Missing file, Upload file")

      elif self.__data_collection.get("Active")=='':
         return messagebox.showinfo(title="Warring", message="Missing arguments\n Choose Active")

      elif self.__data_collection.get('Active')==0:
          if 'ipa' not in self.__data_collection.get('FilePath') or self.__data_collection.get('Provision')=='' or self.__data_collection.get('P12')=='' or self.__data_collection.get('Pass')=='':
              return messagebox.showinfo(title="Warring", message="Invalid arguments\n or Missing files,Enter(Provision,P12,Pass")

      elif self.__data_collection.get("Active")==1:
          if ".sh" not in self.__data_collection.get("FilePath") and ".ipa" not in self.__data_collection.get("FilePath"):
           return messagebox.showinfo(title="Warring", message="Invalid arguments\n Attach *.sh or IPA file")

      elif self.__data_collection.get("Active")==2:
           if ".ipa" not in self.__data_collection.get("FilePath"):
            return messagebox.showinfo(title="Warring", message="Invalid arguments\n Attach IPA file")

      if ".ipa" in self.__data_collection.get("FilePath"):
       self.__rename_output()
      logging.debug(self.__data_collection)
      ios_activity(self.__data_collection)

  def submit_button(self):
      ttk.Button(self.__ios, text='Submit',width=17, command=self.__check_valid_field).place(x=180, y=450)

  def __rename_output(self):
      filename = self.__data_collection.get("FilePath")
      if self.__data_collection.get("Active") == 0 or self.__data_collection.get('Active') == 1:
          self.__data_collection.update(
              FileOut=filename[:filename.index(".ipa")] + "_Resigned" + filename[filename.index(".ipa"):])
      else:
          self.__data_collection.update(
              FileOut=filename[:filename.index(".ipa")] + "_Tempered" + filename[filename.index(".ipa"):])

  def __list_box_append(self,filename='None/'):
    self.__listbox.insert(self.__provision_count,filename[filename.rfind('/')+1:])
    self.__provision_count+=1
    self.__init_lables()

  def __activity_selection(self, param):
      self.__data_collection.update(Active=int(param))
      if param != 0:
         self.__check_button_state='disabled'
         self.__data_collection.update(ct='')
         if self.__var.get() == 1:
            self.__checkb.invoke()
      else:
          self.__check_button_state = 'normal'
      self.__init_lables()

  def __set_checkbox_value(self):
      logging.debug(self.__data_collection)
      self.__data_collection.update(ct='-cs' if self.__var.get() == 1 else '')

  def __pop_out_listbox(self):
      self.__listbox.delete(len(self.__prov_list), 'end')
      self.__init_lables()

  def __set_p12password(self,val):
      self.__data_collection.update(Pass=val.get())
