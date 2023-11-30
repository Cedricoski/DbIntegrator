import json
import os
import xml.etree.ElementTree as ET
import logging


class DbIntegrator:
    CONF_FILE = open("config.json")
    FORMAT = '%(asctime)s %(levelname)s : %(message)s'
    logging.basicConfig(format=FORMAT, level="INFO", filename='DbIntegrator.log')

    def __init__(self):
        self.config_vars = json.load(self.CONF_FILE)
        self.xml_path = self.config_vars['XMLPATH']
        self.output = self.config_vars['OUTPUT']
        self.old_bases = self.config_vars['OLDBASES']
        self.bases = self.config_vars['BASES']
        self.categories = self.config_vars['CATEGORIES']

    def __index__(self):
        # CREATION DES REPERTOIRES D'ENTREE ET DE SORTIE DES XML
        if not os.path.exists(self.output):
            os.makedirs(self.output)
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
                base_from_filename = file.split('.xml')[0].upper()
                if base_from_filename in base:
                    file_with_fullpath = self.xml_path + '/' + file
                    logging.info(f'Traitement du fichier {file_with_fullpath}')
                    if os.path.isfile(file_with_fullpath) and file_with_fullpath.endswith('.xml'):
                        tree = ET.parse(file_with_fullpath)
                        root = tree.getroot()
                        tagIndex = root.findall(".//Object/Tag/TagIndex")
                        # category = root.findall(".//Object/Tag/TagIndex/Category")

                        # value = [val.text for val in root.findall(".//Value/string")]
                        for tag in tagIndex:
                            category = tag.findall(".//Category")
                            value = tag.findall(".//Value/string")

                            for child in category:
                                number = child.find(".//number")
                                child.attrib['Name'] = self.categories[base][child.attrib['Name']]
                                number.text = self.bases['AUTRES'].get(child.attrib['Name'])
                            for val in value:
                                val.text = f"Test {str(n)}"
                            n = n + 1
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
                        logging.info('Traitement terminé')
                else:
                    continue
        except Exception as e:
            logging.exception(e)
            return False


DbIntegrator().__index__()
