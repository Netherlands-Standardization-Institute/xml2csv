from csv import DictWriter
import csv
import uuid
import copy
import re
from xml2csv import Processor
import os
from bs4 import BeautifulSoup, Tag


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
        with open("additonal_info.csv", "w", encoding="utf-8") as added_info_file: 
            writer_added = csv.writer(added_info_file)
            writer_added.writerow(["Req_UUID","AdditionalInfo_Type", "AdditionalInfo_UUID", "StandardID", "SectionID", "ID", "AdditionalInfo_Body"])
            
            for file in os.listdir(self.input_folder):
                if not file.endswith(".xml"):
                    continue
                full_path = f"{self.input_folder}/{file}"
                print(full_path)
                self.convert_file(full_path, writer_added)
                    

    def convert_file(self, filename, extra_writer):

        processor = self.processor_cls(filename, self.writer)
        processor.process()
        converted_dict = [ 
                [
                    row["Req_UUID"],
                    row["AdditionalInfo_Type"], 
                    row["AdditionalInfo_UUID"], 
                    row["StandardID"], 
                    row["SectionID"], 
                    row["ID"], 
                    row["AdditionalInfo_Body"]
                ]
                for row in processor.extra_output
            ]
        extra_writer.writerows(converted_dict)


AdditionalInfoTypes = ["Standard", "Section",
                       "Table", "Figure"]  # TODO aanvullen


def extract_relevant_text(paragraph: Tag) -> str:
    copied_par = copy.copy(paragraph)
    inner_formulas = copied_par.find_all("inline-formula")
    for formula in inner_formulas:
        formula.decompose()
    text = copied_par.get_text().replace("\n", " ").strip()
    return re.sub(r" +", " ", text)


class RequirementsProcessor(Processor):
    fieldnames = ["Req_UUID", "Text", "Standard", "Section"]

    def __init__(self, input_file, writer, job_id=None):
        self.input_file = input_file
        self.extra_output = []
        self.referenced_stds = {}
        self.referenced_items = {}
        super().__init__(None, writer, job_id)

    def extract_standard(self, soup: BeautifulSoup):
        ref_undated = soup.find('std-ref', type='undated')
        ref_undated = ref_undated.get_text().upper() if ref_undated else None
        if ref_undated is not None:
            return ref_undated

        ref_dated = soup.find('std-ref', type='dated')
        ref_dated = ref_dated.get_text().upper() if ref_dated else None
        if ref_dated is not None:
            return ref_dated

        other_ref = soup.find('nat-meta').find('std-ref')
        no_duplicates = soup.find('nat-meta').find_all('std-ref')

        if other_ref is not None and no_duplicates[0] == other_ref and len(no_duplicates) == 1:
            return other_ref.get_text().upper()
        return None

    def converter(self, data):
        soup = BeautifulSoup(data, 'lxml')
        output = []
        standard = self.extract_standard(soup)
        if standard is None:
            print("Help!")
        sections = soup.find_all("sec")

        def build_output(text: str, section):
            id = uuid.uuid4()
            text = text.replace("\n", "  ")
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
            paragraphs = sec.find("p", recursive=False)
            paragraphs = []
            for p in paragraphs:
                try:
                    section_id = sec['id']
                except KeyError:
                    section_id = "-"
                extracted_text = extract_relevant_text(p)
                if len(extracted_text):
                    single_output = build_output(extracted_text, section_id)
                    # self.process_inner_text(
                    #     single_output["Req_UUID"], p, section_id, standard, soup)
                output.append(single_output)

        return output

    def process(self):
        with open(self.input_file, "r", encoding="utf-8") as f:
            self.reader = f
            super().process()
        


    def add_std_ref(self, uid, section_id, norm_id, reference: Tag):
        std_text = reference.find("std-ref").get_text(strip=True).upper()
        try:
            added_uid = self.referenced_stds[std_text]
        except KeyError:
            added_uid = uuid.uuid4()
            self.referenced_stds[std_text] = added_uid

        added_row = {
            "Req_UUID": uid,
            "AdditionalInfo_Type": "Standard",
            "AdditionalInfo_UUID": added_uid,
            "StandardID": norm_id,
            "SectionID": section_id,
            "ID": std_text,
            "AdditionalInfo_Body": "",
        }

        self.extra_output.append(added_row)

    def add_additional_info(self, uid, section_id, norm_id, reference: Tag, soup: BeautifulSoup):
        ID = reference.attrs["rid"]
        body = soup.find(attrs={"id": ID})
        try:
            added_uid = self.referenced_items[ID]
        except KeyError:
            added_uid = uuid.uuid4()
            self.referenced_items[ID] = added_uid
        type = reference.attrs["ref-type"]
        if type == "sec":
            added_row = {
                "Req_UUID": uid,
                "AdditionalInfo_Type": "Section",
                "AdditionalInfo_UUID": added_uid,
                "StandardID": norm_id,
                "SectionID": section_id,
                "ID": ID,
                "AdditionalInfo_Body": "",
            }
            self.extra_output.append(added_row)
            return

        added_row = {
            "Req_UUID": uid,
            "AdditionalInfo_Type": type,
            "AdditionalInfo_UUID": added_uid,
            "StandardID": norm_id,
            "SectionID": section_id,
            "ID": ID,
            "AdditionalInfo_Body": str(body),
        }
        self.extra_output.append(added_row)

    def process_inner_text(self, uid, paragraph_node, section_id, norm_id, soup):
        pass
        Standard_references = paragraph_node.find_all("std")
        for reference in Standard_references:
            self.add_std_ref(uid, section_id, norm_id, reference)

        Cross_references = paragraph_node.find_all("xref")
        for xref in Cross_references:
            print(xref)
            self.add_additional_info(uid, section_id, norm_id, xref, soup)
        # Type depends on the xref type

        ...


if __name__ == "__main__":
    print("START!")
    test = False 
    input_file = "data/xml/1739.xml"
    # Please change:
    input_folder = "C:/Users/Semmtech/Downloads/NENHackathon/xml"
    process_all = ProcessAll("output.csv", RequirementsProcessor, input_folder)
    if not test:
        process_all.convert_all()
    with open("test.csv", "w", encoding="utf-8") as f:
        writer = DictWriter(f, delimiter=',', lineterminator='\n',
                            fieldnames=["Req_UUID", "Text", "Standard", "Section"])
        writer.writeheader()
        print("END")
        proc = RequirementsProcessor(input_file, writer)
        proc.process()
        with open("test.txt", "w") as f2:
            f2.write(str(proc.extra_output))
