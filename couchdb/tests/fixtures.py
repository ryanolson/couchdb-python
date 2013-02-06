# -*- coding: utf-8 -*-
import datetime
from couchdb.mapping import Document
from schematics.models import Model
from schematics.types import *
from schematics.types.compound import ListType, ModelType
from schematics.serialize import wholelist, whitelist, blacklist

"""
AuthUser is the base class for a more general User class.  AuthUser
is designed to encapsulate all the basic authentication for the
User class.

AuthUser tests ModelType via the AuthUser.Session class.  This ModelType
tests an auto_fill fields and two fields with default options, one being
callable and the other being None.

AuthUser requires both the email and _password fields be valid.  AuthUser
also tests the ListType field using the Session ModelType as entries.

AuthUser also has a "hidden" field in _password.  The password
property uses the _get_password and _set_password for a getter/setter.
The setter automatically hashes the value passed with a salted string.
CouchDB will not let us save a field with the name "_password", 
(CouchDB reserves _'ed attributes), so we use the "print_name" feature
so that the value of the _password field will be serialized to "password"
with any of the schematics.serialize routines.

This leaved one headache.  We don't want to rehash the value of password
when loading the Document from CouchDB.  Thus we have the condition in 
__init__ that ignores the "password" keyword if "_rev" is present.

"""
class AuthUser(Document):
    class Session(Model):
        token = UUIDType(auto_fill=True)
        created_on = DateTimeType(default=datetime.datetime.utcnow)
        device_info = DictType(default=None)
        class Options:
           roles = {
              'mysessions': blacklist('token')
           }
    email = EmailType(required=True)
    sessions = ListType(ModelType(Session))
    _password = MD5Type(required=True,print_name="password")
    class Options:
        roles = {
           'me': blacklist('_password','sessions'),
           'mysessions': blacklist('_password')
        }

    def __init__(self, *args, **kwargs):
        super(AuthUser, self).__init__(*args, **kwargs)
        if 'password' in kwargs and '_rev' not in kwargs:
           self._password = self._salted_password(kwargs['password'])

    def _get_password(self):
        return self._password

    def _set_password(self,passwd):
        self._password = self._salted_password(passwd)

    password = property(_get_password, _set_password)
    
    def challenge_password(self,passwd):
        if self.password == self._salted_password(passwd): return True
        return False

    def _salted_password(self, passwd):
        s = "salt+{}".format(passwd)
        return MD5Type.generate(s)

class User(AuthUser):
    first_name = StringType()
    # TODO - Figure out how User can inherit Options from AuthUser
    class Options:
        roles = {
           'me': blacklist('_password','sessions'),
           'mysessions': blacklist('_password')
        }

