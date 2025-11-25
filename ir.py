from lxml import etree
from trytond.pool import PoolMeta


class View(metaclass=PoolMeta):
    __name__ = 'ir.ui.view'

    @classmethod
    def get_rng(cls, type_):
        rng = super().get_rng(type_)
        if type_ in ('form', 'list-form'):
            ns = {'ns': 'http://relaxng.org/ns/structure/1.0'}
            Q = '{http://relaxng.org/ns/structure/1.0}'

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

            # Find the define used by Tryton for field attributes
            # IMPORTANT: it may appear twice, but the one we want is
            # the one with combine="interleave"
            defines = rng.xpath(
                '//ns:define[@name="attlist.field" and @combine="interleave"]',
                namespaces=ns
            )

            if defines:
                define = defines[0]
            else:
                grammar = rng.xpath('/ns:grammar', namespaces=ns)[0]
                define = etree.SubElement(grammar, Q + 'define')
                define.set('name', 'attlist.field')
                define.set('combine', 'interleave')

            # Check if the 'language' attribute already exists
            exists = define.xpath(
                './/ns:attribute/ns:name[.="language"]',
                namespaces=ns
            )
            if not exists:
                optional = etree.SubElement(define, Q + 'optional')
                attribute = etree.SubElement(optional, Q + 'attribute')
                name = etree.SubElement(attribute, Q + 'name')
                name.text = 'language'
                etree.SubElement(attribute, Q + 'text')

        return rng
