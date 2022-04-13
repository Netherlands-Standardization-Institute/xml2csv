
from xml.etree import ElementTree


xmlTree = ElementTree.ElementTree(file="data/xml/663.xml")
print(xmlTree.getroot().tag)
sections = xmlTree.findall("body/sec")
paragraphs = []
for section in sections:
    print(section.attrib['id'])
    paragraphs.extend(section.findall("p"))
print(paragraphs)
for par in paragraphs: 
    print(par.text)