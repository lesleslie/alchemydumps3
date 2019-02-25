# coding: utf-8


class Confirm(object):
    def __init__(self, assume_yes=False):
        self.assume_yes = assume_yes

    def ask(self):
        if self.assume_yes:
            return True

        message = '\n==> Press "Y" to confirm, or anything else to abort: '
        confirmation = input(message)
        return True if str(confirmation).lower() == "y" else False
