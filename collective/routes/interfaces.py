from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.interface import Interface
from OFS.interfaces import IItem


class IFragmentContext(IItem):
    pass


class IWrappedContext(IItem):
    pass


class IWrappedObjectContext(IWrappedContext):
    pass


class IWrappedBrainsContext(IWrappedContext):
    pass


class IWrappedItem(Interface):
    pass


class ILayer(Interface):
    pass


class IRoutedRequest(IDefaultBrowserLayer):
    pass
