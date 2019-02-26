# coding: utf-8
from arrow import utcnow
from os import path as op, getcwd
from re import search
from pathlib import Path
from ftplib import FTP, error_perm
from dataclasses import dataclass, field
from alchemydumps.storage import FtpStorage, LocalStorage
from alchemydumps.utils import pprint
from typing import Dict, List, Generator, Union, Any
from alchemydumps.config import DefaultLoader, config





@dataclass
class Backup(object):
    settings_type: str = 'yaml'
    files: list = None
    storage: classmethod = None
    settings: classmethod = DefaultLoader

    def __post_init__(self):
        self.conf = self.settings()
        self.target = self.get_target()
        self.ftp = self.ftp_connect()

    @config
    def ftp_connect(self) -> Union[FTP, bool]:
        if c.ftp_server and c.ftp_user:
            try:
                ftp = FTP(c.ftp_server, c.ftp_user, c.ftp_password)
                return self.ftp_change_path(ftp, c.ftp_path)
            except error_perm:
                print("==> Couldn't connect to " + c.ftp_server)
        return False

    @staticmethod
    def ftp_change_path(ftp, path) -> Union[FTP, bool]:
        """
        Changes path at FTP server
        :param ftp: Python FTP class instance
        :param path: (str) Path at the FTP server
        :return: Python FTP class instance or False
        """
        change_path = ftp.cwd(path)
        if not change_path.startswith("250 "):
            print("==> Path doesn't exist: " + path)
            ftp.quit()
            return False
        return ftp

    def close_ftp(self) -> None:
        if self.ftp:
            self.ftp.quit()

    @config
    def get_target(self) -> Union[FtpStorage, LocalStorage]:
        if type(self.storage) == FTP:
            return FtpStorage(self.ftp, backup_path=c.ftp_path)
        else:
            return LocalStorage(backup_path=c.local_dir)

    @staticmethod
    def get_timestamp(name):
        pattern = r"(.*)(-)(?P<timestamp>[\d]{10})(-)(.*)"
        match = search(pattern, name)
        return match.group("timestamp") if match else False

    def get_timestamps(self):
        """
        Gets the different existing timestamp numeric IDs
        :param files: (list) List of backup file names
        :return: (list) Existing timestamps in backup directory
        """
        if not self.files:
            self.files = tuple(self.target.get_files())

        different_timestamps = list()
        for name in self.files:
            timestamp = self.target.get_timestamp(name)
            if timestamp and timestamp not in different_timestamps:
                different_timestamps.append(timestamp)
        return different_timestamps

    def by_timestamp(self, timestamp):
        """
        Gets the list of all backup files with a given timestamp
        :param timestamp: (str) Timestamp to be used as filter
        :param files: (list) List of backup file names
        :return: (list) The list of backup file names matching the timestamp
        """
        if not self.files:
            self.files = tuple(self.target.get_files())

        for name in self.files:
            if timestamp == self.target.get_timestamp(name):
                yield name

    def valid(self, timestamp):
        """Check backup files for the given timestamp"""
        if timestamp and timestamp in self.get_timestamps():
            return True
        print('==> Invalid id. Use "history" to list existing downloads')
        return False

    def get_name(self, class_name, timestamp=None):
        """
        Gets a backup file name given the timestamp and the name of the
        SQLAlchemy mapped class.
        """
        timestamp = timestamp or utcnow().timestamp
        return "{}-{}-{}.gz".format(c.prefix, timestamp, class_name)


if __name__ == "__main__":
    Backup(settings=DefaultLoader)
