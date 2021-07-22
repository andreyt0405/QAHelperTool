import logging
from future.moves.tkinter import messagebox
from tkinter import filedialog
from tkinter import *
from tkinter import ttk
from android_apk_activity import *
is_on = False
class android_apk_tkinter:

  def __init__(self,root):
    logging.basicConfig(level=logging.DEBUG)
    self.__root=root
    self.__keystore_state='normal'
    self.__data_collection= {"Active":'', "FilePath":'', "FileOut":'', "Sign":'', "Bundle":False, "KeyStore":'',"KeyStorePass":''}
    self.__android_apk = ttk.Frame(self.__root)
    self.__root.add(self.__android_apk, text='Android APK')
    self.__root.pack(expand=1, fill="both")
    self.__init_lables()
    self.__init_object()
    self.__combobox_singature()
    self.__keystore_button()
    self.__submit_button()

  def __init_lables(self):
    ttk.Label(self.__android_apk, text="Android APK", font=("bold", 20), background='dodgerblue4').place(x=90, y=30)
    ttk.Label(self.__android_apk, text="Upload APK/ABB", width=20, font=("bold", 14)).place(x=60, y=100)
    ttk.Label(self.__android_apk, text="Select Activty", width=20, font=("bold", 14)).place(x=60, y=140)
    ttk.Label(self.__android_apk, text="Upload KeyStore", font=("bold", 14), background='dark slate grey').place(x=60, y=220)
    ttk.Label(self.__android_apk, text="Select Sign", font=("bold", 14), background='dark slate grey').place(x=60, y=260)
    ttk.Label(self.__android_apk, text="Password KeyStore", font=("bold", 14), background='dark slate grey').place(x=60, y=300)
    ttk.Label(self.__android_apk, text="Uninstall Bundle", width=20, font=("bold", 14)).place(x=60, y=360)

  def __submit_button(self):
      ttk.Button(self.__android_apk, text='Submit', command=self.__validation_filed, width=17).place(x=180, y=450)

  def __combobox_singature(self):
      list_signature= ['Appdome', 'OpenSource', 'TimeCard', 'Select KeyStore...']
      cbox = ttk.Combobox(self.__android_apk, values=list_signature, width=15)
      cbox.place(x=240, y=260)
      cbox.bind("<<ComboboxSelected>>", lambda x: self.__set_sign_type(cbox.current()))
      cbox.set('Select Sign')

  def __keystore_button(self):
      ttk.Button(self.__android_apk, text="Select KeyStore...", state=self.__keystore_state, width=17, command= lambda: self.__file_dialogs(1)).place(x=240, y=220)

  def __init_object(self):
      ativity_list= ['APK Install','APK Upgrade(-r)','APK(SignAPK)', 'APK(*.apk)PrivateSign','Dev-Signature(*.sh)',"apksigner(Apksigner sign)"]
      activity_box = ttk.Combobox(self.__android_apk, values=ativity_list, width=17)
      activity_box.place(x=240, y=140)
      activity_box.bind("<<ComboboxSelected>>", lambda x: self.__activity_selection(activity_box.current()))
      activity_box.set('Activity Selection')

      sv = StringVar()
      sv.trace("w", lambda name, index, mode, sv=sv: self.__set_keypass(sv))
      keypass = ttk.Entry(self.__android_apk, show="\u2022", textvariable=sv, width=17)
      keypass.place(x=240, y=300)

      photo = Image.Tk=PhotoImage(file=r"btn-off.png")
      ttk.Radiobutton(self.__android_apk, image = photo, command=self.__swtich).place(x=230, y=360)

      ttk.Button(self.__android_apk, text="Select File...", width=17, command= lambda: self.__file_dialogs(0)).place(x=240, y=100)


  def __file_dialogs(self, value):
      if(value == 0):
       filename = filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("Apk Files","*.apk"),("Bash Files","*.sh")))
       if filename != '':
          self.__data_collection.update(FilePath=filename)
      else:
       keystore = filedialog.askopenfilename(initialdir="/", title="Select file")
       if keystore != '':
          self.__data_collection.update(KeyStore=keystore)
  def __extract_file_out(self):
   if self.__data_collection.get("FilePath") != '' and self.__data_collection.get('Active')!=4 and (self.__data_collection.get('Active')!=0 and self.__data_collection.get('Active')!=1):
    filename = self.__data_collection.get("FilePath")
    if self.__data_collection.get("Active")==2 or  self.__data_collection.get("Active")==5 and '.apk' in self.__data_collection.get("FilePath"):
        if self.__data_collection.get("Active")==2:
            if ".apk" in self.__data_collection.get("FilePath"):
               return filename[:filename.index(".apk")] + "Tampered" + filename[filename.index(".apk"):]
        if self.__data_collection.get("Active")==5:
            return filename[:filename.index(".apk")] + "Apksigner" + filename[filename.index(".apk"):]
    elif self.__data_collection.get("Active")==3:
        if '.apk' in self.__data_collection.get('FilePath'):
           return filename[:filename.index(".apk")] + "Singed" + filename[filename.index(".apk"):]
        else:
            return filename[:filename.index(".sh")] + "Singed.apk"

  def __set_sign_type(self,value):
      if value != 3:
       self.__data_collection.update(Sign='Appdome' if value==0 else 'OpenSource' if value==1 else 'TimeCard')
       self.__data_collection.update(KeyStore='')
       self.__keystore_state = 'disabled'
      else:
          self.__keystore_state = 'normal'
          self.__data_collection.update(Sign='')
      self.__keystore_button()

  def __activity_selection(self,val):
      self.__data_collection.update(Active=int(val))

  def __set_keypass(self,val):
      self.__data_collection.update(KeyStorePass=val.get())

  def __swtich(self):
      global is_on
      if is_on == False:
          is_on=True
          self.__data_collection.update(Bundle=True)
          photo = Image.Tk = PhotoImage(file=r"btn-on.png")
          ttk.Radiobutton(self.__android_apk, image = photo, command=self.__swtich).place(x=230, y=360)
      else:
          is_on=False
          self.__data_collection.update(Bundle=False)
          photo = Image.Tk = PhotoImage(file=r"btn-off.png")
          ttk.Radiobutton(self.__android_apk, image = photo, command=self.__swtich).place(x=230, y=360)
      logging.debug(self.__data_collection)

  def __validation_filed(self):
      if self.__data_collection.get('FilePath') == '':
          return messagebox.showinfo(title="Warring", message="Upload APK file")

      if self.__data_collection.get('Active')=='':
          return messagebox.showinfo(title="Warring", message="Missing arguments\n Choose Active")
      if self.__data_collection.get('Active')==0:
          if '.apk' not in self.__data_collection.get('FilePath'):
              return messagebox.showinfo(title="Warring", message="Invalid file\nUpload APK")

      if self.__data_collection.get('Active')==1:
         if '.apk' not in self.__data_collection.get('FilePath'):
             return messagebox.showinfo(title="Warring", message="Invalid file\nUpload APK")

      if self.__data_collection.get('Active') == 2:
          if '.apk' not in self.__data_collection.get('FilePath') or (self.__data_collection.get('Sign')=='' and self.__data_collection.get('KeyStore')=='')\
              or self.__data_collection.get('KeyStorePass')=='':
              return messagebox.showinfo(title="Warring", message="Invalid arguments\nAPK,Sign,Keystore,KeyPass")

      if self.__data_collection.get('Active')==3:
          if '.apk' not in self.__data_collection.get('FilePath') or (self.__data_collection.get('Sign')=='' and self.__data_collection.get('KeyStore')=='')\
              or self.__data_collection.get('KeyStorePass')=='':
              return messagebox.showinfo(title="Warring", message="Missing arguments\nAPK,Sign,Keystore,KeyPass")

      if self.__data_collection.get('Active')==4:
          if '.sh' not in self.__data_collection.get('FilePath') or (self.__data_collection.get('Sign')=='' and self.__data_collection.get('KeyStore')=='') \
                  or self.__data_collection.get('KeyStorePass')=='':
              return messagebox.showinfo(title="Warring", message="Missing arguments\n(*.sh),Sign,Keystore,KeyPass")

      if self.__data_collection.get('Active') == 5:
          if '.apk' not in self.__data_collection.get('FilePath') or (
                  self.__data_collection.get('Sign') == '' and self.__data_collection.get('KeyStore') == '') \
                  or self.__data_collection.get('KeyStorePass') == '':
              return messagebox.showinfo(title="Warring", message="Missing arguments\nAPK,Sign,Keystore,KeyPass")

      self.__data_collection.update(FileOut=self.__extract_file_out())
      logging.debug(self.__data_collection)
      android_apk_activity(self.__data_collection)