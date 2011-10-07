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
	 	defaultQuery={'portal_type': 'News Item'})


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
                      'sort_order': 'reverse'})

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
                       'sort_order': 'reverse'})

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
