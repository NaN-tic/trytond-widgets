from lxml import etree
from trytond.pool import PoolMeta


class View(metaclass=PoolMeta):
    __name__ = 'ir.ui.view'

    @classmethod
    def get_rng(cls, type_):
        rng = super().get_rng(type_)
        if type_ in ('form', 'list-form'):
            # Add 'block' and 'code' as possible values for the 'widget' attribute
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

            # Using RNG format allow defining a new attribute named 'language':
            #
            # <define name="attlist.field" combine="interleave">
            #   <optional>
            #     <attribute>
            #       <name ns="">language</name>
            #       <text/>
            #     </attribute>
            #   </optional>
            # </define>
            define = rng.xpath(
                '/ns:grammar',
                namespaces={'ns': 'http://relaxng.org/ns/structure/1.0'})[0]
            define = etree.SubElement(define, '{http://relaxng.org/ns/structure/1.0}define')
            define.set('name', 'attlist.field')
            define.set('combine', 'interleave')
            optional = etree.SubElement(define, '{http://relaxng.org/ns/structure/1.0}optional')
            attribute = etree.SubElement(optional, '{http://relaxng.org/ns/structure/1.0}attribute')
            name = etree.SubElement(attribute, '{http://relaxng.org/ns/structure/1.0}name')
            name.text = 'language'
            etree.SubElement(attribute, '{http://relaxng.org/ns/structure/1.0}text')
        return rng
