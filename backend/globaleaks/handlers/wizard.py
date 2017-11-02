# -*- coding: utf-8
#
# wizard
from globaleaks import models
from globaleaks.db import db_refresh_memory_variables
from globaleaks.handlers.admin import tenant
from globaleaks.handlers.admin.context import db_create_context
from globaleaks.handlers.admin.user import db_create_user, db_create_receiver_user
from globaleaks.handlers.base import BaseHandler
from globaleaks.models import config, l10n, profiles
from globaleaks.orm import transact
from globaleaks.rest import requests, errors
from globaleaks.utils.utility import log, datetime_null


@transact
def wizard(store, tid, request, language):
    models.db_delete(store, l10n.EnabledLanguage,
                     l10n.EnabledLanguage.name != language,
                     l10n.EnabledLanguage.tid == tid)

    tenant = models.db_get(store, models.Tenant, id=tid)
    tenant.label = request['node']['name']

    node = config.NodeFactory(store, tid)

    if node.get_val(u'wizard_done'):
        log.err("DANGER: Wizard already initialized!")
        raise errors.ForbiddenOperation

    node._query_group()

    node.set_val(u'name', request['node']['name'])
    node.set_val(u'default_language', language)
    node.set_val(u'wizard_done', True)

    node_l10n = l10n.NodeL10NFactory(store, tid)

    node_l10n.set_val(u'description', language, request['node']['description'])
    node_l10n.set_val(u'header_title_homepage', language, request['node']['name'])

    profiles.load_profile(store, tid, request['profile'])

    request['receiver']['username'] = u'recipient'
    request['receiver']['language'] = language

    _, receiver = db_create_receiver_user(store, tid, request['receiver'], language)

    request['context']['receivers'] = [receiver.id]
    context = db_create_context(store, tid, request['context'], language)

    admin_dict = {
        'username': u'admin',
        'password': request['admin']['password'],
        'role': u'admin',
        'state': u'enabled',
        'deletable': False,
        'name': u'Admin',
        'public_name': u'Admin',
        'description': u'',
        'mail_address': request['admin']['mail_address'],
        'language': language,
        'password_change_needed': False,
        'pgp_key_remove': False,
        'pgp_key_fingerprint': '',
        'pgp_key_public': '',
        'pgp_key_expiration': datetime_null()
    }

    db_create_user(store, tid, admin_dict, language)

    db_refresh_memory_variables(store)


class Wizard(BaseHandler):
    """
    Setup Wizard handler
    """
    check_roles = 'unauthenticated'
    invalidate_cache = True

    def post(self):
        request = self.validate_message(self.request.content.read(),
                                        requests.WizardDesc)

        return wizard(self.request.tid, request, self.request.language)
