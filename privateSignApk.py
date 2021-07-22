import argparse
import re
from os import remove
from os.path import basename, splitext, abspath
from shutil import move, copy
from subprocess import Popen, PIPE
from sys import stderr as sys_stderr

PRIVATE_SIGNAPK_SCRIPT_NAME = splitext(basename(__file__))[0] + ".py"

SEALED_FINGERPRINT_VALUE = "SEALED_FINGERPRINT_PLACEHOLDER"
GOOGLE_PLAY_FINGERPRINT_VALUE = "GOOGLE_PLAY_FINGERPRINT_PLACEHOLDER"
PLACEHOLDER_INDICATION = "_"

IS_ANDROID_APP_BUNDLE_IN_SCRIPT = "IS_ANDROID_APP_BUNDLE_PLACEHOLDER"

SHA1_REGEX_IN_KEYTOOL_OUTPUT = "SHA1: ([1234567890ABCDEF:]{59})"
SHA1_LEN = 40
SHA256_REGEX_IN_KEYTOOL_OUTPUT = "SHA256: ([1234567890ABCDEF:]{95})"
SHA256_LEN = 64
APKSIGNER_VERIFY_STRING = 'Verifies'
JARSIGNER_VERIFY_STRING = 'jar verified.'


def apksigner_signing_command(input_file, output_file, keystore, keystore_pass, keystore_alias, key_pass):
    return ['apksigner', 'sign', '--ks', keystore, '--ks-pass', 'pass:' + keystore_pass,
            '--ks-key-alias', keystore_alias, '--key-pass', 'pass:' + key_pass, '--v2-signing-enabled',
            '--v1-signing-enabled', '--out', output_file, input_file]


def jarsigner_signing_command(input_file, keystore, keystore_pass, keystore_alias, key_pass):
    return ['jarsigner', input_file, '-sigalg', 'SHA256withRSA', '-digestalg', 'SHA-256', '-keystore', keystore,
            keystore_alias, '-storepass', keystore_pass, '-keypass', key_pass]


def apksigner_verify_command(file_path):
    return['apksigner', 'verify', '-v', '--print-certs', file_path]


def jarsigner_verify_command(file_path):
    return['jarsigner', '-verify', file_path]


def keytool_list_command_on_keystore(keystore, keystore_pass, keystore_alias):
    return ["keytool", "-list", "-v", "-keystore", keystore, "-storepass", keystore_pass, "-alias", keystore_alias]


def zipalign_command(input_file, ouput_file):
    return ["zipalign", "-f", "-v", "4", input_file, ouput_file]


def private_sign_apk_run_command(cmd, _stdin=None, _stdout=None, _stderr=None):
    try:
        p = Popen(cmd, stdin=_stdin, stdout=_stdout, stderr=_stderr)
        output, err = p.communicate()
        # in python 3 Popen returns output as bytes
        if type(output) == bytes:
            output = output.decode("utf-8")
        if type(err) == bytes:
            err = err.decode("utf-8")
        res = p.returncode
        if res != 0:
            err_str = "%s failed with error code: %s." % (cmd[0], str(res))
            if output:
                err_str += " Output: %s." % (output,)
            if err:
                err_str += " Error: %s." % (err,)
            private_sign_apk_die_with_error(err_str)
        return output, err
    except OSError as error:
        if isinstance(cmd, list):
            cmd = cmd[0]
        if error.errno == 13:
            message = "No permission to run %s" % (cmd,)
            private_sign_apk_die_with_error(message)
        elif error.errno == 2:
            message = "Can't find %s" % (cmd,)
            private_sign_apk_die_with_error(message)
        else:
            message = "Unknown error running %s Error: %s." % (cmd, error)
            private_sign_apk_die_with_error(message)
    except ValueError as error:
        if isinstance(cmd, list):
            cmd = cmd[0]
        message = "Invalid arguments when trying to run %s ErrorMessage: %s" % (cmd, error)
        private_sign_apk_die_with_error(message)
    except TypeError as error:
        if isinstance(cmd, list):
            cmd = cmd[0]
        message = "Unknown error running %s. Error: %s." % (cmd, error)
        private_sign_apk_die_with_error(message)


def private_sign_apk_die_with_error(error_message, return_value=-1):
    sys_stderr.write("ERROR: " + error_message)
    sys_stderr.write("\n")
    exit(return_value)


# pylint: disable=superfluous-parens
def private_sign_apk_log(log_str):
    print("INFO: " + log_str)


def add_sign_apk_args(parser, keystore_default=None, required_args=False):
    parser.add_argument('-k', '--keystore', default=keystore_default, required=required_args, help='Path to keystore to use while signing.')
    parser.add_argument('-kp', '--keystore_pass', required=required_args, help='Password for keystore.')
    parser.add_argument('-kyp', '--key_pass', required=required_args, help='Password for the key to use.')
    parser.add_argument('-ka', '--keystore_alias', required=required_args, help='Keystore alias to use.')


def parse_args():
    parser = argparse.ArgumentParser(description='Auto-DEV Android signing script')
    parser.add_argument("SourceApk", help="To be inserted automatically by bash script")
    parser.add_argument("-o", "--output", help='Path of output file (file name included)', required=True)
    add_sign_apk_args(parser, required_args=True)
    return parser.parse_args()


