import logging
import subprocess
import os
from os import getenv
import tkinter
import shlex
from subprocess import Popen, PIPE
from time import sleep

BIN_PATH = getenv('BIN', '')
DEV_ENV_PATH = getenv('DEV_ENV_PATH', '')

class android_aab_activity():
    def __init__(self, collection):
        self.__keystorePass = ''
        self.__alias = ''
        self.__keyPass= ''
        self.__collection = collection
        logging.basicConfig(level=logging.INFO)
        self.__ext=self.__collection.get('FilePath')[-3:]
        self.__build_tools = os.listdir(os.path.expanduser('~/Library/Android/sdk/build-tools/'))[-1]
        self.__keystore = self.__setKeyStoreAndPass()
        self.__script_path = BIN_PATH
        self.__filter_By_data()

    def __filter_By_data(self):
        if self.__collection.get('Active')==0:
           self.__aab_install()
        elif self.__collection.get('Active')==1:
             self.__dev_sign()
        elif self.__collection.get('Active')==2:
             self.__aab_to_apks()
        elif self.__collection.get('Active')==3:
             self.__abb_jarsigner()

    def __setKeyStoreAndPass(self):
            self.__keystorePass = self.__collection.get("KeyStorePass")
            self.__alias = self.__collection.get("Alias")
            self.__keyPass = self.__collection.get("KeyPass")
            if self.__collection.get("KeyStore")!='':
               return self.__collection.get("KeyStore")
            else:
                if self.__collection.get("Sign") == "Appdome":
                    return DEV_ENV_PATH + "/Certs/AndroidCertificate/appdome.keystore"
                elif self.__collection.get("Sign") == "OpenSource":
                    return DEV_ENV_PATH + "/Certs/AndroidCertificate/opensource/opensource.keystore"
                else:
                    return DEV_ENV_PATH + "/Certs/AndroidCertificate/timecard/gil.keystore"

    def __aab_install(self):
        logging.info("Adb initializing..\n {}".format(self.__collection.get("FilePath")))
        try:
            subprocess.call("python installAAB.py -ks {} -ksp {} -ksa {} -kp {} -i -f {}"
                            .format(self.__keystore, self.__keystorePass, self.__alias, self.__keyPass,
                                    self.__collection.get("FilePath")), shell=True)
        except:
            logging.error("Expected error,the process stopped,check the arguments")

    def __dev_sign(self):
        try:
         op = self.__collection.get('FilePath')[:self.__collection.get('FilePath').rfind('/')]
         os.chmod('{}'.format(self.__collection.get("FilePath")), 0o755)
         subprocess.call(
            "export PATH=$PATH::~/Library/Android/sdk/build-tools/{}/ && {} -o "
            "{}/Auto_Dev_signed.aab -k {} -kp {} -kyp {} -ka {}".format(self.__build_tools, self.__collection.get("FilePath"), op, self.__keystore, self.__keystorePass, self.__keyPass, self.__alias),shell=True)
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

    def __aab_to_apks(self):
        filename = self.__collection.get('FilePath')
        "Funcation extract from aab file the apk, copy apk to work direcoty and sending the apk to aapt"
        apks_file=os.path.splitext(filename)[0]+'.apks'
        try:
         os.remove(apks_file)
        except:
         logging.info("Package ID haven't found")

        subprocess.call("cd && bundletool build-apks --bundle={} --output={} \
        --ks={} --ks-pass=pass:{} --ks-key-alias={} --key-pass=pass:{} --mode=universal".format(filename, apks_file, self.__keystore, self.__keystorePass, self.__alias, self.__keyPass)
                        ,shell=True,stdout=subprocess.PIPE)


    def __abb_jarsigner(self):
        command = shlex.split(
            "keytool -list -v -keystore {} -alias {} -storepass {} -keypass {}".format(self.__keystore,self.__alias,self.__keystorePass,self.__keyPass))
        process = Popen(command, stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()
        stdout = str(stdout).split()
        output = stdout[stdout.index("algorithm")+2]
        output=output[:output.find("\\nSubject")]

        filename = self.__collection.get('FilePath')
        command = shlex.split('jarsigner {} -sigalg {} -digestalg SHA-256 -keystore {} {} -storepass {} -keypass {}'
                              .format(filename,output,self.__keystore,self.__alias,self.__keystorePass,self.__keyPass))
        Popen(command, stdout=PIPE, stderr=PIPE).communicate()
        sleep(3)
        subprocess.call("cd && ./Library/Android/sdk/build-tools/{}/zipalign -f 4 {} {}".format(self.__build_tools,self.__collection.get("FilePath"),self.__collection.get("FileOut"))
                        ,shell=True,stdout=subprocess.PIPE)
        tkinter.messagebox.showinfo("showinfo", "Signing Completed The sealed app was changed by signed app")