import posixpath
import weakref

from .content import get_content_path
from guillotina.interfaces import IResource


class Navigator:
    def __init__(self, txn, container):
        self.txn = txn
        self.container = container
        self.index = weakref.WeakValueDictionary()
        self.deleted = {}
        for obj in txn.added.values():
            self._load_obj(obj)
        for obj in txn.modified.values():
            self._load_obj(obj)
        for obj in txn.deleted.values():
            self.deleted[get_content_path(obj)] = obj

    async def get(self, path):
        if path == '/':
            return self.container
        if path in self.deleted:
            return None
        obj = self.index.get(path)
        if obj is None:
            parent, child = posixpath.split(path)
            parent = await self.get(parent)
            obj = await parent.async_get(child)
            if obj is None:
                return None
            self.index[path] = obj
        return obj

    def delete(self, obj: IResource):
        path = get_content_path(obj)
        self.deleted[path] = obj
        self.txn.delete(obj)
        del self.index[path]

    def _load_obj(self, obj: IResource):
        """insert an object in the index"""
        if obj.__parent__ and get_content_path(
                obj.__parent__) not in self.index:
            self._load_obj(obj.__parent__)
        self.index[get_content_path(obj)] = obj
