import asyncio
from abc import ABCMeta, abstractmethod, abstractproperty


class AbstractResource(metaclass=ABCMeta):
    @abstractproperty
    def __parent__():
        """ Parent resource or None for root """

    @abstractmethod
    def __getitem__(name):
        """ Return traversal.Traverser instance

        In simple:

            return traversal.Traverser(self, [name])
        """

    @asyncio.coroutine
    @abstractmethod
    def __getchild__(name):
        """ Return child resource or None, if not exists """


class AbstractView(metaclass=ABCMeta):
    @abstractmethod
    def __init__(resource):
        """ Receive current traversed resource """

    @asyncio.coroutine
    @abstractmethod
    def __call__():
        """ Return aiohttp.web.Response """
