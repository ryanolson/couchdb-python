## BaseUser

from couchdb.mapping import Document
from schematics.models import Model
from schematics.types import *
from schematics.types.compound import ListType, ModelType
from schematics.serialize import wholelist, whitelist, blacklist, make_safe_dict, make_safe_json

class AuthUser(Document):
    class Session(Model):
        token = UUIDType(auto_fill=True)
        created_on = DateTimeType(default=datetime.datetime.utcnow)
        device_info = DictType(default=None)
        class Options:
           roles = {
              'test': whitelist('created_on', 'device_info')
           }
    email = EmailType(required=True)
    sessions = ListType(ModelType(Session))
    _password = MD5Type(required=True,print_name="password")
    class Options:
        roles = {
           'test': blacklist('_password')
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
    class Options:
        roles = {
           'test': blacklist('_password')
        }

