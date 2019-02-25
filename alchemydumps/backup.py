# coding: utf-8

from ftplib import FTP, error_perm
from dataclasses import dataclass, field
from alchemydumps.storage import FtpStorage, LocalStorage
from typing import Dict, List, Generator, Union

from yaml import dump, load
from yamlordereddictloader import Loader, SafeDumper


def load_settings(settings_file: str) -> dict:
    with open(settings_file, "r+") as f:
        settings = load(f, Loader=Loader)
        f.seek(0)
        f.truncate()
        dump(settings, f, Dumper=SafeDumper)  # this will reformat yml file
        f.close()  # do not trust `with` to close our file - close immediately
    return settings


@dataclass
class DefaultConfig(object):
    local_dir: str = 'alchemydumps-backup'
    prefix: str = 'db-backup'
    ftp_server: str = None
    ftp_user: str = None
    ftp_password: str = None
    ftp_path: str = None


@dataclass
class Config(DefaultConfig):
    settings_file: str = None

    def __post_init__(self):
        settings = load_settings(self.settings_file)
        for k, v in settings:
            self.__dict__[k] = v

def get_backup_config():
    return globals()['Backup'].config

def config():
    def get_config(func):
        func.__globals__['c'] = get_backup_config
        return func
    return get_config


@dataclass
class Backup(object):
    settings_file: str = None
    files: list = None

    def __post_init__(self):
        self.target = self.get_target()
        self.config = Config(self.settings_file)
        self.ftp = self.ftp_connect()



    # settings = Dict[load_settings(settings_file)]

    # def config(self):
    #     c = Config(self.settings)
    # return c

    # def __init__(self):
    #     """
    #     Bridge backups to local file system or to FTP server according to env
    #     vars set to allow FTP usage (see connect method).
    #     """
    #     self.ftp = self.ftp_connect()
    #     self.dir = config.dir
    #     self.prefix = config("ALCHEMYDUMPS_PREFIX", default=self.PRE)
    #     self.files = None
    #     self.target = self.get_target()

    @config()
    def ftp_connect(self, c) -> Union[FTP, bool]:
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

    @config()
    def get_target(self, ftp: FTP) -> Union[FTP, LocalStorage]:
        """Returns the object to manage backup files (Local or Remote)"""
        return FtpStorage(ftp, c.ftp_path) if ftp else LocalStorage(c.local_dir)

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

    @config()
    def get_name(self, class_name, timestamp=None):
        """
        Gets a backup file name given the timestamp and the name of the
        SQLAlchemy mapped class.
        """
        timestamp = timestamp or self.target.TIMESTAMP
        return "{}-{}-{}.gz".format(c.prefix, timestamp, class_name)


if __name__ == '__main__':
    pass
