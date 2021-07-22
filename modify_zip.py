import argparse
from contextlib import contextmanager
from os import remove
from tempfile import mkdtemp
from os.path import join, exists
from shutil import rmtree, copyfile
from zipfile import ZipFile
from logger import logger
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

def parse_arguments():
    parser = argparse.ArgumentParser(description='adds a file to an existing zip file', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-i", "--input", required=True, help='Path to fused .ipa/apk/aab file')
    parser.add_argument("-o", "--output", required=True, help='Path of output file (file name included)')
    parser.add_argument("-f", "--file_to_add", default="", help="Path of exising file to add. if empty or doesn't exist, add empty file")
    parser.add_argument("-l", "--location_in_zip", required=True, help='location of file to place in zip. For eg. "Payload/Trends256.app/new_file" for ipa. add trailing "/" to create a dir')
    change_file_parser = parser.add_argument_group("change_file", "change a char inside given file location")
    change_file_parser.add_argument("-lf", "--location_in_file", default=0, type=int, help="numeric location in file to modify")
    change_file_parser.add_argument("-c", "--char_to_put", help="char to put in location_in_file")
    return parser.parse_args()

def add_file(input_path, output_path, file_to_add, location_in_zip):
    copyfile(input_path, output_path)
    zipFile = ZipFile(output_path, 'a')
    if exists(file_to_add):
        logger.info("adding file '" + file_to_add + "' to zip '" + input_path + "' and writing to '" + output_path + "' under location '" + location_in_zip + "'")
        zipFile.write(file_to_add, location_in_zip)
    else:
        if location_in_zip.endswith("/"):
            logger.info("adding empty dir to zip '" + input_path + "' and writing to '" + output_path + "' under location '" + location_in_zip + "'")
        else:
            logger.info("adding empty file to zip '" + input_path + "' and writing to '" + output_path + "' under location '" + location_in_zip + "'")
        zipFile.writestr(location_in_zip, "")
    zipFile.close()


# this is meant to be used witht the AuthVerifier, to replace a single byte in the fused ipa's executable in order to have ANTAMP fail its __TEXT section comparison.
def modify_file(input_path, output_path, location_in_zip, location_in_file, char_to_put):
    with erasedTempDir() as temp_dir:
        zipHandler = ZipHandler(input_path)
        zipHandler.extractall(temp_dir)

        file_to_modify_path = join(temp_dir, location_in_zip)

        with open(file_to_modify_path, 'rb') as f:
            content = f.read()
        content_list = list(content)
        content_list[location_in_file] = char_to_put

        with open(file_to_modify_path, 'wb') as f:
            f.write("".join(content_list))
        ZipHandler(output_path, "w").zip_directories(orig_zip_handler=zipHandler, zip_location=temp_dir)
        logger.info('success!')

def replace_file(input_path, output_path, file_to_add, location_in_zip):
    if not exists(file_to_add):
        logger.error("file " + file_to_add + " doesn't exist")
        return
    with erasedTempDir() as temp_dir:
        zipHandler = ZipHandler(input_path)
        zipHandler.extractall(temp_dir)

        file_to_replace_path_in_zip = join(temp_dir, location_in_zip)
        if not exists(file_to_replace_path_in_zip):
            logger.error("file " + location_in_zip + " doesn't exist in " + input_path)
            return

        remove(file_to_replace_path_in_zip)
        copyfile(file_to_add, file_to_replace_path_in_zip)

        ZipHandler(output_path, "w").zip_directories(orig_zip_handler=zipHandler, zip_location=temp_dir)
        logger.info('success!')


def main():
    script_args = parse_arguments()
    if script_args.char_to_put is not None:
        modify_file(script_args.input, script_args.output, script_args.location_in_zip, script_args.location_in_file, script_args.char_to_put)
    else:
        add_file(script_args.input, script_args.output, script_args.file_to_add, script_args.location_in_zip)


if __name__ == "__main__":
    main()