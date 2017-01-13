#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Parses the OSM file and counts the tags by type.
"""
import xml.etree.ElementTree as ET
from pprint import pprint
import operator

OSMFILE = 'data/dallas_texas.osm'

def count_tags(filename):
    """
    Parses the OSM file and counts the tags by type.
    Args:
        filename: name and position of the OSM file
    Returns:
        element_count: dictionary storing elements' tag names and its related frequency
        k_attributes: dictionary storing k attributes and its correponding value in each "tag" element
    """
    element_count = {}
    k_attributes = {}

    # iterate through elements
    for event, element in ET.iterparse(filename, events=("start",)):
        # Iterate through all element tags and get a count for each of them
        element_count[element.tag] = element_count.get(element.tag, 0) + 1

        # for sub elements whose tag is "tag" and has attribute "k", count the occurences for every k attribute
        if element.tag == 'tag' and 'k' in element.attrib:
            k_attributes[element.get("k")] = k_attributes.get(element.get("k"), 0) + 1

    # sort the dictionary by counts in decending order
    k_attributes = sorted(k_attributes.items(), key=operator.itemgetter(1))[::-1]
    element_count = sorted(element_count.items(), key=operator.itemgetter(1))[::-1]

    return element_count, k_attributes

def main():
    """ main function """
    element_count, k_attributes = count_tags(OSMFILE)
    print element_count
    print k_attributes
    return element_count, k_attributes

if __name__ == "__main__":
    main()