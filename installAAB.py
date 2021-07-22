import argparse
import logging
import os
from pathlib import Path


class aab(object):
    def __init__(self, filePath, outputPath, mode, keyStorePath, keyStorePass, keyStoreAlias, keyPass,
                 disableConnectedDevice, install):
        """
        :param filePath: path to the AAB file
        :param outputPath: path to the output file
        :param mode: apks output mode
        :param keyStorePath: path to the keystore file
        :param keyStorePass: keystore password
        :param keyStoreAlias: keystore alias
        :param keyPass: key password
        :param disableConnectedDevice: disable the connected device option
        :param install: install on device option
        """
        self.filePath = os.path.expanduser(filePath)
        if outputPath:
            self.outputPath = os.path.expanduser(outputPath)
        else:
            self.outputPath = os.path.expanduser(self.getOutputPath())
        self.mode = mode
        self.keyStorePath = os.path.expanduser(keyStorePath)
        self.keyStorePass = keyStorePass
        self.keyStoreAlias = keyStoreAlias
        self.keyPass = keyPass
        self.disableConnectedDevice = disableConnectedDevice

        self.extractAPK()
        if install:
            self.installAPK()

        logging.info('Script Finished successfully')

    def getOutputPath(self):
        logging.info('Getting default output path')
        aabDirectory = os.path.dirname(self.filePath)
        aabFileName = Path(self.filePath).stem
        outputPath = aabDirectory + '/' + aabFileName + '.apks'
        return outputPath

    def extractAPK(self):
        logging.info('Extracting APKs from AAB')
        if self.disableConnectedDevice:
            extractResult = os.system(
                'java -jar bundletool.jar build-apks --bundle="' + self.filePath + '" --output="' + self.outputPath + '" --overwrite --mode=' + self.mode + ' --ks=' + self.keyStorePath + ' --ks-pass=pass:' + self.keyStorePass + ' --ks-key-alias=' + self.keyStoreAlias + ' --key-pass=pass:' + self.keyPass)
        else:
            extractResult = os.system(
                'java -jar bundletool.jar build-apks --connected-device --bundle="' + self.filePath + '" --output="' + self.outputPath + '" --overwrite --mode=' + self.mode + ' --ks=' + self.keyStorePath + ' --ks-pass=pass:' + self.keyStorePass + ' --ks-key-alias=' + self.keyStoreAlias + ' --key-pass=pass:' + self.keyPass)
        if extractResult != 0:
            raise Exception('Failed to extract APKs!!!')

    def installAPK(self):
        logging.info('Installing APK on device')
        installResult = os.system(
            'java -jar bundletool.jar install-apks --apks="' + self.outputPath + '"')
        if installResult != 0:
            raise Exception('Failed to install APK on device!!!')


def main():
    parser = argparse.ArgumentParser(description='Times citi app',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-f', '--file', required=True, help="full path to the AAB file")
    parser.add_argument('-o', '--output', required=False, default=False, help="full path to the output file")
    parser.add_argument('-m', '--mode', required=False, default="default", help="apks output mode (universal, default)")
    parser.add_argument('-ks', '--key_store', required=True, help="full path to the key store file")
    parser.add_argument('-ksp', '--ks_pass', required=True, help="key store password")
    parser.add_argument('-ksa', '--ks_alias', required=True, help="key store alias")
    parser.add_argument('-kp', '--key_pass', required=True, help="key password")
    parser.add_argument('-dcd', '--disable_connected_device', required=False, default=False,
                        help="disable connected device option", action='store_true')
    parser.add_argument('-i', '--install', required=False, default=False, help="install on device", action='store_true')
    parser.add_argument('-d', '--debug', required=False, help="debug mode", action='store_true')

    arguments = parser.parse_args()

    if arguments.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.INFO)

    aab(arguments.file, arguments.output, arguments.mode, arguments.key_store, arguments.ks_pass, arguments.ks_alias,
        arguments.key_pass, arguments.disable_connected_device, arguments.install)


if __name__ == "__main__":
    main()