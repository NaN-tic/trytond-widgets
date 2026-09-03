from lxml import etree

from trytond.pool import PoolMeta


class _WidgetValidator:
    def __init__(self, validator, widgets):
        self._validator = validator
        self._widgets = widgets

    def _prepare_tree(self, tree):
        tree = etree.fromstring(etree.tostring(tree))
        widgets = ' or '.join(f'@widget="{widget}"' for widget in self._widgets)
        for field in tree.xpath(f'.//field[{widgets}]'):
            field.set('widget', 'text')
            field.attrib.pop('language', None)
        return tree

    def _validate_tree(self, tree, method):
        validator = self._validator
        tree = self._prepare_tree(tree)
        while hasattr(validator, '_validator'):
            tree = validator._prepare_tree(tree)
            validator = validator._validator
        return getattr(validator, method)(tree)

    def validate(self, tree):
        return self._validate_tree(tree, 'validate')

    def assertValid(self, tree):
        return self._validate_tree(tree, 'assertValid')

    @property
    def error_log(self):
        validator = self._validator
        while hasattr(validator, '_validator'):
            validator = validator._validator
        return validator.error_log


class View(metaclass=PoolMeta):
    __name__ = 'ir.ui.view'

    @classmethod
    def _validator(cls, type_):
        validator = super()._validator(type_)
        widgets = set()
        if type_ in {'form', 'list-form'}:
            widgets.update({'block', 'code'})
        if widgets and not isinstance(validator, _WidgetValidator):
            validator = _WidgetValidator(validator, widgets)
            key = (cls.__name__, type_)
            validator = cls._get_validator_cache.set(key, validator)
        return validator
