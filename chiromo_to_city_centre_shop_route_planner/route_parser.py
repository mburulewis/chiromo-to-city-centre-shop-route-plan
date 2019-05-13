from xml.etree.ElementTree import iterparse
from datetime import datetime


class Parser(object):
    def __init__(self, filename='', parse_key = 'element'):
        self.filename = filename
        self.data = None
        self.parse_key = "element"
        self.parsedFile = []
        self.nodes = {}
        self.ways = {}
        self.routes = {}
        self.parseOSM()
        self.setup_nodes()
        self.setup_ways()

    def getAttributes(self, el):
        data = {}
        for key, value in el.attrib.items():
            if key == "id":
                data[key] = value
            elif key == "visible":
                data[key] = value == "true"
            elif key == "version":
                data[key] = int(value)
            elif key == "changeset":
                data[key] = int(value)
            elif key == "timestamp":
                data[key] = value
            elif key == "user":
                data[key] = value
            elif key == "uid":
                data[key] = int(value)
            elif key == "lat":
                data[key] = float(value)
            elif key == "lon":
                data[key] = float(value)

        return data

    def getTags(self, el):
        data = {}
        for tag in el.findall('tag'):
            data[tag.attrib['k']] = tag.attrib['v']

        return data

    def getWayNodes(self, el):
        node_ids = []
        for node in el.findall('nd'):
            node_ids.append(node.attrib['ref'])

        return node_ids

    def getMembers(self, el):
        members = []
        for node in el.findall('member'):
            members.append(node.attrib)

        return members

    def parseOSM(self):
        elements = []
        for _, el in iterparse(self.filename):
            tag = el.tag
            if tag in ('node', 'way', 'relation'):
                data = self.getAttributes(el)
                data.update({
                    "tags": self.getTags(el),
                    "type": tag
                })
                if tag == 'node':
                    data.update({
                        "ways": []
                    })
                elif tag == 'way':
                    data.update({
                        "nodes": self.getWayNodes(el)
                    })
                elif tag == 'relation':
                    data.update({
                        "members": self.getMembers(el)
                    })

                elements.append(data)
                
        self.parsedFile = elements
        return elements

    
    def setup_nodes(self):
        for el in self.parsedFile:
            if el["type"] == "node":
                self.nodes[el["id"]] = el

    def setup_ways(self):
        for el in self.parsedFile:
            if el["type"] == "way":
                nodes = []
                for node_id in el["nodes"]:
                    if node_id in self.nodes:
                        if not el["id"] in self.nodes[node_id]["ways"]:
                            self.nodes[node_id]["ways"].append(el["id"])
                        nodes.append(self.nodes[node_id])

                el["nodes"] = nodes
                self.ways[el["id"]] = el