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
                file_with_fullpath = self.xml_path + '/' + file
                logging.info(f'Traitement du fichier {file_with_fullpath}')
                if os.path.isfile(file_with_fullpath) and file_with_fullpath.endswith('.xml'):
                    tree = ET.parse(file_with_fullpath)
                    root = tree.getroot()
                    category = root.findall(".//Object/Tag/TagIndex/Category")

                    for child in category:
                        number = child.find(".//number")
                        child.attrib['Name'] = self.categories[base][child.attrib['Name']]
                        number.text = self.bases['AUTRES'].get(child.attrib['Name'])

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
        except Exception as e:
            logging.exception(e)
            return False


DbIntegrator().__index__()
