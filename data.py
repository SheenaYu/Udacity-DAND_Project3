#-----------------data.py---------------------#
"""
Parse through the OSM XML dataset and update any inconsistent data
Finally output a JSON file for the purpose of uploading to MongoDB
"""

import xml.etree.cElementTree as ET
import codecs
import pprint
import json
import re
from collections import defaultdict


OSMFILE = "data/dallas_texas.osm"

problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

mapping = { "E": "East", "E.": "East", "W.":"West", "W": "West", "N.": "North", "N": "North", "S": "South", "Rd": "Road",
            "Rd.": "Road", "ln": "Lane", "ln.": "Lane", "Ln": "Lane", "Ln.": "Lane", "Ct": "Court", "dr": "Drive",
            "dr.": "Drive", "Dr": "Drive", "Dr.": "Drive", "st": "Street", "St": "Street", "St.": "Street", "Ste": "Suite",
            "Ste.": "Suite", "Trl": "Trail", "Cir": "Circle", "cir": "Circle", "CR": "Country Road", "Av": "Avenue", "Ave": "Avenue",
            "Ave.": "Avenue", "Hwy": "Highway", "Hwy.": "Highway", "HIghway": "Highway", "Pky": "Parkway", "Pky.": "Parkway",
            "Pkwy": "Parkway", "pkwy": "Parkway", "Fwy": "Freeway", "Fwy.": "Freeway", "BLVD": "Boulevard", "Blvd": "Boulevard",
            "Blvd.": "Boulevard", "Expy": "Expressway", "Expessway": "Expressway"
            }

CREATED = ["version", "changeset", "timestamp", "user", "uid"]

TIGER_NAME_KEYS = ["name_direction_prefix", "name_base", "name_type", "name_direction_suffix"]

def update_postcode(value):
    """
    Replace any postcodes that are not of length 5 with 5-digit string
    """
    postcode = ''
    for char in value:
        if char.isdigit():
            postcode += char
        if len(postcode) == 5:
            break
    return postcode
                    
def update_street(name, mapping):
    """
    Scan through each substring and update any matched substring to their values in dictionary 'mapping'
    """
    words = name.split()
    for w in range(len(words)):
        if words[w] in mapping:
            words[w] = mapping[words[w]]
    name = " ".join(words)
    return name

def process_address_tiger(element, node, address, tiger):
    """
    Specifically deal with the dictionaries 'address' and 'tiger'
    """
    street = {}
    zipcode = set()
    for tag in element.iter("tag"):  
        k = tag.attrib["k"]
        v = tag.attrib["v"]
        problem = problemchars.search(k)

        if problem:
            continue

        # Create dictionary 'address'
        elif k.startswith("addr:"):
            if ":" in k[5:]:
                continue
            else:
                address[k[5:]] = v

        # Create dictionary 'tiger'
        elif k.startswith("tiger:"):
            if k[6:] in TIGER_NAME_KEYS:
                street[k[6:]] = v
            elif k[6:].startswith("zip"):
                if ";" in  v:
                    for z in v.split(";"):
                        zipcode.add(z)
                else:
                    zipcode.add(v)
            elif k[6:] in ["county", "cfcc"]:
                tiger[k[6:]] = v
            else:
                continue

        # Ignore gnis geographical features
        elif k.startswith("gnis:"):
            continue
        # To avoid overwriting the key "type" which records whether the document is a "node" or a "way",
        # Thus I rename the "type" attribute to "location_type"
        elif k == "type":
            node["location_type"] = v
        else:
            node[k] = v

    # Process tiger street name
    if len(street) != 0:
        street_string = " ".join([street[key] for key in TIGER_NAME_KEYS if key in street])
        tiger["street_name"] = update_street(street_string, mapping)

    # Update street in dictionary 'address'
    if "street" in address:
        address["street"] = update_street(address["street"], mapping)
    
    # Process postcodes
    if "postcode" in address:
        address["postcode"] = update_postcode(address["postcode"])
    if len(zipcode) != 0:
        tiger["zipcode"] = [update_postcode(v) for v in list(zipcode)]

    if len(tiger) != 0:
        node["tiger"] = tiger
    if len(address) != 0:
        node["address"] = address




def create_common_attributes_dict(element, common_attr_list, node):
    """
    Create a dictionary to store common attributes for the nodes
    Common attributes are: "version", "changeset", "timestamp", "user", "uid".
    """
    if "created" not in node:
        node["created"] = {}
    for attr in common_attr_list:
        node["created"][attr] = element.attrib[attr]


def shape_element(element):
    """
    Takes an XML tag as input and returns a cleaned and reshaped dictionary for JSON ouput. 
    If the element contains an abbreviated street name, it returns with an updated full street name.
    If the postcodes/zipcodes do not follow 5-digit format, update them with the correct format.
    """
    node = {}
    address = {}
    tiger = {}
    nd_info = []
    if element.tag == "node" or element.tag == "way":
        node["type"] = element.tag
        node["id"] = element.attrib["id"]
        if "visible" in element.attrib:
            node["visible"] = element.attrib["visible"]
        if "lat" in element.attrib:
            node["pos"] = [float(element.attrib["lat"]), float(element.attrib["lon"])]
        create_common_attributes_dict(element, CREATED, node)
        process_address_tiger(element, node, address, tiger)
 
        for tag in element.iter("nd"):
            nd_info.append(tag.attrib['ref'])
        if nd_info != []:
            node['node_refs'] = nd_info

        return node
    
    else:
        return None


# for _, element in ET.iterparse(OSMFILE):
#     node = shape_element(element)
#     if node is not None and 'tiger' in node and "zipcode" in node["tiger"]:
#         print node

def process_map(file_in, pretty = False):
    """
    Outputs a JSON file with the above structure.
    Returns the data as a list of dictionaries.
    """
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        parser = ET.iterparse(file_in)
        for __, elem in parser:
            el = shape_element(elem)
            if el:
                data.append(el)
                # Output to JSON
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
        del parser
    return data


def main_test():
    data = process_map(OSMFILE, False)
    print 'Map processed'

if __name__ == "__main__":
    main_test()
