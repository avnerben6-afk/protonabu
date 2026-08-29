""" Module: Protonabu Progress Indicator Interface
    - Author: Avner Ben
        - Created: 24-Aug-2026
            - Separated from Nabu
"""

from abc import ABC, abstractmethod


class IProgressIndicator(ABC):
    """ Progress Indicator
    """
    def __init__(self):
        """ to INITIALIZE Progress Indicator
        """

    @abstractmethod
    def start(self):
        """ to start <SUBSTITUTE> Progress Indicator
        """
        pass

    @abstractmethod
    def progress(self):
        """ to progress <SUBSTITUTE> Progress Indicator
        """
        pass

    @abstractmethod
    def end(self):
        """ to close <SUBSTITUTE> Progress Indicator
        """
        pass

    @abstractmethod
    def set(self, expected: int, units: str='items'):
        """ to set <SUBSTITUTE> Progress Indicator
        """
        pass

    @abstractmethod
    def isConsole(self)->bool:
        """ to tell if <SUBSTITUTE> Progress Indicator is on console
        """
        return False

    def isCancelled(self)->bool:
        """ to tell if <SUBSTITUTE> Progress Indicator has been cancelled
        """
        return False


class DummyProgressIndicator(IProgressIndicator):
    """ Dummy Progress Indicator
    """
    def __init__(self, 
        desc: str='', 
        expected: int = 0, 
        unit: str='',
        increment: int=0
    ):
        """ to INITIALIZE Dummy Progress Indicator
        """
        super().__init__()

    def start(self):
        """ to start <Dummy> Progress Indicator
        """
        pass

    def progress(self):
        """ to progress <Dummy> Progress Indicator
        """
        pass

    def end(self):
        """ to close <Dummy> Progress Indicator
        """
        pass

    def set(self, expected: int, units: str='items'):
        """ to set <Dummy> Progress Indicator
        """
        pass

    def isConsole(self)->bool:
        """ to tell if <Dummy> Progress Indicator is on console
        """
        return False

    def isCancelled(self)->bool:
        """ to tell if <Dummy> Progress Indicator has been cancelled
        """
        return False
