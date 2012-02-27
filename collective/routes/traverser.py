from zope.publisher.interfaces import IRequest
from zope.component import adapts
from collective.routes import getRoute
from zope.component import getUtility
from ZPublisher.BaseRequest import DefaultPublishTraverse
from plone.registry.interfaces import IRegistry
from collective.routes.interfaces import ILayer
from Products.CMFCore.interfaces._content import ISiteRoot
from collective.routes.controlpanel import IRoutesSettings
from collective.routes.content import FragmentContext


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

                fullpath = request.physicalPathFromURL(
                    request.get('ACTUAL_URL', ''))
                context_path = self.context.getPhysicalPath()
                fullpath = fullpath[len(context_path):]
                for route_name in activated_routes:
                    route = getRoute(route_name)
                    if not route:
                        continue
                    if route.matches(fullpath, request):
                        fragments = route.fragments
                        fragment = fragments[0]
                        query = route.defaultQuery.copy()
                        query.update(fragment.query(name))
                        return FragmentContext(self.context, request, name,
                            route, fragments[0], fragments[1:],
                            query).__of__(self.context)

            raise
