import argparse
from shutil import move, copyfile

from zipHandler import ZipHandler
from logger import logger
from json import load as json_load
from os import getenv, makedirs, getcwd, stat
from os.path import exists, basename, join, abspath
from modify_zip import add_file, erasedTempDir, modify_file, replace_file
import subprocess
from xml.etree import ElementTree

DEV_ENV_PATH = getenv('DEV_ENV_PATH', '')
BIN_PATH = getenv('BIN', '')
ANDROID_MANIFEST_FILE = 'AndroidManifest.xml'
XML_SCHEME_PREFIX = "http://schemas.android.com/apk/res/"
ANDROID_XML_SCHEME = XML_SCHEME_PREFIX + 'android'
MANIFEST_XML_PREFIX = '{' + ANDROID_XML_SCHEME + '}'
MANIFEST_XML_NAME = MANIFEST_XML_PREFIX + 'name'

def parse_arguments():
    parser = argparse.ArgumentParser(description='adds a file to an existing zip file',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-i", "--input", required=True, help='Path to fused .ipa/apk/aab file')
    parser.add_argument("-j", "--json", required=True, help='json file that defines all the action to do')
    parser.add_argument("-o", "--output", required=True, help='output dir to put all output files in')
    return parser.parse_args()

def open_apktool(input_file, apktool_output, android_manifest_bak, cur_data, is_aab):

    android_manifest_path = join(apktool_output, ANDROID_MANIFEST_FILE)
    if exists(android_manifest_bak):
        logger.debug("copying android manifest from " + android_manifest_bak + " to " + android_manifest_path)
        copyfile(android_manifest_bak, android_manifest_path)
    else:
        if is_aab:
            logger.info("got aab. using bundletool to change it to universal apk")
            key_alias, key_password, keystore, keystore_password = get_android_sign_profile(cur_data)
            apks_output = apktool_output + '.apks'
            cmd = ['bundletool', 'build-apks', '--bundle=' + input_file, '--output=' + apks_output, '--mode=universal']
            cmd.append('--ks=' + keystore)
            cmd.append('--ks-pass=pass:' + keystore_password)
            cmd.append('--ks-key-alias=' + key_alias)
            cmd.append('--key-pass=pass:' + key_password)
            cmd_str = " ".join(cmd)
            logger.info("running cmd - " + cmd_str)
            ret = subprocess.call(cmd_str, shell=True)
            logger.info("ret=" + str(int(ret)))
            if ret == 0:
                apks_handler = ZipHandler(apks_output)
                logger.info("extracting universal apk to dir input_universal_apk")
                universal_output = apktool_output + 'universal'
                apks_handler.extract('universal.apk', universal_output)
                base_apk_input = join(universal_output, 'universal.apk')
            else:
                logger.error("failed to turn aab to apks. exit")
                return False
        else:
            base_apk_input = input_file

        logger.info("using apktool to get text files")
        cmd = ['apktool', 'd', '--only-main-classes', base_apk_input, '-f', '-o', apktool_output]
        cmd.append('--no-src')
        cmd_str = " ".join(cmd)
        logger.info("running cmd - " + cmd_str)
        ret = subprocess.call(cmd_str, shell=True)
        logger.info("ret=" + str(int(ret)))
        logger.debug("making android manifest backup to " + android_manifest_bak)
        copyfile(android_manifest_path, android_manifest_bak)


def close_apktool(apktool_output, temp_output_path):
    cmd = ['apktool', "b", "-f", apktool_output, "-o", temp_output_path]
    cmd_str = " ".join(cmd)
    logger.info("running cmd - " + cmd_str)
    ret = subprocess.call(cmd_str, shell=True)
    logger.info("ret=" + str(int(ret)))

def main():
    if not DEV_ENV_PATH or not BIN_PATH:
        logger.error("need to set environment val DEV_ENV_PATH and BIN")
        exit(1)
    with erasedTempDir() as temp_dir:
        cur_dir = getcwd()
        script_args = parse_arguments()
        with open(script_args.json) as f:
            tests_json = json_load(f)
        input_file = script_args.input
        input_file_name = basename(input_file)
        output_dir = script_args.output
        if not exists(output_dir):
            makedirs(output_dir)
        test_data = tests_json["data"]
        platform = get_platform(tests_json)
        apktool_output = join(temp_dir, input_file_name + "_apktool")
        # android manifest will be changed in apktool_output, so keep the manifest here
        android_manifest_bak = join(temp_dir, input_file_name + "_apktool_" + ANDROID_MANIFEST_FILE)
        android_manifest = join(apktool_output, ANDROID_MANIFEST_FILE)

        if platform == "android":
            is_aab = True if "is_aab" in tests_json and tests_json["is_aab"] == "true" else False
            if is_aab:
                logger.info("in aab platform")
            else:
                logger.info("in apk platform")

        for cur_data in test_data:
            test_name = str(cur_data["test_name"])
            test_file_full_name = test_name + "_" + input_file_name
            temp_output_path = join(temp_dir, test_file_full_name)
            output_path = join(cur_dir, output_dir, test_file_full_name)
            if "action" in cur_data:
                logger.debug("action=" + str(cur_data["action"]))
                if cur_data["action"] == "add_file":
                    location_in_zip = str(cur_data["location_in_zip"])
                    logger.debug("location_in_zip=" + location_in_zip)
                    if "file_to_add" in cur_data:
                        file_to_add = str(cur_data["file_to_add"])
                    else:
                        file_to_add = ""
                    add_file(input_file, temp_output_path, file_to_add, location_in_zip)
                elif cur_data["action"] == "replace_file":
                    location_in_zip = str(cur_data["location_in_zip"])
                    logger.debug("location_in_zip=" + location_in_zip)
                    file_to_add = str(cur_data["new_file"])
                    replace_file(input_file, temp_output_path, file_to_add, location_in_zip)
                elif cur_data["action"] == "modify_file":
                    location_in_zip = str(cur_data["location_in_zip"])
                    location_in_file = int(cur_data["location_in_file"])
                    char_to_put = str(cur_data["char_to_put"])

                    logger.debug("location_in_zip=" + location_in_zip + ", location_in_file=" + str(
                        location_in_file) + ", char_to_put=" + str(char_to_put))
                    modify_file(input_file, temp_output_path, location_in_zip, location_in_file, char_to_put)
                elif cur_data["action"] == "manifest_add":
                    field = str(cur_data["field"])
                    name = str(cur_data["name"])
                    extra_properties = cur_data["extra_properties"]
                    open_apktool(input_file, apktool_output, android_manifest_bak, cur_data, is_aab)
                    logger.debug(ANDROID_MANIFEST_FILE + " size=" + (str(stat(android_manifest).st_size)))
                    ElementTree.register_namespace('android', ANDROID_XML_SCHEME)

                    src_manifest_tree_main = ElementTree.parse(android_manifest)
                    src_manifest_root = src_manifest_tree_main.getroot()
                    logger.info("before change - " + ElementTree.tostring(src_manifest_root, encoding='utf8').decode('utf8'))
                    logger.info((src_manifest_root.tag + ": " + str(src_manifest_root.attrib)))

                    new_elem = ElementTree.SubElement(src_manifest_root, field)
                    new_elem.set(MANIFEST_XML_NAME, name)
                    for key, value in extra_properties.items():
                        new_elem.set(MANIFEST_XML_PREFIX + key, value)

                    logger.info("after change root - " + ElementTree.tostring(src_manifest_root, encoding='utf8').decode('utf8'))
                    for child in src_manifest_root:
                        logger.info((child.tag + ": " + str(child.attrib)))
                    logger.info("writing modified android manifest back to " + android_manifest)
                    src_manifest_tree_main.write(android_manifest, encoding="utf-8", xml_declaration=True)

                    modified_manifest_apk = join(temp_dir, 'modified_manifest_' + test_file_full_name)
                    logger.info("writing apk with modified " + ANDROID_MANIFEST_FILE + " to " + modified_manifest_apk)
                    close_apktool(apktool_output, modified_manifest_apk)

                    logger.info("extracting modified binary " + ANDROID_MANIFEST_FILE + " to " + temp_dir)
                    zipHandler = ZipHandler(modified_manifest_apk)
                    zipHandler.extract(ANDROID_MANIFEST_FILE, temp_dir)
                    logger.debug("writing modified android manifest to " + temp_output_path)
                    replace_file(input_file, temp_output_path, join(temp_dir, ANDROID_MANIFEST_FILE), ANDROID_MANIFEST_FILE)
                else:
                    logger.error("can't find action " + str(cur_data["action"]))
            else:
                logger.info("no action found for test " + test_name + ". signing")
                temp_output_path = abspath(input_file)
            logger.debug("profile=" + str(cur_data["profile"]))
            sign_app(platform, cur_data, temp_output_path, output_path)

    # if script_args.char_to_put is not None:
    #     modify_file(script_args.input, script_args.output, script_args.location, script_args.location_in_file, script_args.char_to_put)
    # else:
    #     add_file(script_args.input, script_args.output, script_args.file, script_args.location)




def sign_app(platform, cur_data, temp_output_path, output_path):
    if platform == "ios":
        try:
            p12_pass, p12_path, prov_string = get_ios_provisioning_profile(cur_data)
            cmd = "cd {} && python signIpa.py -ct {} -ctp {} {} -o {} -pr {} --apple_root_pem " \
                  "AppleIncRootCertificate.pem --apple_wwd_pem AppleWWDRCA.pem".format(BIN_PATH,
                                                                                       p12_path,
                                                                                       p12_pass,
                                                                                       temp_output_path,
                                                                                       output_path,
                                                                                       prov_string)
            logger.info("running cmd - " + cmd)
            subprocess.call(cmd, shell=True)
        except:
            logger.error("received error from ios sign process, exiting")
            exit(1)

    elif platform == "android":
        try:
            key_alias, key_password, keystore, keystore_password = get_android_sign_profile(cur_data)

            cmd = "cd {} && python signApk.py -k {} -kp {} -ka {} -kyp {} -o {} {}".format(BIN_PATH,
                                                                                           keystore,
                                                                                           keystore_password,
                                                                                           key_alias,
                                                                                           key_password,
                                                                                           output_path,
                                                                                           temp_output_path)
            logger.info("running cmd - " + cmd)
            subprocess.call(cmd, shell=True)
        except:
            logger.error("received error from ios sign process, exiting")
            exit(1)
    else:
        logger.info("not signing file " + output_path)
        move(temp_output_path, output_path)

    logger.info(" ----------- " + output_path + " --------------")


def get_android_sign_profile(cur_data):
    with open(cur_data["profile"]) as p:
        sign_profile = json_load(p)
    keystore = join(DEV_ENV_PATH, sign_profile["keystore"])
    keystore_password = sign_profile["keystore_password"]
    key_alias = sign_profile["key_alias"]
    key_password = sign_profile["key_password"]
    return key_alias, key_password, keystore, keystore_password


def get_ios_provisioning_profile(cur_data):
    with open(cur_data["profile"]) as p:
        sign_profile = json_load(p)
    prov_list = [join(DEV_ENV_PATH, pr) for pr in sign_profile["provisioning"]]
    prov_string = " ".join(prov_list)
    p12_path = join(DEV_ENV_PATH, sign_profile["certificate"])
    p12_pass = sign_profile["password"]
    return p12_pass, p12_path, prov_string


def get_platform(tests_json):
    if "platform" not in tests_json:
        logger.error("json script need to contain platform(ios or android)")
        exit(1)
    platform = tests_json["platform"]
    if platform == "android":
        logger.info("android test")
    elif platform == "ios":
        logger.info("ios test")
    else:
        logger.error("current platform = '" + str(platform) + "', need to put 'android' or 'ios'")
        exit(1)
    return platform


if __name__ == "__main__":
    main()