import re
from logger import logger
from collections import OrderedDict
from os import remove, listdir, getcwd, chdir, path, symlink, utime
from os.path import join, abspath, exists, isdir
from time import time
from zipfile import ZIP_STORED, ZipFile, ZIP_DEFLATED

ZIP_INFO_SYMLINK_MAGIC = 2716663808

class ZipHandler(object):
    def __init__(self, file_path, mode='r'):
        self.file = abspath(file_path)
        self.zipFile = ZipFile(file_path, mode)
        self.files_dict = self._create_files_dict_builtin()

    def _create_files_dict_builtin(self):
        res = OrderedDict()
        for file_name in self.zipFile.namelist():
            res[file_name] = self.zipFile.getinfo(file_name).compress_type
        return res

    @staticmethod
    def _normalize_path_in_zip(path_in_zip):
        return path_in_zip[2:] if path_in_zip.startswith("./") else path_in_zip

    def namelist(self):
        return self.files_dict.keys()

    def files_compression_dict(self):
        return self.files_dict

    def _extract_sym_links(self, to_dir):
        # Python zipfile doesn't support symlinks. See https://bugs.python.org/issue18595, https://mail.python.org/pipermail/python-list/2005-June/322179.html
        for f in self.zipFile.infolist():
            if f.external_attr == ZIP_INFO_SYMLINK_MAGIC:
                output_file = join(to_dir, f.filename)
                if exists(output_file):
                    remove(output_file)
                logger.info("Extracting symlink: " + f.filename)
                target = self.zipFile.read(f)
                symlink(target, output_file)

    def extractall(self, to_dir="."):
        self.zipFile.extractall(to_dir)
        self._extract_sym_links(to_dir)

    def extract(self, file_to_extract, to_dir="."):
        return self.zipFile.extract(file_to_extract, to_dir)

    def has_file(self, file_to_check):
        file_to_check = self._normalize_path_in_zip(file_to_check)
        file_value = self.files_dict.get(file_to_check, None)
        return file_value is not None

    # FALLBACK use get_compress_type instead. This is used only if file is not found in orig zip
    @staticmethod
    def _determine_compression_type(file_path, compress, is_apk):
        NO_COMPRESS_PATTERN = re.compile(
            "\.(jpg|jpeg|png|gif|wav|mp2|mp3|ogg|aac|mpg|mpeg|mid|midi|smf|jet|rtttl|imy|xmf|mp4|m4a|m4v|3gp|3gpp|3g2|3gpp2|amr|awb|wma|wmv|apk|arsc|dll|zip)$")
        if not compress:
            return ZIP_STORED
        if not is_apk:
            return ZIP_DEFLATED
        if re.search(NO_COMPRESS_PATTERN, path.basename(file_path)):
            return ZIP_STORED
        else:
            return ZIP_DEFLATED

    def get_compress_type(self, file_to_check, compress=True, is_apk=False):
        file_to_check = self._normalize_path_in_zip(file_to_check)
        if self.has_file(file_to_check):
            return self.files_dict[file_to_check]
        else:
            return self._determine_compression_type(file_to_check, compress, is_apk=is_apk)

    def read(self, file_to_read):
        return self.zipFile.read(file_to_read)

    def zip_directories(self, dirs_to_zip=None, zip_location=".", orig_zip_handler=None, compress=True, is_apk=False,
                        orig_files_dict=None, ignore_list=None):
        if not orig_files_dict and orig_zip_handler:
            orig_files_dict = orig_zip_handler.files_dict

        if dirs_to_zip is None:
            dirs_to_zip = ["."]
        old_dir = getcwd()
        chdir(zip_location)
        for dirToZip in dirs_to_zip:
            self._rec_add_files(orig_files_dict, dirToZip, compress, is_apk, ignore_list)
        self.zipFile.close()
        chdir(old_dir)

    def _rec_add_files(self, orig_files_dict, dir_path, compress, is_apk, ignore_list):
        if not isdir(dir_path):
            return
        if not is_apk:
            filesSet = set()
            prevFileSetSize = 0
            for filename in listdir(dir_path):
                filesSet.add(filename.lower())
                if len(filesSet) == prevFileSetSize:
                    logger.info("deleting a duplicated file: " + filename + " in folder: " + dir_path)
                    remove(join(dir_path, filename))
                else:
                    prevFileSetSize = len(filesSet)

            # write the dir entry if this is not apk
            self.zipFile.write(dir_path, compress_type=ZIP_STORED)
        for entry in sorted(listdir(dir_path)):
            entry_path = join(dir_path, entry)
            # write dirs in DFS
            if isdir(entry_path):
                self._rec_add_files(orig_files_dict, entry_path, compress, is_apk, ignore_list)
                continue
            # write files in the dir
            entry_path_to_check = self._normalize_path_in_zip(entry_path)
            if ignore_list and entry_path_to_check in ignore_list:
                continue
            if orig_files_dict and entry_path_to_check in orig_files_dict:
                compress_type = orig_files_dict[entry_path_to_check]
            else:
                compress_type = self._determine_compression_type(entry_path, compress, is_apk)
            try:
                if entry_path.decode("utf-8") in self.namelist():
                    logger.info("found duplicate %s" % entry_path)
                else:
                    self.zipFile.write(entry_path, compress_type=compress_type)
            except ValueError as e:
                if 'ZIP does not support timestamps before 1980' in str(e):
                    utime(entry_path, (time(), time()))
                    self.zipFile.write(entry_path, compress_type=compress_type)
                else:
                    raise e