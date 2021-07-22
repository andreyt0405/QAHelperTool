import logging
from time import sleep
import subprocess
import os
from os import getenv
import tkinter

BIN_PATH = getenv('BIN', '')
DEV_ENV_PATH = getenv('DEV_ENV_PATH', '')

class android_apk_activity():
    def __init__(self, collection):
        self.__collection = collection
        logging.basicConfig(level=logging.INFO)
        self.__ext=self.__collection.get('FilePath')[-3:]
        self.__build_tools = os.listdir(os.path.expanduser('~/Library/Android/sdk/build-tools/'))[-1]
        self.__keyPass = ''
        self.__keystore = self.__setKeyStoreAndPass()
        self.__script_path = BIN_PATH
        self.__filter_By_data()

    def __filter_By_data(self):
        if self.__collection.get('Active')==0:
           self.__android_uninstall()
        elif self.__collection.get('Active')==1:
             self.__apk_install_upgarde()
        elif self.__collection.get('Active')==2:
             self.__apk_resign()
        elif self.__collection.get('Active')==3:
             self.__apk_private()
        elif self.__collection.get('Active')==4:
             self.__dev_sign()
        elif self.__collection.get('Active')==5:
             self.__apksigner_sign()

    def __apk_install_upgarde(self):
        logging.info("Adb initializing..\n {}".format(self.__collection.get("FilePath")))
        if self.__collection.get('Active')==0:
         subprocess.call('adb install {}'.format(self.__collection.get("FilePath")),shell=True)
        else:
            subprocess.call('adb install -r {}'.format(self.__collection.get("FilePath")), shell=True)

    def __android_uninstall(self):
     if self.__collection.get("Bundle") == True:
        logging.info('Uninstalling bundle package...')
        subprocess.call('adb uninstall {}'.format(self.__aapt_bundle_id(self.__collection.get("FilePath"))),shell=True)
     sleep(3)
     self.__apk_install_upgarde()

    def __setKeyStoreAndPass(self):
            self.__keyPass = self.__collection.get("KeyStorePass")
            if self.__collection.get("KeyStore")!='':
               return self.__collection.get("KeyStore")
            else:
                if self.__collection.get("Sign") == "Appdome":
                    return DEV_ENV_PATH + "/Certs/AndroidCertificate/appdome.keystore"
                elif self.__collection.get("Sign") == "OpenSource":
                    return DEV_ENV_PATH + "/Certs/AndroidCertificate/opensource/opensource.keystore"
                else:
                    return DEV_ENV_PATH + "/Certs/AndroidCertificate/timecard/gil.keystore"

    def __apk_resign(self):
         subprocess.call("export PATH=$PATH::~/Library/Android/sdk/build-tools/{}/ && cd {} && python signApk.py -k {} -kp {} -ka {} -kyp {} -o {} {}"
                   .format(self.__build_tools,self.__script_path,self.__keystore, self.__keyPass, self.__keyPass, self.__keyPass, self.__collection.get("FileOut"), self.__collection.get("FilePath")),shell=True)


    def __apk_private(self):
        try:
         subprocess.call(
            "export PATH=$PATH::~/Library/Android/sdk/build-tools/{}/ && cd {} && python privateSignApk.py -k {} -kp {} -ka {} -kyp {} -o {} {}"
            .format(self.__build_tools,self.__script_path,self.__keystore, self.__keyPass, self.__keyPass, self.__keyPass, self.__collection.get("FileOut"), self.__collection.get("FilePath")),shell=True)
         tkinter.messagebox.showinfo("showinfo", "Signing Completed")
        except:
            logging.error("Expected error,the process stopped,check the arguments")

    def __dev_sign(self):
        try:
         op = self.__collection.get('FilePath')[:self.__collection.get('FilePath').rfind('/')]
         os.chmod('{}'.format(self.__collection.get("FilePath")), 0o755)
         subprocess.call(
            "export PATH=$PATH::~/Library/Android/sdk/build-tools/{}/ && {} -o "
            "{}/A-uto_Dev_signed.apk -k {} -kp {} -kyp {} -ka {}".format(self.__build_tools,self.__collection.get("FilePath"),op,self.__keystore,self.__keyPass,self.__keyPass,self.__keyPass),shell=True)
         tkinter.messagebox.showinfo("showinfo", "Signing Completed")
        except:
            logging.error("Expected error,the process stopped,check the arguments")

    def __aapt_bundle_id(self,file_path):
        "aapt dump badging <path-to-apk> | grep package:\ name "
        "By using aapt Android tool extract the apk bundle id"

        os.chmod('aapt', 0o755)
        logging.info('Attempting extract package ID...')
        subprocess_return = subprocess.check_output("./aapt dump badging {} | grep package:\ name".format(file_path)).split(" ")[1]
        return subprocess_return[subprocess_return.index("'"):]


    def __apksigner_sign(self):
        subprocess.call('cd && ./Library/Android/sdk/build-tools/{}/apksigner sign --ks {} --ks-pass pass:{} --ks-key-alias {} --key-pass pass:{} --v2-signing-enabled {}'
                        .format(self.__build_tools,self.__keystore,self.__keyPass,self.__keyPass,self.__keyPass,self.__collection.get("FileOut")),shell=True,stdout=subprocess.PIPE)
        sleep(3)
        subprocess.call("cd && ./Library/Android/sdk/build-tools/{}/zipalign -f 4 {} {}".format(self.__build_tools,self.__collection.get("FilePath"),self.__collection.get("FileOut"))
                        ,shell=True,stdout=subprocess.PIPE)
        tkinter.messagebox.showinfo("showinfo", "Signing Completed")
