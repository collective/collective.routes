from zope.app.component.hooks import getSite
from zope.interface import implements
from zope.component import getMultiAdapter

from Acquisition import aq_inner
from zExceptions import NotFound

from Products.Five import BrowserView
from Products.CMFPlone.browser.interfaces import INavigationBreadcrumbs
from Products.CMFPlone.browser.navigation import get_view_url
from Products.CMFPlone import utils

from collective.routes import getObject
from collective.routes.interfaces import IWrappedObjectContext
from collective.routes.interfaces import IWrappedBrainsContext
from collective.routes.interfaces import IWrappedContext
from collective.routes.interfaces import IFragmentContext


class FragmentView(BrowserView):

    def __call__(self):
        route = self.context.route
        wrapped = getObject(route, self.context, self.request)

        if route.customViewName:
            view = wrapped.restrictedTraverse(route.customViewName)
        elif IWrappedBrainsContext.providedBy(wrapped):
            view = wrapped.restrictedTraverse('folder_summary_view')
        elif IWrappedObjectContext.providedBy(wrapped):
            layout = wrapped.obj.getLayout()
            view = wrapped.restrictedTraverse(layout)
        else:
            raise NotFound
        return view()


class WrappedBreadcrumbs(BrowserView):
    """
    The reason we do this is because the wrapped
    object makes the breadcrumb behave a bit funky
    and this fixes it.
    """
    implements(INavigationBreadcrumbs)

    def breadcrumbs(self):
        context = aq_inner(self.context)
        request = self.request

        if hasattr(context, 'route') and context.route.breadcrumbFactory:
            return context.route.breadcrumbFactory(context, request)

        # XXX this is the main part here:
        # to up 2 parents since the current context
        # is wrapped
        if IWrappedContext.providedBy(context):
            container = utils.parent(utils.parent(context))
        elif IFragmentContext.providedBy(context):
            container = getSite()
        name, item_url = get_view_url(context)

        view = getMultiAdapter((container, request), name='breadcrumbs_view')
        base = tuple(view.breadcrumbs())

        if base:
            item_url = '%s/%s' % (base[-1]['absolute_url'], name)

        base += ({'absolute_url': item_url,
                  'Title': utils.pretty_title_or_id(context, context)},)
        return base
