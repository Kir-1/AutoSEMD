# Парсит шапки всех документов в папке etalons
import json
from pprint import pprint
from lxml import etree
from lxml.etree import _Element, _Comment
import utils
from utils import *

base_headers_values = {}

namespaces = {
    'ns': 'urn:hl7-org:v3'
}


def main_logic(path):

    xml_data = get_xml_doc(path=path)
    xml_tree = etree.fromstring(xml_data)
    parent_map = get_parent_map(xml_tree)

    ClinicalDocument = xml_tree.xpath('//ns:ClinicalDocument', namespaces=namespaces)[0]

    def rec(root, last_comment='', indent=0):

        for element in root.iterchildren():

            if type(element) == _Comment:
                last_comment = get_tag_or_comment_text(element)

            if type(element) != _Comment and get_tag_or_comment_text(element) != 'component':

                path = find_ancestors(element, parent_map)

                if element.attrib or element.text and element.text.strip():

                    base_headers_values.setdefault(path, {'comment': ''})
                    base_headers_values[path]['comment'] = last_comment

                    for key in element.attrib:
                        key = get_tag_or_comment_text(key)
                        # base_headers_values[path].setdefault(key, {'@type': '', 'examples': []})
                        base_headers_values[path].setdefault(key, {'@type': '^.+$'})
                        # base_headers_values[path][key]['examples'] += [element.attrib[key]]
                    if element.text and element.text.strip():
                        base_headers_values[path].setdefault('text', {'@type': '^.+$'})
                    # print(path)
                # print(' ' * indent, get_tag_or_comment_text(element), sep='')

                # if len(element) == 0:
                #     print(' ' * indent, 'END', sep='')

                rec(element, last_comment, indent=indent + 4)

    rec(root=ClinicalDocument)


if __name__ == '__main__':

    script_dir = os.path.dirname(os.path.abspath(__file__))
    relative_path = os.path.join(script_dir, 'etalons')
    dir = relative_path
    for root, dirs, files in os.walk(dir):
        for file in files:
            path = os.path.join(root, file)
            print(path)
            main_logic(path)

    print('\nNAMESPACES:')
    pprint(utils.reversed_namespaces)

    # print('\nbase_headers_values:')
    # pprint(base_headers_values)

    with open('base_headers_values.json', 'w', encoding='utf-8') as json_file:
        json.dump(base_headers_values, json_file, ensure_ascii=False, indent=4)

    print(len(base_headers_values))