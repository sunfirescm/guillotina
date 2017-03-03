# -*- encoding: utf-8 -*-
from guillotina import configure
from guillotina.interfaces import IGroups
from guillotina.interfaces import ISite
from zope.component import getUtility
from zope.security.interfaces import IInteraction


@configure.service(context=ISite, method='GET', permission='guillotina.AccessContent',
                   name='@user')
async def get_user_info(context, request):
    """Return information about the logged in user.
    """
    result = {}
    groups = set()
    principal = IInteraction(request).principal
    result[principal.id] = {
        'roles': principal.roles,
        'groups': principal.groups,
        'properties': principal.properties
    }
    groups.update(principal.groups)

    group_search = getUtility(IGroups)
    result['groups'] = {}
    for group in groups:
        group_object = group_search.get_principal(group)
        result['groups'][group_object.id] = {
            'roles': group_object.roles,
            'groups': group_object.groups
        }

    return result
