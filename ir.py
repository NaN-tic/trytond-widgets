from lxml import etree
from trytond.pool import PoolMeta


class View(metaclass=PoolMeta):
    __name__ = 'ir.ui.view'

    @classmethod
    def get_rng(cls, type_):
        rng = super().get_rng(type_)
        if type_ in ('form', 'list-form'):
            widgets = rng.xpath(
                '//ns:define/ns:optional/ns:attribute'
                '/ns:name[.="widget"]/following-sibling::ns:choice',
                namespaces={'ns': 'http://relaxng.org/ns/structure/1.0'})[0]
            subelem = etree.SubElement(widgets,
                '{http://relaxng.org/ns/structure/1.0}value')
            subelem.text = 'block'
            subelem = etree.SubElement(widgets,
                '{http://relaxng.org/ns/structure/1.0}value')
            subelem.text = 'code'
        return rng
