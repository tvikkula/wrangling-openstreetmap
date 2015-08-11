import xml.etree.cElementTree as ET
import pprint
import json
import re
import codecs
DATA = "../data/hesa.osm"
# Regex's for problematic tags:
lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

def shape_element(element):
    CREATED = [ "version", "changeset", "timestamp", "user", "uid"]
    node = {}
    node["pos"] = []
    if element.tag == "node" or element.tag == "way":
        node["type"] = element.tag
        for key, value in element.attrib.iteritems():
            if key in CREATED:
                if not "created" in node:
                    node["created"] = {}
                node["created"][key] = value
            elif key == "lon":
                node["pos"].append(float(value))
            elif key == "lat":
                node["pos"].insert(0, float(value))
            else:
                node[key] = value
        for tag in element.findall("tag"):
            tagkey = tag.attrib["k"]
            tagval = tag.attrib["v"]
            if tagkey.startswith("addr:"):
                if not "address" in node:
                    node["address"] = {}
                node["address"][tagkey.replace("addr:", "")] = \
                tagval
            else:
                node[tagkey] = tagval
        for tag in element.findall("nd"):
            if not "node_refs" in node:
                node["node_refs"] = []
            node["node_refs"].append(tag.attrib["ref"])

        return node
    else:
        return None

# Courtesy of Udacity:
def process_map(file_in, pretty = False):
    file_out = "{0}.json".format(file_in)
    meta_file_out = "{0}_metadata.json".format(file_in)
    summarydata = {}
    users = {}
    errors = {}
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            if errorintagkeys(element, errors):
                pass
            summary(element.tag, summarydata)
            checkusercontribs(element, users)
            el = shape_element(element)
            if el:
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    with codecs.open(meta_file_out, "w") as fo:
        fo.write(json.dumps(summarydata) + "\n")
        fo.write(json.dumps(users) + "\n")
        fo.write(json.dumps(errors) + "\n")
    return summarydata, users, errors

def summary(tag, summary):
    """
    Takes a tag as input and adds it to the summary-dict.

    Args:
        tag: Tag of the element in question.
        summary: A dict consisting of summary-data of the tags
        in the osm-dataset.

    Returns:
        void
    """
    summary["_id"] = "tags"
    if (tag in summary):
        summary[tag] = summary[tag] + 1
    else:
        summary[tag] = 1

def errorintagkeys(elem, keys):
    """
    Checks whether the given elem (if a tag) contains erronous input
    that could cause problems in MongoDB.

    Args:
        elem: The xml-element in question.
        keys: The dictionary displaying error-statistics of the tag-keys
        in the dataset.

    Returns:
       boolean: A boolean-value indicating whether the tag-key contained
       an error or not.
    """
    keys["_id"] = "errors"
    error = False
    if elem.tag == "tag":
        if problemchars.match(elem.attrib['k']):
            print "problemchars found!"
            if ("problemchars" in keys):
                keys["problemchars"] = keys["problemchars"] + 1
            else:
                keys["problemchars"] = 1
            error = True
        elif elem.attrib['k'].count(':') > 1:
            if ("toomanycolons" in keys):
                keys["toomanycolons"] = keys["toomanycolons"] + 1
            else:
                keys["toomanycolons"] = 1
            error = True
        elif lower.match(elem.attrib['k']):
            if ("lower" in keys):
                keys["lower"] = keys["lower"] + 1
            else:
                keys["lower"] = 1
        elif lower_colon.match(elem.attrib['k']):
            if ("lower_colon" in keys):
                keys["lower_colon"] = keys["lower_colon"] + 1
            else:
                keys["lower_colon"] = 1
        if not error:
            if ("correct" in keys):
                keys["correct"] = keys["correct"] + 1
            else:
                keys["correct"] = 1
    return error

def checkusercontribs(elem, users):
    """
    Checks a uid of the element and adds corresponding
    numerics to the user contribution dict.

    Args:
        elem: The xml-element in question.
        users: The users-dictionary used to check whether
        the user already exists in the dict.

    Returns:
        void
    """
    users["_id"] = "users"
    if elem.tag in ("node", "way", "relation"):
        if (elem.attrib["user"] in users):
            users[elem.attrib["user"]] = \
                users[elem.attrib["user"]] + 1
        else:
            users[elem.attrib["user"]] = 1

if __name__ == "__main__":
    sums, errors, users = process_map(DATA)
    pprint.pprint(sums)
    pprint.pprint(errors)
    pprint.pprint(users)
