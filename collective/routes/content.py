from zope.app.component.hooks import getSite
from zope.publisher.interfaces.browser import IBrowserPublisher
from zope.component import queryMultiAdapter
from zope.interface import implements
from zope.interface import Interface

from zExceptions import NotFound
from OFS.SimpleItem import SimpleItem

from Products.Archetypes.interfaces.base import IBaseObject
from Products.Archetypes.utils import shasattr

from collective.routes.interfaces import IFragmentContext
from collective.routes.interfaces import IWrappedContext
from collective.routes.interfaces import IWrappedObjectContext
from collective.routes.interfaces import IWrappedBrainsContext
from collective.routes.utils import smart_update


class WrappedContext(SimpleItem):
    implements(IWrappedContext, IBrowserPublisher)

    portal_type = meta_type = 'TemporaryWrappedItem'

    def __init__(self, context, request, obj=None):
        super(WrappedContext, self).__init__(context, request)
        self.__parent__ = context
        self.context = context
        self.request = request
        self.obj = obj

    def getPhysicalPath(self):
        return self.context.getPhysicalPath()


class WrappedObjectContext(WrappedContext):
    implements(IWrappedObjectContext)

    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]
        return getattr(self.__dict__['obj'], name)

    def boboTraverse(self, context, REQUEST, name):
        # try view first
        target = queryMultiAdapter((context, self.request), name=name)
        if target:
            return target

        if name.startswith('image'):
            field = self.getField('image')
            if field:
                image = None
                if name == 'image':
                    image = field.getScale(self)
                else:
                    scalename = name[len('image_'):]
                    if scalename in field.getAvailableSizes(self):
                        image = field.getScale(self, scale=scalename)
                if image is not None and not isinstance(image, basestring):
                    # image might be None or '' for empty images
                    return image

        # sometimes, the request doesn't have a response, e.g. when
        # PageTemplates traverse through the object path, they pass in
        # a phony request (a dict).
        RESPONSE = getattr(REQUEST, 'RESPONSE', None)

        # Is it a registered sub object
        data = hasattr(context, 'getSubObject') and \
            context.getSubObject(name, REQUEST, RESPONSE)
        if data:
            return data
        # Or a standard attribute (maybe acquired...)
        target = None
        # Logic from "ZPublisher.BaseRequest.BaseRequest.traverse"
        # to check whether this is a browser request
        if shasattr(self, name):  # attributes of self come first
            target = getattr(self, name)
        else:  # then views
            target = queryMultiAdapter((context, REQUEST), Interface, name)
            if target is not None:
                # We don't return the view, we raise an
                # AttributeError instead (below)
                target = None
            else:  # then acquired attributes
                target = getattr(self, name, None)

        if target is not None:
            return target

        raise AttributeError(name)

    def __bobo_traverse__(self, REQUEST, name):
        try:
            return self.boboTraverse(self.obj, REQUEST, name)
        except AttributeError:
            if not IBaseObject.providedBy(self.obj):
                return self.boboTraverse(getSite(), REQUEST, name)
            raise


class WrappedBrainsContext(WrappedContext):
    implements(IWrappedBrainsContext)

    def __init__(self, context, request, brains):
        super(WrappedBrainsContext, self).__init__(context, request)
        self.__parent__ = context
        self.context = context
        self.request = request
        self.brains = brains
        self.id = ''
        self.Title = lambda: 'Listing'

    def getFolderContents(self, contentFilter={}, batch=False,
                          b_size=100, full_objects=False):
        b_start = int(self.request.get('b_start', 0))
        contents = self.brains
        if full_objects:
            contents = [b.getObject() for b in contents]

        if batch:
            from Products.CMFPlone import Batch
            batch = Batch(contents, b_size, b_start, orphan=0)
            return batch
        return contents


class FragmentContext(SimpleItem):
    implements(IFragmentContext, IBrowserPublisher)

    portal_type = meta_type = 'TemporaryFragmentItem'

    def __init__(self, context, request, name, route, fragment, fragments=[],
                 query={}):
        super(FragmentContext, self).__init__(context, request)
        # make sure that breadcrumbs will be correct
        self.__parent__ = context
        self.context = context
        self.request = request
        self.route = route
        self.fragment = fragment
        self.fragments = fragments
        self.query = query
        self.name = name
        self.id = name
        self.Title = lambda: name

    def getFragmentContext(self, request, name):
        fragment = self.fragments[0]
        if fragment.matches(name):
            query = self.query.copy()
            query = smart_update(query, fragment.query(name))
            return FragmentContext(self, request, name, self.route,
                fragment, self.fragments[1:], query).__of__(self)

    def boboTraverse(self, wrapped, request, name):
        if hasattr(wrapped, '__bobo_traverse__'):
            return wrapped.__bobo_traverse__(request, name)
        else:
            raise NotFound

    def publishTraverse(self, request, name):
        try:
            # first see if it can be traversed
            # or if there is a view for this object
            route = self.route
            from collective.routes import getObject
            wrapped = getObject(route, self, request)
            return self.boboTraverse(wrapped, request, name)
        except (AttributeError, NotFound):
            # okay, now try to use url fragments to continue
            # traversal
            if len(self.fragments) > 0:
                return self.getFragmentContext(request, name)
        raise NotFound

    def browserDefault(self, request):
        return self, ('@@view',)

    def getPhysicalPath(self):
        return self.context.getPhysicalPath() + (self.id,)
