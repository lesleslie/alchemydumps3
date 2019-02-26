from os import path as op, getcwd
from dataclasses import dataclass
from pathlib import Path
from pyclbr import readmodule

from contextlib import suppress
from functools import wraps

from yaml import dump, load
from yamlordereddictloader import Loader, SafeDumper


@dataclass
class DefaultLoader(object):
    storage: str = 'local'
    settings_file: str = op.join(getcwd(), "settings.yml")

    def __post_init__(self):
        self.configs = self.load_settings()
        self.add_storage_adaptor(self.configs['storage'])
        for k, v in self.configs.items():
            setattr(self, k, v)

    def load_settings(self) -> dict:
        with suppress(FileExistsError):
            Path(self.settings_file).touch()  # touched this way - not `w+`
        with open(self.settings_file, "r") as f:
            settings = load(f, Loader=Loader)
        return settings

    def add_storage_adaptor(obj, storage_adapter):
        available_adaptors = list(readmodule("alchemydumps.storage"))
        adaptor_name = f'{storage_adapter.title()}Storage'
        adaptor = [a for a in available_adaptors if a == adaptor_name][0]
        base_cls = obj.__class__
        base_cls_name = obj.__class__.__name__
        obj.__class__ = type(base_cls_name, (base_cls, adaptor), {})

@dataclass
class YamlLoader(DefaultLoader):
    def load_settings(self) -> dict:
        with suppress(FileExistsError):
            Path(self.settings_file).touch()  # touched this way - not `w+`
        with open(self.settings_file, "r") as f:
            settings = load(f, Loader=Loader)
        return settings


@dataclass
class EnvLoader(DefaultLoader):
    def load_settings(self):
        pass


def config(func):
    def wrapper(self, *args, **kwargs):
        func.__globals__['c'] = self.conf
        func(self, *args, **kwargs)

    return wrapper
