domain=collective.routes
if test -e manual.pot; then
        echo "Manual PO entries detected"
        MERGE="--merge manual.pot"
else
        echo "No manual PO entries detected"
        MERGE=""
fi
i18ndude rebuild-pot --pot $domain.pot $MERGE --create $domain ../../
i18ndude sync --pot $domain.pot */LC_MESSAGES/$domain.po

#i18ndude sync --pot plone-manual.pot */*/plone.po
