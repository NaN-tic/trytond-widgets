from trytond.model import ModelView, fields
from trytond.pool import PoolMeta, Pool
import json, re, html2text
from bs4 import BeautifulSoup


def js_to_html(content_block, url=''):
    '''
    Converts editorJS data blocks into an html document
    '''
    if not content_block:
        return ''
    html = '<html><body>'
    js_object = json.loads(content_block)
    for block in js_object['blocks']:
        was_p = False
        match block['type']:
            case 'list':
                if block['data']['style'] == 'unordered':
                    html += '<ul>'
                    for entry in block['data']['items']:
                        html += '<li>' + entry + '</li>'
                    html += '</ul>'
                else:
                    html += '<ol>'
                    for entry in block['data']['items']:
                        html += '<li>' + entry + '</li>'
                    html += '</ol>'
            case 'header':
                html += '<h' + str(block['data']['level']) + '>' + block['data']['text'] + '</h' + str(block['data']['level']) + '>'
            case 'paragraph':
                html += '<p>' + block['data']['text'] + '</p>'
                was_p = True
            case 'checklist':
                html += '<form>'
                counter = 0
                for entry in block['data']['items']:
                    is_checked = "false"
                    if entry['checked']:
                        is_checked = "true"
                    html += '<input type="checkbox" id="checkbox' + str(counter) + '" value="checkbox' + str(counter) + '" checked="' + is_checked + '" />'
                    html += '<label for="checkbox' + str(counter) + '">'+ entry['text'] + '</label>'
                    counter += 1
                html += '</form>'
            case 'table':
                html += '<table>'
                counter = 0
                for entry in block['data']['content']:
                    html += '<tr>'
                    for text in entry:
                        if block['data']['withHeadings'] == True and counter == 0:
                            html += '<th>' + text + '</th>'
                        else:
                            html += '<td>' + text + '</td>'
                    html += '</tr>'
                html += '</table>'
            case 'delimeter':
                html += '<hr />'
            case 'warning':
                html += '<table><tr><th>' + block['data']['title'] + '</th></tr>'
                html += '<tr><td>' + block['data']['message'] + '</td></tr>'
            case 'code':
                html += '<code>'
                html += re.sub('[^\\]\\n', '<br />',block['data']['code'])
                html += '</code>'
            case 'quote':
                html += '<blockquote cite=' + block['data']['caption'] + '>' + block['data']['text'] + '</blockquote>'
            case 'image':
                html += '<img src="' + url_from_tryton_to_flask(block['data']['file']['url'], url)+ '" />'
            case 'link':
                html += '<a href=' + block['data']['url'] + ' ></a>'
        if not was_p:
            html += '<br />'

    #html = html[:-3]
    html += '</body></html>'
    return html

def text_to_js(text):
    '''
    Converts text to a dictionary of datablocks to be used with editorJS using
    Markdown-like structure
    '''
    datablocks = []
    text_blocks = text.split('\n')
    for block in text_blocks:
        if not block:
            continue
        current_block = {'data' : {}}
        block = block.strip('\n')
        block = block.lstrip('\\')
        match block[0]:
            case '#':
                current_block['type'] = 'header'
                current_block['data']['level'] = len(block.split(' ')[0])
                current_block['data']['text'] = block.strip('#').strip(' ')
                datablocks.append(current_block.copy())
            case '-':
                if len(block) > 1:
                    if block[1] and block[2]:
                        if block[1] == '-' and block[2] == '-':
                            current_block['type'] = 'delimeter'
                            current_block['data'] = {}
                            datablocks.append(current_block.copy())
                        else:
                            current_block['type'] = 'list'
                            current_block['data']['style'] = 'unordered'
                            current_block['data']['items'] = [b.strip('-') for b in block.split('\n')]
                            datablocks.append(current_block.copy())
            case '1':
                if block[1]:
                    if block[1] == '.':
                        current_block['type'] = 'list'
                        current_block['data']['style'] = 'ordered'
                        current_block['data']['items'] = [b[2:] for b in block.split('\n')]
                        datablocks.append(current_block.copy())
            case '`':
                current_block['type'] = 'code'
                current_block['data']['code'] = block.strip('`')
                datablocks.append(current_block.copy())
                '''
            case '>':
                current_block['type'] = 'quote'
                current_block['data']['text'] = block[1:]
                current_block['data']['caption'] = ''
                current_block['data']['alignment'] = 'left'
                datablocks.append(current_block.copy())
                '''
            case '>':
                if len(block) > 1:
                    if block[1] and block[2]:
                        current_block['type'] = 'list'
                        current_block['data']['style'] = 'unordered'
                        current_block['data']['items'] = [b.strip('>') for b in block.split('\n')]
                        datablocks.append(current_block.copy())
            case '!':
                current_block['type'] = 'image'
                current_block['data']['url'] = block[block.find('('):block.find(')')]
                datablocks.append(current_block.copy())
            case '<':
                if re.match('<image>', block):
                    current_block['type'] = 'image'
                    current_block['data']['url'] = 'widgets/attachment/' + block.split('>')[-1].split(' ')[0].strip('"').strip("'")
                    datablocks.append(current_block.copy())
            case _:
                current_block['type'] = 'paragraph'
                current_block['data']['text'] = block.strip(' ')
                if len(current_block['data']['text'].strip(' ')) > 0:
                    datablocks.append(current_block.copy())
    return json.dumps({'blocks': datablocks})

