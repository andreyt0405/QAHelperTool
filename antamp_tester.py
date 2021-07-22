import argparse
from contextlib import contextmanager
from os import makedirs, getcwd, chdir
from os.path import join, exists
from shutil import rmtree
from tempfile import mkdtemp
from zipHandler import ZipHandler

@contextmanager
def erasedTempDir():
    tempDir = mkdtemp()
    try:
        yield tempDir
    except Exception as e:
        raise e
    finally:
        if tempDir and exists(tempDir):
            rmtree(tempDir, ignore_errors=True)

@contextmanager
def temp_change_dir(dir_to_change):
    if dir_to_change and not exists(dir_to_change):
        makedirs(dir_to_change)
    try:
        old_dir = getcwd()
        chdir(dir_to_change)
        yield
        chdir(old_dir)
    except:
        chdir(old_dir)
        raise

# this is meant to be used witht the AuthVerifier, to replace a single byte in the fused ipa's executable in order to have ANTAMP fail its __TEXT section comparison.
def modify_ipa(input_path, output_path):
    file_path_in_ipa = join('Payload', 'AuthVerifier.app', 'AuthVerifier')

    with erasedTempDir() as temp_dir:
        zipHandler = ZipHandler(input_path)
        zipHandler.extractall(temp_dir)

        exe_path = join(temp_dir, file_path_in_ipa)

        with open(exe_path, 'rb') as f:
            content = f.read()
        bytes_string_to_search_for = 'F65701A9F44F02A9FD7B03A9FDC30091481A8052E80300F9A00D00D000A02A910B320494E80D00F0000144F9E80D00D0'
        bytes_string_to_replace_with = 'F65701A9F44F02A9FD7B03A9FDC30091E84C8052E80300F9A00D00D000A02A910B320494E80D00F0000144F9E80D00D0'

        searched = bytearray.fromhex(bytes_string_to_search_for)
        replacement = bytearray.fromhex(bytes_string_to_replace_with)

        replaced_content = content.replace(searched, replacement)
        if replaced_content == content:
            print 'error! could not find bytes to replace'
        else:
            with open(exe_path, 'wb') as f:
                f.write(replaced_content)
            ZipHandler(output_path, "w").zip_directories(orig_zip_handler=zipHandler, zip_location=temp_dir)
            print 'success!'


def parse_arguments():
    parser = argparse.ArgumentParser(description='replaces a single byte in the fused ipa executable in order to have ANTAMP fail its __TEXT section comparison', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-i", "--input_ipa", required=True, help='Path to fused .ipa file')
    parser.add_argument("-o", "--output", required=True, help='Path of output file (file name included)')
    return parser.parse_args()


def main():
    script_args = parse_arguments()
    modify_ipa(script_args.input_ipa, script_args.output)


if __name__ == "__main__":
    main()
