from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from collective.routes.controlpanel import IRoutesSettings


default_profile = 'profile-collective.routes:default'
uninstall_profile = 'profile-collective.routes:uninstall'


def upgrade_to_1_1a1(context):
    context.runImportStepFromProfile(uninstall_profile, 'controlpanel')
    context.runImportStepFromProfile(default_profile, 'controlpanel')
    context.runImportStepFromProfile(uninstall_profile, 'propertiestool')
    context.runImportStepFromProfile(default_profile, 'propertiestool')

    # convert selected routes
    pprops = getToolByName(context, 'portal_properties')
    props = pprops.routes_properties
    activated_routes = props.getProperty('activated_routes', ())
    registry = getUtility(IRegistry)
    settings = registry.forInterface(IRoutesSettings)
    settings.routes = set(activated_routes)
