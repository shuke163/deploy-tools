#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@aythor: shuke
@file: delete_hidden_file.py 
@content: zhaofengfeng@rongcloud.cn
@time: 2020/01/20 14:38
@software:  Door
"""

import os
import re
import shutil
import tarfile
import click
import logging

logging.basicConfig(format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                    level=logging.DEBUG)


class DeleteHiddenFile:
    """
    delete rcx pkg hidden file
    """

    def __init__(self):
        self.rcx_encrypt = self.rcx_encrypt_dir()
        self.tar_name = "rcx.tar.gz"
        self.outFullName = os.path.join(os.getcwd(), self.tar_name)

    def rcx_encrypt_dir(self):
        for file in os.listdir(os.getcwd()):
            if file.endswith("encrypt"):
                rcx_encrypt = os.path.join(os.getcwd(), file)
                return rcx_encrypt

    def delete_file(self):
        for fpathe, dirs, fs in os.walk(os.getcwd()):
            for f in fs:
                if re.match("._.*", f):
                    file_path = os.path.join(fpathe, f)
                    os.remove(file_path)
                    logging.info(f"recurs hidden file path: {file_path}")

    def rcx_tar_gz(self):
        tar = tarfile.open(self.outFullName, "w:gz")
        for root, dir, files in os.walk(self.rcx_encrypt):
            for file in files:
                fullpath = os.path.join(root, file)
                tar.add(fullpath)
                tar.close()

    def package_file(self):
        try:
            tar = tarfile.open(self.outFullName, "w:gz")
            for root, dirs, files in os.walk(self.rcx_encrypt):
                os.chdir(self.rcx_encrypt)
                _root = os.path.relpath(root, start=os.getcwd())
                for filename in files:
                    tar.add(os.path.join(root, filename),
                            arcname=os.path.join(_root, filename))
                for dir in dirs:
                    tar.add(os.path.join(root, dir), arcname=os.path.join(_root, dir))
            tar.close()

            if os.path.isdir(self.rcx_encrypt):
                shutil.rmtree(self.rcx_encrypt, ignore_errors=False)

        except Exception as exc:
            logging.error(f"{self.outFullName} file error! '{exc.__class__.__name__}: {exc}")

    def main(self):
        self.delete_file()
        self.package_file()


@click.command()
@click.option('--dir', default=DeleteHiddenFile().rcx_encrypt, help='rcx encrypt dir path')
def main(dir):
    logging.info(f"enter rcx_encrypt path: {dir}")

    DeleteHiddenFile().main()

    click.echo("delete file end!")


if __name__ == '__main__':
    main()
