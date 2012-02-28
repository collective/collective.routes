from zope.interface import alsoProvides
# -*- coding: utf-8 -*-

import unittest2 as unittest

from zope.component import getMultiAdapter
from zope.component import getUtility

from plone.app.testing import TEST_USER_ID
from plone.app.testing import logout
from plone.app.testing import setRoles
from plone.app.testing import applyProfile
from plone.registry import Registry
from plone.registry.interfaces import IRegistry

from Products.CMFCore.utils import getToolByName

from collective.routes.controlpanel import IRoutesSettings
from collective.routes.testing import Routes_INTEGRATION_TESTING
from collective.routes.interfaces import ILayer

BASE_REGISTRY = 'collective.routes.controlpanel.IRoutesSettings.%s'


class RegistryTest(unittest.TestCase):

    layer = Routes_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        # set up settings registry
        self.registry = Registry()
        self.registry.registerInterface(IRoutesSettings)

        request = self.portal.REQUEST
        alsoProvides(request, ILayer)

    def test_controlpanel_view(self):
        view = getMultiAdapter((self.portal, self.portal.REQUEST),
                               name='routes-settings')
        view = view.__of__(self.portal)
        self.failUnless(view())

    def test_controlpanel_view_is_protected(self):
        from AccessControl import Unauthorized
        logout()
        self.assertRaises(Unauthorized,
                          self.portal.restrictedTraverse,
                          '@@routes-settings')

    def test_action_in_controlpanel(self):
        cp = getToolByName(self.portal, 'portal_controlpanel')
        actions = [a.getAction(self)['id'] for a in cp.listActions()]
        self.failUnless('routes' in actions)

    def test_routes_record(self):
        record_routes = self.registry.records[
            BASE_REGISTRY % 'routes']
        self.failUnless('routes' in IRoutesSettings)
        self.assertEquals(record_routes.value, set([]))


class RegistryUninstallTest(unittest.TestCase):

    layer = Routes_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.registry = getUtility(IRegistry)
        # uninstall the package
        self.qi = getattr(self.portal, 'portal_quickinstaller')
        self.qi.uninstallProducts(products=['collective.routes'])

    def test_records_removed_from_registry(self):
        records = [
            'collective.routes.controlpanel.IRoutesSettings.routes',
            ]
        for r in records:
            self.failIf(r in self.registry.records,
                        '%s record still in configuration registry' % r)


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
