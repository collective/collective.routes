# -*- encoding: utf-8 -*-

from zope import schema
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary
from zope.interface import implements
from zope.interface import Interface

from plone.app.registry.browser import controlpanel
from z3c.form.browser.checkbox import CheckBoxFieldWidget

from collective.routes import getRoute
from collective.routes import getRouteNames
from collective.routes import _


class RoutesVocabulary(object):
    """Creates a vocabulary with all the routes available on the
    site.
    """
    implements(IVocabularyFactory)

    def __call__(self, context):
        items = []
        for route_name in getRouteNames():
            route = getRoute(route_name)
            if not route:
                continue
            items.append(SimpleVocabulary.createTerm(route.name,
                                                     route.name,
                                                     route.name))
        return SimpleVocabulary(items)
RoutesVocabularyFactory = RoutesVocabulary()


class IRoutesSettings(Interface):
    """ Interface describing the settings on the control panel """
    routes = schema.Set(
            title=_(u"Available Routes"),
            description=_(u""),
            value_type=schema.Choice(vocabulary=u"collective.routes.Routes"),
            default=set([]),
            missing_value=set([]),
            required=False,
            )


class RoutesSettingsEditForm(controlpanel.RegistryEditForm):
    schema = IRoutesSettings
    label = _(u'Routes Settings')
    description = _(u'Here you can modify the settings for Routes.')

    def updateFields(self):
        super(RoutesSettingsEditForm, self).updateFields()
        self.fields['routes'].widgetFactory = CheckBoxFieldWidget

    def updateWidgets(self):
        super(RoutesSettingsEditForm, self).updateWidgets()


class RoutesConfiglet(controlpanel.ControlPanelFormWrapper):
    form = RoutesSettingsEditForm
