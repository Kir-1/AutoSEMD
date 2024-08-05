import io
import os
import re
import time
from functools import wraps
from typing import List

import lxml
from colorama import Fore, Style
from lxml.etree import _Element, _Comment


USE_TIMER = 0

ACC = 0


def timer(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        global ACC
        t0 = time.perf_counter()
        res = f(*args, **kwargs)
        t1 = time.perf_counter()
        print(f'{Fore.LIGHTBLACK_EX}Время работы {f.__name__}: {t1 - t0}{Style.RESET_ALL}')
        ACC += t1 - t0
        return res

    return wrapper if USE_TIMER else f


@timer
def get_xml_doc(path: str):
    with io.open(path, "rb") as f:
        document_example = f.read()

    return document_example


@timer
def get_tag_or_comment_text(element):
    if isinstance(element, _Comment):
        return element.text
    if isinstance(element, _Element):
        return str(re.sub(r'{.*}', '', str(element.tag)))

    if isinstance(element, str):
        # match = re.search(r'{.*}', element)
        return str(re.sub(r'{.*}', 'xsi:', str(element)))

    raise TypeError('Not lxml.etree._Element or lxml.etree._Comment type or str')


@timer
def get_comment_text(element):
    if isinstance(element, _Comment):
        return element.text
    raise TypeError('Not lxml.etree._Comment type')


reversed_namespaces = {
    'urn:f103': 'f103',
    'urn:f88': 'f88',
    'urn:fias': 'fias',
    'urn:hl7-org:': 'ns',
    'urn:hl7-org:v3': 'ns',
    'urn:hl7-ru:': 'ns',
    'urn:hl7-ru:PII': 'PII',
    'urn:hl7-ru:address': 'address',
    'urn:hl7-ru:fias': 'fias',
    'urn:hl7-ru:identity': 'identity',
    'urn:hl7-ru:medService': 'medService',
    'urn:tmk': 'tmk',
    "http://www.w3.org/2001/XMLSchema-instance": "xsi"
}

# http://www.w3.org/2001/XMLSchema-instance

@timer
def get_ns(element):
    if isinstance(element, lxml.etree._Element):
        match = re.search(r'{((.*:?.*)?:(.*?))}', element.tag)
        if match:
            reversed_namespaces.setdefault(match.group(1), match.group(len(match.groups())))
            if not reversed_namespaces.get(match.group(1)):
                print('***', element.tag)
            return reversed_namespaces.get(match.group(1))
        else:
            print('***', element.tag)
    else:
        # print(type(element), element)
        ...




@timer
def get_parent_map(tree):
    parent_map = {}
    for parent in tree.iter():
        cnt_number_of_elements = {get_tag_or_comment_text(child): 1 for child in parent}

        for child_number, child in enumerate(child for child in parent):
            parent_map[(id(child), child)] = (id(parent), parent, cnt_number_of_elements[get_tag_or_comment_text(child)])
            cnt_number_of_elements[get_tag_or_comment_text(child)] += 1

    return parent_map


@timer
def get_elements_by_attribute(xml_tree, attr_name: str):
    elements = []
    for elem in xml_tree.iter():
        if attr_name in elem.attrib:
            elements += [elem]
    return elements


@timer
def get_elements_by_attributes(xml_tree, attr_names: List[str]):
    elements = []
    for elem in xml_tree.iter():
        if all(attr_name in elem.attrib for attr_name in attr_names):
            elements += [elem]
    return elements


@timer
def find_ancestors(element, parents: dict):
    ancestors = []
    path = [f'{get_ns(element)}:{get_tag_or_comment_text(element)}']
    element_set = (id(element), element)
    while element_set is not None:
        element_set = parents.get(element_set)
        if element_set is not None:
            element = element_set[1]
            ancestors += [element]
            path[-1] += f'[{element_set[2]}]'
            path += [f'{get_ns(element)}:{get_tag_or_comment_text(element)}']
            element_set = (element_set[0], element_set[1])

    return '/' + '/'.join(reversed(path))


def get_elements_by_name(
        parent_element, elem_namespace, elem_name: str, ns: dict, elem_cls, parents, etalon=False
):

    elems = parent_element.xpath(f'//{elem_namespace}:' + f'{elem_name}', namespaces=ns)
    elems_attrib = []
    for i, elem in enumerate(elems):
        elem.attrib['path'] = find_ancestors(elem, parents)[1]
        elems_attrib += [elem_cls(elem.attrib, etalon)]
        if elem.attrib.get('codeSystem') is None:
            print(f'{i} {elem_name} is None')
            ancestors = find_ancestors(elem, parents)

    return elems_attrib


if __name__ == '__main__':
    from lxml import etree
    path = r'C:\Users\user\PycharmProjects\AutoSEMD\props\81.xml'
    xml_data = get_xml_doc(path=path)
    xml_tree = etree.fromstring(xml_data)
    parent_map = get_parent_map(xml_tree)

    el = xml_tree.xpath('//ns:ClinicalDocument/ns:documentationOf[1]/ns:serviceEvent[1]/ns:performer[6]/ns:assignedEntity[1]/ns:addr[1]/address:stateCode[1]',
                        namespaces = {
                            'PII': 'urn:hl7-ru:PII',
                            'address': 'urn:hl7-ru:address',
                            'f103': 'urn:f103',
                            'f88': 'urn:f88',
                            'fias': 'urn:hl7-ru:fias',
                            'identity': 'urn:hl7-ru:identity',
                            'medService': 'urn:hl7-ru:medService',
                            'ns': 'urn:hl7-org:v3',
                            'tmk': 'urn:tmk'
                        })[0]
    res = get_tag_or_comment_text(el)
    print(res)