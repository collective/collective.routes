Changelog
=========

1.1a2 (2014-08-29)
------------------

- Added Italian translation
  [giacomos]

- Added some i18n strings and 2 script for i18n rebuild
  [giacomos]

- plone 4.3 compat imports
  [Lewicki]

1.1a1 (2012-02-28)
------------------

- Added Spanish and Brazilian Portuguese translations
  [hvelarde]

- Move to using plone.app.registry
  [saibatizoku]

- Make work with plone.locking
  [vangheem]

- provide ability to specify the view to traverse to
  in route configuration
  [vangheem]

- do not apply IWrappedContext interface
  [vangheem]

- add IRoutedRequest layer dynamically to request when
  routing request so you can override specific parts of
  plone only when routed.
  [vangheem]

- add ability to provide custom predicates
  [vangheem]

- add ability to provide a custom breadcrumb factory
  [vangheem]

- added addRoute parameter of allowPartialMatch so that
  you do not have to match an entire url when matching
  url against a route.
  [vangheem]


1.0a1 (2011-10-07)
------------------

- Initial release
