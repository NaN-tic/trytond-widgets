# This file is part widgets module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.tests.test_tryton import ModuleTestCase
from trytond.modules.widgets import tools


class WidgetsTestCase(ModuleTestCase):
    'Test Widgets module'
    module = 'widgets'

    def test_tools(self):
        "Test tools"

        # EditorJS to markdown
        value = """
            {"time":1745489360215,"blocks":[
            {"id":"bHSf_DWCks","type":"header","data":{"text":"HEADER","level":2},"tunes":{"textVariant":"","textAlign":{"alignment":"left"}}},
            {"id":"UiBKpCMOn9","type":"paragraph","data":{"text":"Test paragraph"},"tunes":{"textVariant":"","textAlign":{"alignment":"left"}}},
            {"id":"Bhd62vxvDB","type":"list","data":{"style":"unordered","items":["list1"]},"tunes":{"textVariant":"","textAlign":{"alignment":"left"}}},
            {"id":"HbRKWv6Rkr","type":"list","data":{"style":"unordered","items":["list2"]},"tunes":{"textVariant":"","textAlign":{"alignment":"left"}}},
            {"id":"bHuvUZOXvo","type":"quote","data":{"text":"quote","caption":"","alignment":"left"},"tunes":{"textVariant":"","textAlign":{"alignment":"left"}}},
            {"id":"APp1Gp2DWU","type":"code","data":{"code":"code"},"tunes":{"textVariant":"","textAlign":{"alignment":"left"}}},
            {"id":"9J1x5b604K","type":"image","data":{"caption":"","withBorder":false,"withBackground":false,"stretched":false,"file":{"url":"widgets/attachment/1"}},"tunes":{"textVariant":"","textAlign":{"alignment":"left"}}}
            ],"version":"2.31.0-rc.7"}
            """
        markdown_text = tools.js_to_text(value)
        self.assertIn('# HEADER\\n', markdown_text)
        self.assertIn('- list1\n', markdown_text)
        self.assertIn('> quote\\n', markdown_text)
        self.assertIn('```\ncode\n```\\n', markdown_text)
        self.assertIn('![](widgets/attachment/1)\\n', markdown_text)

del ModuleTestCase
