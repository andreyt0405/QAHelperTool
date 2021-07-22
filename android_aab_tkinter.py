import logging
from future.moves.tkinter import messagebox
from tkinter import filedialog
from tkinter import *
from tkinter import ttk
from android_aab_activity import android_aab_activity
is_on = False
class android_aab_tkinter:

  def __init__(self,root):
    logging.basicConfig(level=logging.DEBUG)
    self.__root=root
    self.__keystore_state='normal'
    self.__key_alias_state='normal'
    self.__keyPass_state='normal'
    self.__data_collection= {"Active":'', "FilePath":'', "FileOut":'', "Sign":'', "KeyStore":'',"KeyStorePass":'',"Alias":'',"KeyPass":''}
    self.__android_aab = ttk.Frame(self.__root)
    self.__root.add(self.__android_aab, text='Android AAB')
    self.__root.pack(expand=1, fill="both")
    self.__init_lables()
    self.__init_object()
    self.__combobox_singature()
    self.__keystore_button()
    self.__submit_button()

  def __init_lables(self):
    ttk.Label(self.__android_aab, text="Android AAB", font=("bold", 20), background='dodgerblue4').place(x=90, y=30)
    ttk.Label(self.__android_aab, text="Upload APK/ABB", width=20, font=("bold", 14)).place(x=60, y=100)
    ttk.Label(self.__android_aab, text="Select Activty", width=20, font=("bold", 14)).place(x=60, y=140)
    ttk.Label(self.__android_aab, text="Upload KeyStore", font=("bold", 14), background='dark slate grey').place(x=60, y=220)
    ttk.Label(self.__android_aab, text="Select Sign", font=("bold", 14), background='dark slate grey').place(x=60, y=260)
    ttk.Label(self.__android_aab, text="Password KeyStore", font=("bold", 14), background='wheat4').place(x=60, y=300)
    ttk.Label(self.__android_aab, text="Keystore Alias", font=("bold", 14), background='wheat4').place(x=60, y=340)
    ttk.Label(self.__android_aab, text="Key Password", font=("bold", 14), background='wheat4').place(x=60, y=380)

  def __submit_button(self):
      ttk.Button(self.__android_aab, text='Submit', command=self.__validation_filed, width=17).place(x=180, y=450)

  def __combobox_singature(self):
      list_signature= ['Appdome', 'OpenSource', 'TimeCard', 'Select KeyStore...']
      cbox = ttk.Combobox(self.__android_aab, values=list_signature, width=15)
      cbox.place(x=240, y=260)
      cbox.bind("<<ComboboxSelected>>", lambda x: self.__set_sign_type(cbox.current()))
      cbox.set('Select Sign')

  def __keystore_button(self):
      ttk.Button(self.__android_aab, text="Select KeyStore...", state=self.__keystore_state, width=17, command= lambda: self.__file_dialogs(1)).place(x=240, y=220)

  def __init_object(self):
      if self.__data_collection.get("Active")=='':
        ativity_list= ['AAB Install(installAAB)','Dev-Signature(*.sh)',"Extract Universal(APK)","JarSigner(*.AAB)"]
        activity_box = ttk.Combobox(self.__android_aab, values=ativity_list, width=17)
        activity_box.place(x=240, y=140)
        activity_box.bind("<<ComboboxSelected>>", lambda x: self.__activity_selection(activity_box.current()))
        activity_box.set('Activity Selection')

      KEYSTORE_PASS = StringVar()
      KEYSTORE_PASS.trace("w", lambda name, index, mode, sv=KEYSTORE_PASS: self.__set_keystorepass(sv))
      keystorepass = ttk.Entry(self.__android_aab,show="\u2022", textvariable=KEYSTORE_PASS, width=17)
      keystorepass.place(x=240, y=300)

      ALIAS_VAR = StringVar()
      ALIAS_VAR.trace("w", lambda name, index, mode, sv=ALIAS_VAR: self.__set_alias(sv))
      alias = ttk.Entry(self.__android_aab, state=self.__key_alias_state,show="\u2022", textvariable=ALIAS_VAR, width=17)
      alias.place(x=240, y=340)

      KEY_PASS_VAR = StringVar()
      KEY_PASS_VAR.trace("w", lambda name, index, mode, sv=KEY_PASS_VAR: self.__set_keyPass(sv))
      keyPass = ttk.Entry(self.__android_aab, state=self.__keyPass_state,show="\u2022", textvariable=KEY_PASS_VAR, width=17)
      keyPass.place(x=240, y=380)

      ttk.Button(self.__android_aab, text="Select File...", width=17, command= lambda: self.__file_dialogs(0)).place(x=240, y=100)


  def __file_dialogs(self, value):
      if(value == 0):
       filename = filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("AAB Files","*.aab"),("Bash Files","*.sh")))
       if filename != '':
          self.__data_collection.update(FilePath=filename)
      else:
       keystore = filedialog.askopenfilename(initialdir="/", title="Select file")
       if keystore != '':
          self.__data_collection.update(KeyStore=keystore)
  def __extract_file_out(self):
    if self.__data_collection.get("FilePath") != '':
       filename = self.__data_collection.get("FilePath")
       if self.__data_collection.get("Active")==0:
               return filename[:filename.index(".aab")] + "Tampered" + filename[filename.index(".aab"):]
       if self.__data_collection.get("Active")==1:
               return filename[:filename.index(".sh")] + "Singed.aab"
       if self.__data_collection.get("Active")==3:
               return filename[:filename.index(".aab")] + "JarSinged.aab"

  def __set_sign_type(self,value):
      if value != 3:
       self.__data_collection.update(Sign='Appdome' if value==0 else 'OpenSource' if value==1 else 'TimeCard')
       self.__data_collection.update(KeyStore='')
       self.__data_collection.update(Alias='')
       self.__data_collection.update(KeyPass='')
       self.__keystore_state = 'disabled'
       self.__key_alias_state = 'disabled'
       self.__keyPass_state = 'disabled'
      else:
          self.__keystore_state = 'normal'
          self.__key_alias_state = 'normal'
          self.__keyPass_state = 'normal'
          self.__data_collection.update(Sign='')
      self.__keystore_button()
      self.__init_object()

  def __activity_selection(self,val):
      self.__data_collection.update(Active=int(val))

  def __set_keystorepass(self,val):
      self.__data_collection.update(KeyStorePass=val.get())
  def __set_alias(self,val):
      self.__data_collection.update(Alias=val.get())
  def __set_keyPass(self,val):
      self.__data_collection.update(KeyPass=val.get())

  def __validation_filed(self):
      if self.__data_collection.get('FilePath') == '':
          return messagebox.showinfo(title="Warring", message="Upload file(*.AAB,*.sh)")

      if self.__data_collection.get('Active')=='':
          return messagebox.showinfo(title="Warring", message="Missing arguments\n Choose Activity")

      if (self.__data_collection.get('Sign')=='' and self.__data_collection.get('KeyStore')=='')\
              or self.__data_collection.get('KeyStorePass')=='':
                 return messagebox.showinfo(title="Warring", message="Missing Arguments")
      if self.__data_collection.get('Active')==0:
          if '.aab' not in self.__data_collection.get('FilePath'):
              return messagebox.showinfo(title="Warring", message="Invalid file\nUpload AAB")

      if self.__data_collection.get('Active')==1:
         if '.sh' not in self.__data_collection.get('FilePath'):
             return messagebox.showinfo(title="Warring", message="Invalid file\nUpload *.sh file")

      if self.__data_collection.get('Active') == 2:
          if '.aab' not in self.__data_collection.get('FilePath'):
              return messagebox.showinfo(title="Warring", message="Invalid arguments\nAAB,Sign,Keystore,KeyPass")

      if self.__data_collection.get('Active') == 3:
          if '.aab' not in self.__data_collection.get('FilePath'):
              return messagebox.showinfo(title="Warring", message="Invalid arguments\nAAB,Sign,Keystore,KeyPass")

      if self.__data_collection.get('Alias')=='':
          self.__data_collection.update(Alias=self.__data_collection.get('KeyStorePass'))

      if self.__data_collection.get('KeyPass') == '':
          self.__data_collection.update(KeyPass=self.__data_collection.get('KeyStorePass'))


      self.__data_collection.update(FileOut=self.__extract_file_out())
      logging.debug(self.__data_collection)
      android_aab_activity(self.__data_collection)