def get_fingerprint_from_keystore(script_args, is_sha256):
    output, _ = private_sign_apk_run_command(
        keytool_list_command_on_keystore(script_args.keystore,
                                         script_args.keystore_pass,
                                         script_args.keystore_alias),
        _stdout=PIPE, _stderr=PIPE)

    match = re.search(SHA256_REGEX_IN_KEYTOOL_OUTPUT if is_sha256 else SHA1_REGEX_IN_KEYTOOL_OUTPUT, output)
    if match:
        return match.group(1).replace(":", "")
    return None


def validate_sha1_with_keystore(script_args):
    if PLACEHOLDER_INDICATION in SEALED_FINGERPRINT_VALUE and PLACEHOLDER_INDICATION in GOOGLE_PLAY_FINGERPRINT_VALUE:
        # There is no Sha1 burned into the fused app. No need to validate
        return
    google_play_signing = PLACEHOLDER_INDICATION not in GOOGLE_PLAY_FINGERPRINT_VALUE
    used_fingerprint_value = GOOGLE_PLAY_FINGERPRINT_VALUE if google_play_signing else SEALED_FINGERPRINT_VALUE
    keystore_fingerprint = get_fingerprint_from_keystore(script_args, len(used_fingerprint_value) == SHA256_LEN)
    if not keystore_fingerprint:
        # Did not manage to parse the Sha1 from the keytool output. No need to validate
        return
    if not google_play_signing:
        if keystore_fingerprint != SEALED_FINGERPRINT_VALUE:
            private_sign_apk_die_with_error(
                "The Certificate Fingerprint [%s] must match the keystore used to sign. (Fingerprint: [%s])." %
                (keystore_fingerprint, SEALED_FINGERPRINT_VALUE))
        else:
            private_sign_apk_log("Successfully validated Certificate Fingerprint [%s] with the input Keystore" %
                                 (keystore_fingerprint,))
    else:
        if keystore_fingerprint == GOOGLE_PLAY_FINGERPRINT_VALUE:
            private_sign_apk_die_with_error(
                "When using with Google Play App Signing, the Certificate Fingerprint [%s] must not match the keystore used to sign." %
                (keystore_fingerprint,))
        else:
            private_sign_apk_log("Successfully validated Google Play App Signing.\n"
                                 "  Upload certificate SHA1 must be [%s].\n"
                                 "  App signing certificate SHA1 must be [%s]" %
                                 (keystore_fingerprint, GOOGLE_PLAY_FINGERPRINT_VALUE))


def sign_apk(script_args):
    try:
        aligned_file = script_args.SourceApk+'-aligned.apk'
        private_sign_apk_run_command(zipalign_command(script_args.SourceApk, aligned_file), _stdout=PIPE, _stderr=PIPE)
        move(aligned_file, script_args.SourceApk)
        private_sign_apk_run_command(apksigner_signing_command(
            script_args.SourceApk, script_args.output, script_args.keystore,
            script_args.keystore_pass, script_args.keystore_alias, script_args.key_pass))
        private_sign_apk_log("Successfully signed apk using apksigner with APK Signature Scheme v2 enabled")
    except Exception as e:
        private_sign_apk_die_with_error("Failed to execute apksigner with error: " + str(e))


def verify_apk(script_args):
    output, _ = private_sign_apk_run_command(apksigner_verify_command(script_args.output),
                                             _stdout=PIPE, _stderr=PIPE)
    if APKSIGNER_VERIFY_STRING not in output:
        remove(script_args.output)
        private_sign_apk_die_with_error("Failed to verify the signature after signing. verify output:\n%s" % (output,))
    else:
        private_sign_apk_log("Successfully verified apk signature")


def sign_aab(script_args):
    try:
        copy(script_args.SourceApk, script_args.output)
        private_sign_apk_run_command(jarsigner_signing_command(
            script_args.output, script_args.keystore,
            script_args.keystore_pass, script_args.keystore_alias, script_args.key_pass), _stdout=PIPE, _stderr=PIPE)
        aligned_file = script_args.output+'-aligned.aab'
        private_sign_apk_run_command(zipalign_command(script_args.output, aligned_file), _stdout=PIPE, _stderr=PIPE)
        move(aligned_file, script_args.output)
        private_sign_apk_log("Successfully signed android app bundle using jarsigner")
    except Exception as e:
        private_sign_apk_die_with_error("Failed to execute apksigner with error: " + str(e))


def verify_aab(script_args):
    output, _ = private_sign_apk_run_command(jarsigner_verify_command(script_args.output),
                                             _stdout=PIPE, _stderr=PIPE)
    if JARSIGNER_VERIFY_STRING not in output:
        remove(script_args.output)
        private_sign_apk_die_with_error("Failed to verify the signature after signing. verify output:\n%s" % (output,))
    else:
        private_sign_apk_log("Successfully verified android app bundle signature")


def main():
    script_args = parse_args()
    validate_sha1_with_keystore(script_args)
    if IS_ANDROID_APP_BUNDLE_IN_SCRIPT:
        sign_aab(script_args)
        verify_aab(script_args)
    else:
        sign_apk(script_args)
        verify_apk(script_args)
    extension = "android app bundle" if IS_ANDROID_APP_BUNDLE_IN_SCRIPT else "apk"
    private_sign_apk_log("Signed %s output file location:\n ===> %s <===" % (extension, abspath(script_args.output,)))


if __name__ == "__main__":
    main()
