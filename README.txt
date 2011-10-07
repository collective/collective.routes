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
