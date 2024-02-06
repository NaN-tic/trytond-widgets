from trytond.model import ModelView, fields
from trytond.pool import PoolMeta, Pool
import json, re


def js_to_html(content_block):
    '''
    Converts editorJS data blocks into an html document
    '''
    if not content_block:
        return ''
    html = '<html><body>'
    js_object = json.loads(content_block)
    for block in js_object['blocks']:
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
            case 'checklist':
                html += '<form>'
                counter = 0
                for entry in block['data']['items']:
                    is_checked = "false"
                    if entry['checked']:
                        is_checked = "true"
                    html += '<input type="checkbox" id=checkbox"' + str(counter) + '" value=checkbox' + str(counter) + '" checked=' + is_checked + '/>'
                    html += '<label for=checkbox' + str(counter) + '>'+ entry['text'] + '</label>'
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
                html += '<img src=' + block['data']['file']['url'] + '/>'
        html += '<br />'

    html = html[:-3]
    html += '</body></html>'
    return html

def text_to_js(text):
    '''
    Converts text to a dictionary of datablocks to be used with editorJS using
    Markdown-like structure
    '''
    datablocks = []
    current_block = {'data' : {}}
    text_blocks = text.split('\n\n')
    for block in text_blocks:
        if not block:
            continue
        match block[0]:
            case '#':
                current_block['type'] = 'header'
                current_block['data']['level'] = len(block.split(' ')[0])
                current_block['data']['text'] = block.strip('#').strip(' ')
                datablocks.append(current_block.copy())
            case '-':
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
            case '>':
                current_block['type'] = 'quote'
                current_block['data']['text'] = block[1:]
                current_block['data']['caption'] = ''
                current_block['data']['alignment'] = 'left'
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
                current_block['data']['text'] = block
                datablocks.append(current_block.copy())
        current_block = {'data' : {}}
    return {'blocks': datablocks}

def url_from_tryton_to_flask(url, prefix):
    if not url.startswith('widgets/attachment/'):
        return url
    id_ = url.split('/')[-1]
    try:
        id_ = int(id_)
    except:
        return url
    name = attachment_name_from_id(id)
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
