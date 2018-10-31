from abc import ABCMeta, abstractmethod, abstractproperty


class AbstractResource(metaclass=ABCMeta):
    @abstractproperty
    def __parent__(self):
        """ Parent resource or None for root """

    @abstractmethod
    def __getitem__(self, name):
        """ Return traversal.Traverser instance

        In simple:

            return traversal.Traverser(self, [name])
        """

    @abstractmethod
    async def __getchild__(self, name):
        """ Return child resource or None, if not exists """


class AbstractView(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self, resource, request):
        """ Receive current traversed resource """

    @abstractmethod
    async def __call__(self):
        """ Return aiohttp.web.Response """
