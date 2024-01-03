from abc import ABCMeta, abstractmethod

from timermute.ui.main_window_info import MainWindowInfo


class Base(metaclass=ABCMeta):
    def __init__(self) -> None:
        pass

    @abstractmethod
    def run(self, mw: MainWindowInfo) -> None:
        pass


if __name__ == "__main__":
    pass
