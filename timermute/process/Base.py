# coding: utf-8
from abc import ABCMeta, abstractmethod

from timermute.ui.MainWindowInfo import MainWindowInfo


class Base(metaclass=ABCMeta):
    def __init__(self) -> None:
        pass

    @abstractmethod
    def run(self, mw: MainWindowInfo) -> None:
        pass


if __name__ == "__main__":
    pass
