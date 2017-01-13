#-----------------audit.py---------------------#

# OpenStreetMap Data Case Study

"""
- Audits the OSMFILE and changes the variable 'mapping' to reflect the changes
    needed to fix the unexpected street types to the appropriate ones in the
    expected list. Mappings have been added only for the actual problems found
    in this OSMFILE, not for a generalized solution, since that may and will
    depend on the particular area being audited.
- The update function fixes the street name. It takes a string with a street
    name as an argument and returns the fixed name.
"""
import xml.etree.cElementTree as ET
import pprint
import re
from collections import defaultdict

OSMFILE = "data/sample_dallas_texas.osm"

street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
expected = ["Street", "Avenue", "Avenida", "Boulevard", "Bay", "Creek", "Drive",
            "Court", "Place", "Square", "Lane", "Road", "Run",
            "Trail", "Parkway", "Commons", "Circle", "Crossing",
            "Cove", "Highway", "Freeway", "Tollway", "Park", "Plaza", "Way", "South", "North", "East", "West", 
            "Expressway", "Ridge"]

# Updated dictionary 'mapping' reflects changes needed in dallas.osm file
mapping = { "E": "East", "E.": "East", "W.":"West", "W": "West", "N.": "North", "N": "North", "S": "South", "Rd": "Road",
            "Rd.": "Road", "ln": "Lane", "ln.": "Lane", "Ln": "Lane", "Ln.": "Lane", "Ct": "Court", "dr": "Drive",
            "dr.": "Drive", "Dr": "Drive", "Dr.": "Drive", "st": "Street", "St": "Street", "St.": "Street", "Ste": "Suite",
            "Ste.": "Suite", "Trl": "Trail", "Cir": "Circle", "cir": "Circle", "CR": "Country Road", "Av": "Avenue", "Ave": "Avenue",
            "Ave.": "Avenue", "Hwy": "Highway", "Hwy.": "Highway", "HIghway": "Highway", "Pky": "Parkway", "Pky.": "Parkway",
            "Pkwy": "Parkway", "pkwy": "Parkway", "Fwy": "Freeway", "Fwy.": "Freeway", "BLVD": "Boulevard", "Blvd": "Boulevard",
            "Blvd.": "Boulevard", "Expy": "Expressway", "Expessway": "Expressway"
            }


def audit_street_type(street_types, street_name):
    """
    Adds potentially problematic street names to list 'street_types'
    Args:
        street_types: a dictionary counting the occurrences of unexpected street types
        street_name: a string of full street name
    Returns:
        a complete street_type dictionary recording unexpected street types
    """
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            if street_type.isdigit():
                try:
                    true_street_type = street_name.split()[-2]
                    if true_street_type not in expected:
                        street_types[true_street_type].add(street_name)
                except IndexError:
                    pass
            else:
                street_types[street_type].add(street_name)


def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")


def audit(osmfile):
    """
    Returns a list of problematic street type values
    which will be used for populating the dictionary 'mapping'
    """
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    osm_file.close()
    return street_types


def update(name, mapping):
    """
    Scan through each word in the street name 
    and update any matched word to their corresponding values in dictionary 'mapping'

    Args:
        name: string of full street name
        mapping: dictionary "mapping" 

    Returns:
        Updated street name
    """
    words = name.split()
    for w in range(len(words)):
        if words[w] in mapping:
            words[w] = mapping[words[w]]
    name = " ".join(words)
    return name


def example_test():
    st_types = audit(OSMFILE)
    pprint.pprint(dict(st_types))
    for st_type, ways in st_types.iteritems():
        for name in ways:
            better_name = update(name, mapping)
            print name, "=>", better_name
            if name == "S Central Expy":
                assert better_name == "South Central Expressway"
            if name == "West Southlake Blvd.":
                assert better_name == "West Southlake Boulevard"


if __name__ == '__main__':
    example_test()
