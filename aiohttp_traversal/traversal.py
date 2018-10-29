import asyncio
import logging

log = logging.getLogger(__name__)


async def traverse(root, path):
    """ Find resource for path.

    root: instance of Resource
    path: list or path parts
    return: tuple `(resource, tail)`
    """
    if not path:
        return root, tuple(path)

    path = list(path)
    traverser = root[path.pop(0)]

    while path:
        traverser = traverser[path.pop(0)]

    return await traverser.traverse()


class Traverser:

    def __init__(self, resource, path):
        self.resource = resource
        self.path = path

    def __getitem__(self, item):
        return Traverser(self.resource, self.path + (item,))

    def __await__(self):
        return self.__anext__().__await__()

    async def __anext__(self):
        """ This object is coroutine.

        For this:

            await app.router.get_root()['a']['b']['c']
        """
        resource, tail = await self.traverse()

        if tail:
            raise KeyError(tail[0])
        else:
            return resource

    async def traverse(self):
        """ Main traversal algorithm.

        Return tuple `(resource, tail)`.
        """
        last, current = None, self.resource
        path = list(self.path)

        while path:
            item = path[0]
            last, current = current, await current.__getchild__(item)

            if current is None:
                return last, tuple(path)

            del path[0]

        return current, tuple(path)


def lineage(resource):
    """ Return a generator representing the lineage
        of the resource object implied by the resource argument
    """
    while resource is not None:
        yield resource
        resource = resource.__parent__


def find_root(resource):
    """ Find root resource
    """
    return list(lineage(resource))[-1]
