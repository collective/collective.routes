from collective.routes.controlpanel import IRoutesSettings
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from zExceptions import NotFound
from collective.routes.testing import browserLogin
from collective.routes.testing import createObject
from plone.testing.z2 import Browser
import transaction
import unittest2 as unittest
from collective.routes.testing import Routes_FUNCTIONAL_TESTING


class TestRoutes(unittest.TestCase):

    layer = Routes_FUNCTIONAL_TESTING

    def setUp(self):
        from collective.routes import addRoute
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        addRoute('foobar',
                 '/{effective:year}/{effective:month}/{effective:day}',
                 defaultQuery={'portal_type': 'News Item'},
                 allowPartialMatch=True)
        addRoute('foobar1',
                 '/foobar1/{effective:year}/{effective:month}/{effective:day}',
                 defaultQuery={'portal_type': 'News Item'})
        addRoute('foobar2',
                 '/foobar2/{Subject}',
                 defaultQuery={'portal_type': 'News Item'})
        folder = createObject(self.portal, 'Folder', 'folder')
        createObject(folder, 'News Item', 'test1',
            title="Test 1", effectiveDate="2010/10/10")
        createObject(folder, 'News Item', 'test2',
            title="Test 2", effectiveDate="2010/10/09", subject=('foobar',))
        self.activateRoutes()

        transaction.commit()
        self.browser = Browser(self.layer['app'])
        self.browser.handleErrors = False
        browserLogin(self.portal, self.browser)

    def activateRoutes(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IRoutesSettings)
        settings.routes = set(('foobar', 'foobar1', 'foobar2'))

    def test_route_works(self):
        self.browser.open(self.portal.absolute_url() + '/2010/10/10')
        self.assertTrue('Test 1' in self.browser.contents)

    def test_bad_route_still_returns_a_404(self):
        with self.assertRaises(NotFound):
            self.browser.open(self.portal.absolute_url() + '/foobar')

    def test_not_run_if_not_activated(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IRoutesSettings)
        settings.routes = set([])
        transaction.commit()

        with self.assertRaises(NotFound):
            self.browser.open(self.portal.absolute_url() + '/2010/10/10')

    def test_route_part_still_renders_listing(self):
        self.browser.open(self.portal.absolute_url() + '/2010')
        self.assertTrue('Listing' in self.browser.contents)
        self.assertTrue('Test 1' in self.browser.contents)
        self.assertTrue('Test 2' in self.browser.contents)

    def test_static_fragment_part(self):
        self.browser.open(self.portal.absolute_url() + '/foobar1/2010/10/10')
        self.assertTrue('Test 1' in self.browser.contents)
        self.assertTrue('Test 2' not in self.browser.contents)

    def test_query_fragment_part(self):
        self.browser.open(self.portal.absolute_url() + '/foobar2/foobar')
        self.assertTrue('Test 2' in self.browser.contents)
        self.assertTrue('Test 1' not in self.browser.contents)
