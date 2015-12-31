Introduction
============

A routes implementation for Plone. What drives the route implementation
is querying the portal catalog.


Example Route::
	
	  /posts/{effective:year}/{effective:month}/{effective:day}


To add a route::
	
	 from collective.routes import addRoute
	 addRoute('BlogItems',
	 	'/posts/{effective:year}/{effective:month}/{effective:day}',
	 	defaultQuery={'portal_type': 'News Item'},
        allowPartialMatch=True)


Enable it
---------

Before the route is usable, you need to first enable the route
on the site you'd like to use it for. This can be done via
the route configuration panel in Site Setup.


Out of the box routes
---------------------

collective.routes has a couple example routes that
it comes pre-packaged with.

blog posts
~~~~~~~~~~

Blog Posts
    `/posts/{effective:year}/{effective:month}/{effective:day}`

Exmaple Urls::
    
    /posts/2011 ~ Show all posts from 2011
    /posts/2011/10 ~ Show all from 2011 and the month of October
    /posts/2011/10/5 ~ Show the blog posted October 5, 2011

Definition::

    addRoute('Blog Posts',
      '/posts/{effective:year}/{effective:month}/{effective:day}',
      defaultQuery={'portal_type': 'News Item',
                      'sort_on': 'effective',
                      'sort_order': 'reverse'},
      allowPartialMatch=True)

tagged content
~~~~~~~~~~~~~~

Tagged
    `/tagged/{Subject}/{Subject}/{Subject}`

Example Urls::

    /tagged/foo ~ Show all posts tagged `foo`
    /tagged/foo/bar ~ Show all posts tagged `foo` and `bar`
    /tagged/foo/bar/woo ~ Show all posts tagged `foo`, `bar` and `woo`

Definition::

    addRoute('Tagged',
         '/tagged/{Subject}/{Subject}/{Subject}',
         defaultQuery={'portal_type': 'News Item',
                       'sort_on': 'effective',
                       'sort_order': 'reverse'},
         allowPartialMatch=True)

Route Syntax
------------

The syntax is really basic and only has a few variations.

Literal
~~~~~~~

Literal string match::

    /string-to-match

Will match "string-to-match"


Query
~~~~~

Match anything and maintain it as a query parameter::

    /{Subject}

Will match any string and then keep the value as a query
parameter to be used for a portal_catalog query.


Date Query
~~~~~~~~~~

Has three sub-directives to match part parts::

    /{effective:year}/{effective:month}/{effective:day}

Which will then put together a query for the portal_catalog to
use.


Customize Object Retrieval
--------------------------

If you'd prefer to bypass the normal portal_catalog query
to retrieve your object, you can provide your own object
finder method.

Example::

    def customObjectFinder(context, **kwargs):
        query = context.query
        site = getSite()
        return site[query['id']]

    addRoute('My Route',
         '/my-route/{id}',
         objectFinder=customObjectFinder)


Fiddle with published object
----------------------------

If you'd like to be able to add interfaces at the last moment
before the traversal is published, this is what you'd use.

This can be useful for adding interfaces since the actual 
published object is wrapped so breadcrumbs are maintained
on publishing.

Example::

    from interfaces import IMySpecialContext
    from zope.interface import alsoProvides

    def myMungeMethod(context):
        alsoProvides(context, IMySpecialContext)

    addRoute('My Route',
         '/foo/{bar}',
         mungeObject=myMungeMethod)


Customize view rendered
-----------------------

You can customize the view that is rendered for the found
object also::

    addRoute('My Route',
         '/foo/{bar}',
         customViewName='@@custom-view')


addRoute Signature
------------------

Allow arguments

routeName(required)
    Name of route

route(required)
    Actual route specification

defaultQuery(defaults to {})
    Default query to provide the finder with

objectFinder(defaults to collective.routes.finders.catalogObjectFinder)
    The method used to find the result published object

mungeObject(defaults to None)
    Since the real published is a wrapper object, this is a method to
    be able to mess with the temporary wrapper object before 
    publication

customViewName(defaults to None)
    Custom view to render for the found object

allowPartialMatch(defaults to False)
    If the whole url is not matched, you can still attempt to publish it.
    This can be useful for catalog finder routes where you want to allow
    the user to provide partial urls and still find objects.

breadcrumbFactory(defaults to None)
    Override breadcrumb generation. Must return a tuple of
    {'absolute_url': url, 'Title': title} values.

customPredicates(defaults to [])
    An iterable of custom predicate functions(s) to check against the incoming request
    that they match. A predicate must take 2 parameters(`request`, `query`) where `request`
    is the current request object and `query` is the currently generated query
    from the route. The function must return a boolean. True if it matches, False it doesn't.

