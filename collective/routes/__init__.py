from zope.app.component.hooks import getSite
# -*- coding: utf-8 -*-
import re

from zope.i18nmessageid import MessageFactory
from zope.interface import alsoProvides
from zExceptions import NotFound
from Products.ZCatalog.Lazy import LazyCat
from Products.ZCatalog.Lazy import LazyMap

from collective.routes.content import WrappedBrainsContext
from collective.routes.content import WrappedObjectContext
from collective.routes.finders import catalogObjectFinder
from plone.locking.interfaces import ITTWLockable
from Products.Archetypes.interfaces import IBaseObject
from collective.routes.interfaces import IRoutedRequest

_ = MessageFactory('collective.routes')

_routes = {}
_interfaces_to_munge_with = (
    ITTWLockable,
    IBaseObject
)


def initialize(context):
    pass


def addInterfaceMunge(*ifaces):
    def meth(context):
        for iface in ifaces:
            alsoProvides(context, iface)
    return meth


class Fragment(object):

    def __init__(self, name):
        self.name = name

    def matches(self, path):
        return self.name == path

    def query(self, path):
        return {}

    def __unicode__(self):
        return u'name: %s' % self.name


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

    def __unicode__(self):
        return u'date(%s) : %s' % (self._type, self.name)


class QueryFragment(Fragment):

    def __init__(self, name, _type=str):
        super(QueryFragment, self).__init__(name)
        self._type = _type

    def matches(self, path):
        return True

    def query(self, path):
        return {self.name: path}

    def __unicode__(self):
        return u'query(%s): %s' % (self._type, self.name)


class Route(object):

    def __init__(self, name, route, fragments, defaultQuery={},
                 objectFinder=catalogObjectFinder, mungeObject=None,
                 customViewName=None, allowPartialMatch=False,
                 breadcrumbFactory=None, customPredicates=[]):
        self.name = name
        self.route = route
        self.fragments = fragments
        self.defaultQuery = defaultQuery
        self.objectFinder = objectFinder
        self.mungeObject = mungeObject
        self.customViewName = customViewName
        self.allowPartialMatch = allowPartialMatch
        self.breadcrumbFactory = breadcrumbFactory
        self.customPredicates = customPredicates

    def matches(self, path, request):
        query = {}
        match = False
        for idx, fragpath in enumerate(path):
            if idx >= len(self.fragments):
                if match and self.allowPartialMatch:
                    break
                else:
                    return False
            fragment = self.fragments[idx]
            if not fragment.matches(fragpath):
                if match and self.allowPartialMatch:
                    break
                else:
                    return False
            query = fragment.query(fragpath)
            match = True
        if match:
            if len(path) != len(self.fragments) and not self.allowPartialMatch:
                return False
            for predicate in self.customPredicates:
                if not predicate(request, query):
                    return False
        return match


def addRoute(routeName, route, defaultQuery={},
             objectFinder=catalogObjectFinder, mungeObject=None,
             customViewName=None, allowPartialMatch=False,
             breadcrumbFactory=None, customPredicates=[]):
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

    if type(customPredicates) not in (list, tuple, set):
        customPredicates = [customPredicates]

    _routes[routeName] = Route(routeName, route, fragments,
        defaultQuery=defaultQuery, objectFinder=objectFinder,
        mungeObject=mungeObject, customViewName=customViewName,
        allowPartialMatch=allowPartialMatch,
        breadcrumbFactory=breadcrumbFactory, customPredicates=customPredicates)


def getRoute(name):
    return _routes.get(name, None)


def getRouteNames():
    return _routes.keys()


def mungeAllObject(wrapped):
    for iface in _interfaces_to_munge_with:
        if iface.providedBy(wrapped.obj):
            alsoProvides(wrapped, iface)


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
        wrapped = WrappedObjectContext(context, request, result)
        mungeAllObject(wrapped)
        if route.mungeObject:
            route.mungeObject(wrapped)
    alsoProvides(request, IRoutedRequest)
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
