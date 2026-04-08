from cryptography.fernet import Fernet, InvalidToken
from trytond.config import config
from trytond.exceptions import UserError
from trytond.i18n import gettext

FERNET_KEY = config.get('cryptography', 'fernet_key')


class FernetEncryptionMixin:

    @classmethod
    def get_fernet(cls):
        if not FERNET_KEY:
            raise UserError(gettext('widgets.msg_missing_fernet_key'))
        return Fernet(FERNET_KEY)

    def get_fernet_value(self, name):
        if not name.endswith('_decrypted'):
            if getattr(self, '%s_encrypted' % name, None):
                return 'x' * 10
            return None

        clear_name = name[:-10]
        if clear_name not in self._fields:
            raise UserError(gettext(
                'widgets.msg_unknown_decrypted_field',
                field=clear_name))

        encrypted_name = '%s_encrypted' % clear_name
        encrypted_value = getattr(self, encrypted_name, None)
        if not encrypted_value:
            return None
        try:
            decrypted = self.get_fernet().decrypt(bytes(encrypted_value))
        except InvalidToken as exc:
            raise UserError(gettext(
                    'widgets.msg_invalid_fernet_token',
                    field=clear_name)) from exc
        clear_field = self._fields[clear_name]
        clear_field = getattr(clear_field, '_field', clear_field)
        if clear_field._type == 'binary':
            return decrypted
        return decrypted.decode('utf-8')

    @classmethod
    def set_fernet_value(cls, records, name, value):
        if value == 'x' * 10:
            return
        encrypted_name = '%s_encrypted' % name
        clear_field = cls._fields[name]
        clear_field = getattr(clear_field, '_field', clear_field)
        encrypted_value = None
        if value not in (None, ''):
            if clear_field._type == 'binary':
                value = bytes(value)
            else:
                value = value.encode('utf-8')
            encrypted_value = cls.get_fernet().encrypt(value)
        cls.write(records, {encrypted_name: encrypted_value})