def html_to_js(html_string):
    converted = html2text.html2text(html_string)
    processed = text_to_js(converted)
    return processed

    '''
    if html_string is '' or html_string is None:
        return ''
    datablocks = []
    html_json = BeautifulSoup(html_string, 'lxml')
    for component in html_json.find_all(True):
        print('-----' + str(component.name) + '.......')
        current_block = {'data': {}}
        if not re.match(component.name, 'h[1-6]'):
            match component.name:
                case 'p':
                    current_block['type'] = 'paragraph'
                    current_block['data']['text'] = str(component.contents)
                    datablocks.append(current_block.copy())
                case 'delimeter':
                    current_block['type'] = 'delimeter'
                    current_block['data'] = {}
                    datablocks.append(current_block.copy())
                case 'code':
                    current_block['type'] = 'code'
                    current_block['data']['code'] = str(component.contents).strip('`')
                    datablocks.append(current_block.copy())
                case 'blockquote':
                    current_block['type'] = 'quote'
                    current_block['data']['caption'] = str(component.find('cite').contents[0])
                    current_block['data']['text'] = str(component.find())
                case 'ul':
                    current_block['type'] = 'list'
                    current_block['data']['style'] = 'unordered'
                    current_block['data']['items'] = []
                    for list_entry in component.find_all('li'):
                        current_block['data']['items'].append(list_entry.contents)
                    datablocks.append(current_block.copy())
                case 'ol':
                    current_block['type'] = 'list'
                    current_block['data']['style'] = 'ordered'
                    current_block['data']['items'] = []
                    for list_entry in component.find_all('li'):
                        current_block['data']['items'].append(list_entry.contents)
                    datablocks.append(current_block.copy())
                case 'form':
                    current_block['type'] = 'checklist'
                    current_block['data']['items'] = []
                    for input in component.find_all('input'):
                        if input.find('checked') == 'true':
                            checked: 'True'
                        else:
                            checked: 'False'
                        checkbox = {
                            'checked': checked,
                            'text': str(input.find())
                        }
                        current_block['data']['items'].append(checkbox)
                    datablocks.append(current_block.copy())
                case 'table':
                    current_block['type'] = 'table'
                    current_block['data'] = []
                    current_block['data']['content'] = []
                    for t_row in component.contents:
                        if t_row.name == 'th':
                            current_block['data']['withHeadings'] = True
                        if t_row.name == 'tr' or t_row.name == 'th':
                            row = []
                            for cell in t_row.contents:
                                if cell.name == 'td':
                                    row.append(cell.contents[0])
                            current_block['data']['content'].append(row)
                    datablocks.append(current_block.copy())
                case 'img':
                    current_block['type'] = 'image'
                    current_block['data']['file'] = {}
                    current_block['data']['file']['url'] = 'widgets/attachment/' + attachment_id_from_name(component[0].split('/')[-1])
                case _:
                    current_block['type'] = 'paragraph'
                    current_block['data']['text'] = str(component.contents)
        else:
            current_block['data']['level'] = int(component.name[1])
            current_block['data']['text'] = str(component.contents)
            datablocks.append(current_block.copy())
            datablocks.append(current_block.copy())
    '''
    return text_to_js(html2markdown.convert(html_string))

def url_from_tryton_to_flask(url, prefix):
    if not 'widgets/attachment' in url:
        return url
    id_ = url.split('/')[-1]
    try:
        id_ = int(id_)
    except:
        return url
    name = attachment_name_from_id(str(id_))
    return prefix + name

def attachment_id_from_name(name):
    pool = Pool()
    Attachment = pool.get('ir.attachment')
    attachments = Attachment.search([('name', '=', name)], limit=1)
    if attachments:
        return attachments[0].id

def attachment_name_from_id(id):
    pool = Pool()
    Attachment = pool.get('ir.attachment')
    attachments = Attachment.search([('id', '=', id)], limit=1)
    if attachments:
        return attachments[0].name