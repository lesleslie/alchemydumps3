# coding: utf-8

import ftplib

import decouple

from flask_alchemydumps.storage import FtpStorage, LocalStorage


class Backup(object):
    DIR = "alchemydumps-backup"
    PRE = "db-bkp"

    def __init__(self):
        """
        Bridge backups to local file system or to FTP server according to env
        vars set to allow FTP usage (see connect method).
        """
        self.ftp = self.ftp_connect()
        self.dir = decouple.config("ALCHEMYDUMPS_DIR", default=self.DIR)
        self.prefix = decouple.config("ALCHEMYDUMPS_PREFIX", default=self.PRE)
        self.files = None
        self.target = self.get_target()

    def ftp_connect(self):
        """
        Tries to connect to FTP server according to env vars:
        * `ALCHEMYDUMPS_FTP_SERVER`
        * `ALCHEMYDUMPS_FTP_USER`
        * `ALCHEMYDUMPS_FTP_PASSWORD`
        * `ALCHEMYDUMPS_FTP_PATH`
        :return: Python FTP class instance or False
        """
        server = decouple.config("ALCHEMYDUMPS_FTP_SERVER", default=None)
        user = decouple.config("ALCHEMYDUMPS_FTP_USER", default=None)
        password = decouple.config("ALCHEMYDUMPS_FTP_PASSWORD", default=None)
        path = decouple.config("ALCHEMYDUMPS_FTP_PATH", default=None)
        if server and user:
            try:
                ftp = ftplib.FTP(server, user, password)
                return self.ftp_change_path(ftp, path)
            except ftplib.error_perm:
                print("==> Couldn't connect to " + server)
                return False
            return ftp
        return False

    @staticmethod
    def ftp_change_path(ftp, path):
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

    def close_ftp(self):
        if self.ftp:
            self.ftp.quit()

    def get_target(self):
        """Returns the object to manage backup files (Local or Remote)"""
        return FtpStorage(self.ftp) if self.ftp else LocalStorage(self.dir)

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
        timestamp = timestamp or self.target.TIMESTAMP
        return "{}-{}-{}.gz".format(self.prefix, timestamp, class_name)
