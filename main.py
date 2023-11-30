import array
import json
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom
import logging


class DbIntegrator:
    CONF_FILE = open("config.json")
    FORMAT = '%(asctime)s %(levelname)s : %(message)s'
    logging.basicConfig(format=FORMAT, level="INFO", filename='DbIntegrator.log')

    def __init__(self):
        self.config_vars = json.load(self.CONF_FILE)
        self.xml_path = self.config_vars['XMLPATH']
        self.output = self.config_vars['OUTPUT']
        self.output_kcp = self.config_vars['OUTPUTKCP']
        self.old_bases = self.config_vars['OLDBASES']
        self.bases = self.config_vars['BASES']
        self.categories = self.config_vars['CATEGORIES']

    def __index__(self):
        # CREATION DES REPERTOIRES D'ENTREE ET DE SORTIE DES XML
        if not os.path.exists(self.output):
            os.makedirs(self.output)
        if not os.path.exists(self.output_kcp):
            os.makedirs(self.output_kcp)
        if not os.path.exists(self.xml_path):
            os.makedirs(self.xml_path)

        # EXECUTION DU PROGRAMME
        for base in self.old_bases:
            self.run(base)

    def run(self, base):
        try:
            files = os.listdir(self.xml_path)
            # tree = ET.parse('files/Client.xml')
            for file in files:
                n = 0
                category_list_array = []
                string_list_array = []
                base_from_filename = file.split('.xml')[0].upper()
                if base_from_filename in base:
                    file_with_fullpath = self.xml_path + '/' + file
                    logging.info(f'Traitement du fichier {file_with_fullpath}')
                    if os.path.isfile(file_with_fullpath) and file_with_fullpath.endswith('.xml'):
                        tree = ET.parse(file_with_fullpath)
                        root = tree.getroot()
                        tagIndex = root.findall(".//Object/Tag/TagIndex")
                        document_root = root.findall(".//Object/document/page/uri")
                        document_array = [doc.text for doc in document_root]

                        # category = root.findall(".//Object/Tag/TagIndex/Category")

                        # value = [val.text for val in root.findall(".//Value/string")]
                        for tag in tagIndex:

                            category = tag.findall(".//Category")
                            value = tag.findall(".//Value/string")
                            category_array = []
                            string_array = []
                            for string in value:
                                string_array.append(string.text)
                            for child in category:
                                number = child.find(".//number")
                                child.attrib['Name'] = self.categories[base][child.attrib['Name']]
                                number.text = self.bases['AUTRES'].get(child.attrib['Name'])
                                category_array.append(child.attrib['Name'])
                            category_list_array.append(category_array)
                            string_list_array.append(string_array)

                        output_file = self.output + '/' + file
                        tree.write(output_file, encoding="UTF-8", xml_declaration=True)

                        f = open(output_file, 'r')
                        content = f.readlines()
                        f.close()
                        final_content = content[:1]
                        final_content.append(
                            '<!DOCTYPE Exchange PUBLIC "-//APROGED//DTD EIDE DTD 19990607 Vers 1.0//FR"  "docubase.dtd">\n')

                        final_content.extend(content[1:])
                        f = open(output_file, 'w')
                        f.writelines(final_content)
                        f.close()
                        self.create_xml(category_list_array, string_list_array, document_array, file)

                        logging.info('Traitement terminé')
                else:
                    continue
        except Exception as e:
            logging.exception(e)
            return False

    def create_xml(self, cat_array, string_array, doc_array, file):
        if cat_array:
            n = 0
            root = minidom.Document()
            xml = root.createElement('root')
            root.appendChild(xml)
            for i in range(0, len(cat_array)):

                documentChild = root.createElement('document')
                xml.appendChild(documentChild)
                nb = len(cat_array[i])
                field = root.createElement('field')
                field.setAttribute('name', 'Document Filename with Full Path')
                field.setAttribute('value', doc_array[i])
                documentChild.appendChild(field)
                for j in range(0, nb):
                    field = root.createElement('field')
                    field.setAttribute('name', cat_array[i][j])
                    field.setAttribute('value', string_array[i][j])
                    documentChild.appendChild(field)

            """if not os.path.exists("XML"):
                os.mkdir("XML")"""
            xml_str = root.toprettyxml(indent="\t")
            output_kcp_file = self.output_kcp+'/'+file
            if not os.path.exists(output_kcp_file):
                f = open(output_kcp_file, "w")
            f.write(xml_str)
            f.close()
        else:
            return None


DbIntegrator().__index__()
