import codecs
from csv import DictWriter
import unicodedata
import uuid

from numpy import full

from xml2csv import Processor
import os
from bs4 import BeautifulSoup


class ProcessAll():
    def __init__(self, output_file, Processor, input_folder) -> None:
        f = open(output_file, "w", encoding="utf-8")
        writer = DictWriter(f, delimiter=',', lineterminator='\n',
                            fieldnames=Processor.fieldnames)
        writer.writeheader()
        self.writer = writer
        self.input_folder = input_folder
        self.processor_cls = Processor

    def convert_all(self):
        for file in os.listdir(self.input_folder):
            if not file.endswith(".xml"):
                continue
            full_path = f"{self.input_folder}/{file}"
            print(full_path)
            self.convert_file(full_path)

    def convert_file(self, filename):
       
        processor = self.processor_cls(filename, self.writer)
        processor.process()


class RequirementsProcessor(Processor):
    fieldnames = ["Req_UUID", "Text", "Standard", "Section"]

    def __init__(self, input_file, writer, job_id=None):
        self.input_file = input_file
        super().__init__(None, writer, job_id)

    def extract_standard(self, soup):
        ref_undated = soup.find('std-ref', type='undated')
        ref_undated = ref_undated.get_text().upper() if ref_undated else None
        if ref_undated is not None:
            return ref_undated

        ref_dated = soup.find('std-ref', type='dated')
        ref_dated = ref_dated.get_text().upper() if ref_dated else None
        return ref_dated

    def converter(self, data):
        soup = BeautifulSoup(data, 'lxml')
        output = []
        standard = self.extract_standard(soup)
        sections = soup.find_all("sec")

        def build_output(text, section):
            id = uuid.uuid4()
            return {"Req_UUID": id, "Text": text, "Standard": standard, "Section": section}

        def filter_sections(section):
            try:
                sec_type = section['sec-type']
                if sec_type == "scope" or sec_type == "terms":
                    return False
            except KeyError:
                pass
            return True
        sections = [sec for sec in sections if filter_sections(sec)]

        for sec in sections:
            paragraphs = sec.find_all("p")
            for p in paragraphs:
                try:
                    section_id =  sec['id']
                except KeyError: 
                    section_id = "-"
                single_output = build_output(p.get_text(), section_id)
                output.append(single_output)
        return output

    def process(self):
        with open(self.input_file, "r", encoding="utf-8") as f:
            self.reader = f
            return super().process()
    def link_potential_extras(self, uid, requirement_node, section_id, norm_id): 
        pass 
    



if __name__ == "__main__":
    print("START!")
    input_file = "data/xml/663.xml"
    # Please change: 
    input_folder = "C:/Users/Semmtech/Downloads/NENHackathon/xml"
    process_all = ProcessAll("output.csv", RequirementsProcessor, input_folder)
    process_all.convert_all()
    with open("test.csv", "w", encoding="utf-8") as f:
        writer = DictWriter(f, delimiter=',', lineterminator='\n',
                            fieldnames=["Req_UUID", "Text", "Standard", "Section"])
        writer.writeheader()
        print("END")
        proc = RequirementsProcessor(input_file, writer)
        proc.process()
