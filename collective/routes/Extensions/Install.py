from Products.CMFCore.utils import getToolByName
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from collective.routes.upgrades import uninstall_profile


def uninstall(context, reinstall=False):
    setup = getToolByName(context, 'portal_setup')
    setup.runAllImportStepsFromProfile(uninstall_profile)
    if not reinstall:
        registry = getUtility(IRegistry)
        del registry.records[
            'collective.routes.controlpanel.IRoutesSettings.routes']
