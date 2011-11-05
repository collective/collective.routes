# -*- coding: utf-8 -*-

from collective.routes.controlpanel import IRoutesSettings
from zope.component import getUtility
from plone.registry.interfaces import IRegistry

from zope.component import adapts
from zope.i18nmessageid import MessageFactory
from zope.interface import alsoProvides
from zope.publisher.interfaces import IRequest
from zExceptions import NotFound
from ZPublisher.BaseRequest import DefaultPublishTraverse
from Products.ZCatalog.Lazy import LazyCat
from Products.ZCatalog.Lazy import LazyMap

from Products.CMFCore.interfaces._content import ISiteRoot

from collective.routes.content import FragmentContext
from collective.routes.content import WrappedBrainsContext
from collective.routes.content import WrappedObjectContext
from collective.routes.finders import catalogObjectFinder
from collective.routes.interfaces import IWrappedItem
from collective.routes.interfaces import ILayer

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


class RouteTraverser(DefaultPublishTraverse):
    adapts(ISiteRoot, IRequest)

    def publishTraverse(self, request, name):
        try:
            return DefaultPublishTraverse.publishTraverse(self, request, name)
        except KeyError:
            if ILayer.providedBy(request):
                registry = getUtility(IRegistry)
                settings = registry.forInterface(IRoutesSettings)
                activated_routes = settings.routes

                #path = request.environ['PATH_INFO'].split('/')
                path = request.physicalPathFromURL(request['URL'])
                context_path = self.context.getPhysicalPath()
                path = path[len(context_path):]

                for route_name in activated_routes:
                    route = getRoute(route_name)
                    if not route:
                        continue
                    if route.fragments[0].matches(path[0]):
                        fragments = route.fragments
                        fragment = fragments[0]
                        query = route.defaultQuery.copy()
                        query.update(fragment.query(name))
                        return FragmentContext(self.context, request, name,
                            route, fragments[0], fragments[1:],
                            query).__of__(self.context)
            raise


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
