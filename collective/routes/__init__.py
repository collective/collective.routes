# -*- coding: utf-8 -*-

from zope.i18nmessageid import MessageFactory
from zope.interface import alsoProvides
from zExceptions import NotFound
from Products.ZCatalog.Lazy import LazyCat
from Products.ZCatalog.Lazy import LazyMap

from collective.routes.content import WrappedBrainsContext
from collective.routes.content import WrappedObjectContext
from collective.routes.finders import catalogObjectFinder
from collective.routes.interfaces import IWrappedItem
from plone.locking.interfaces import ITTWLockable

_ = MessageFactory('collective.routes')

_routes = {}


class Fragment(object):

    def __init__(self, name):
        self.name = name

    def matches(self, path):
        return self.name == path

    def query(self, path):
        return {}


class DateFragment(Fragment):

    def __init__(self, name, _type):
        super(DateFragment, self).__init__(name)
        self._type = _type

    def matches(self, path):
        if not path.isdigit():
            return False
        return (self._type == 'year' and len(path) == 4) or \
               (self._type == 'month' and len(path) == 2) or \
               (self._type == 'day' and len(path) == 2)

    def query(self, path):
        return {self.name + '__' + self._type: int(path)}


class QueryFragment(Fragment):

    def __init__(self, name, _type=str):
        super(QueryFragment, self).__init__(name)
        self._type = _type

    def matches(self, path):
        return True

    def query(self, path):
        return {self.name: path}


class Route(object):

    def __init__(self, name, route, fragments, defaultQuery,
                 objectFinder=catalogObjectFinder, mungeObject=None):
        self.name = name
        self.route = route
        self.fragments = fragments
        self.defaultQuery = defaultQuery
        self.objectFinder = objectFinder
        self.mungeObject = mungeObject


def addRoute(routeName, route, defaultQuery={},
             objectFinder=catalogObjectFinder,
             mungeObject=None):
    if route.startswith('/'):
        route = route[1:]

    fragments = []
    for query in route.split('/'):
        if query.startswith('{') and query.endswith('}'):
            query = query.strip('{').strip('}')
            if ':' in query:
                name, _type = query.split(':')
                if _type in ('year', 'month', 'day'):
                    fragments.append(DateFragment(name, _type))
            else:
                fragments.append(QueryFragment(query))
        else:
            fragments.append(Fragment(query))

    _routes[routeName] = Route(routeName, route, fragments, defaultQuery,
                               objectFinder, mungeObject)


def getRoute(name):
    return _routes.get(name, None)


def getRouteNames():
    return _routes.keys()


def mungeAllObject(wrapped):
    if ITTWLockable.providedBy(wrapped.obj):
        alsoProvides(wrapped, ITTWLockable)


def getObject(route, context, request):
    finder = route.objectFinder
    result = finder(context)
    if result is None:
        raise NotFound
    elif type(result) in (set, tuple, list, LazyMap, LazyCat):
        if len(result) == 0:
            raise NotFound
        wrapped = WrappedBrainsContext(context, request, result)
    else:
        alsoProvides(result, IWrappedItem)
        wrapped = WrappedObjectContext(context, request, result)
        mungeAllObject(wrapped)
        if route.mungeObject:
            route.mungeObject(wrapped)
    return wrapped.__of__(context)


addRoute('Blog Posts',
         '/posts/{effective:year}/{effective:month}/{effective:day}',
        defaultQuery={'portal_type': 'News Item',
                      'sort_on': 'effective',
                      'sort_order': 'reverse'})

addRoute('Tagged',
         '/tagged/{Subject}/{Subject}/{Subject}',
         defaultQuery={'portal_type': 'News Item',
                       'sort_on': 'effective',
                       'sort_order': 'reverse'})
