import subprocess
from os import getenv
import os
from sh1_menu import sh1_menu
import logging

BIN_PATH = getenv('BIN', '')
class ios_activity():
    def __init__(self, collection):
        self.__data_collection = collection
        logging.basicConfig(level=logging.INFO)
        self.__p12_path = self.__data_collection.get("P12")
        self.__p12_pass = self.__data_collection.get("Pass")
        self.__sign_ipa_path = BIN_PATH
        self.__filterBydata()


    def __filterBydata(self):
        if self.__data_collection.get("Active") == 0 :
            self.__sign_ipa()
        elif self.__data_collection.get("Active") == 1 :
            self.__dev_singature()
        else: self.__antamp_resign()

    def __sign_ipa(self):
        prov_string=" "
        prov_string=prov_string.join(self.__data_collection.get('Provision'))
        try:
            logging.info(prov_string)
            subprocess.call("cd {} && python signIpa.py -ct {} -ctp {} -pr {} {} -o "
                        "{} {} --apple_root_pem "
                        "AppleIncRootCertificate.pem --apple_wwd_pem AppleWWDRCA.pem".format(self.__sign_ipa_path,self.__p12_path,self.__p12_pass,prov_string,
                         self.__data_collection.get('ct'),self.__data_collection.get("FileOut"),self.__data_collection.get("FilePath")),shell=True)
        except:
            logging.error("Expected error,the process stopped,check the arguments")

    def __dev_singature(self):
        out_path=self.__data_collection.get('FilePath')[:self.__data_collection.get('FilePath').rfind('/')]
        subprocess.call(["security find-identity -v -p codesigning | cut -c 6- | uniq  &> {}/keychains.txt".format(os.getcwd())],shell=True)
        logging.info('sh1 selection window opened')
        sh1 = sh1_menu()
        get_sh = sh1.selected_sh
        subprocess.call("python {}/privateSignIpa.py {} -s {} -o {}/AutoDev_signed.ipa".format(self.__sign_ipa_path,self.__data_collection.get("FilePath"),get_sh,out_path), shell=True)
    def __antamp_resign(self):
        try:
            subprocess.call("Python antamp_tester.py -i {} -o {}".format(self.__data_collection.get("FilePath"),self.__data_collection.get("FileOut")),shell=True)
        except:
            logging.error("Expected error,the process stopped,check the arguments")