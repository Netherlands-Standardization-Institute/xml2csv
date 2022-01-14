# -*- coding: utf-8 -*-
"""
This module provides classes to extract data from XML documents that use the 
ISO Standards Tag Set (<a href="https://www.iso.org/schema/isosts/v1.1/doc/index.html">ISO STS</a>) or NISO Standards Tag Set (<a href="https://www.niso-sts.org/TagLibrary/niso-sts-TL-1-0-html/">NISO STS</a>).

@author <a href="https://www.linkedin.com/in/rmatousek/">Robert Matousek</a>

@email <a href="mailto:innovatielab@nen.nl">innovatielab@nen.nl</a>

@created Sun Dec 19 12:10:42 2021
"""
from abc import ABC, abstractmethod
from bs4 import BeautifulSoup

class Processor(ABC):
    """
    An abstract class to process XML using ISO/NISO STS.
    Args:
        reader (object): A reader that reads data from some input source.
        writer (object): A writer that writes data to some output source.
        
    Attributes:
        reader: A file object.
        writer: A writer object.
        job_id: A unique identifier
    
    """
    
    def __init__(self, reader, writer, job_id=None):     
        self.reader = reader
        self.writer = writer
        self.job_id = job_id

    def process(self):
        """
        Read and write data.
        """
        data = self.reader.read()
        data = self.converter(data)

        if data:    
            # add column with the job id
            #if self.job_id:    
            #    self.fieldnames.append('id')
            #    data = [dict(item, **{'id':self.job_id}) for item in data]
            
            self.writer.writerows(data)
    
    @abstractmethod
    def converter(self, data):
        """
        Convert the data. Overwrite this method to implement the conversion logic.
        """
        pass


class CommRefProcessor(Processor):
    """A class to extract the technical committee, subcommittee, and optionally working group responsible for the standard."""
    
    fieldnames = ['id', 'level', 'committee']
    """Column names.
    
    | Name      | Description              | Element                       |
    |-----------|--------------------------|-------------------------------|
    | id        | Job id                   |                               |    
    | level     | Hierarchical group level | [&lt;comm-ref-group&gt;](https://www.niso-sts.org/TagLibrary/niso-sts-TL-1-0-html/element/comm-ref-group.html) |    
    | committee | Committee code           | [&lt;comm-ref&gt;](https://www.iso.org/schema/isosts/v1.1/doc/n-v530.html) |    
    """
    
    def converter(self, data):
        """
        Parse XML and extract committee.

        Args:
            data (str): XML document
        
        Returns:
            list: A list with dictionaries.
        """
        soup = BeautifulSoup(data, 'lxml')
        data = []
                   
        # container elements for meta data
        containers = ['iso-meta', 'nat-meta', 'reg-meta', 'std-meta', 'std-doc-meta']
        
        for c in containers:
            meta = soup.find(c)
            if meta:
                groups = meta.find('comm-ref-group')
                if groups:
                    data = data + self.parse_groups(meta)                
                else:
                    committees = meta.find_all('comm-ref')
                    for i in committees:
                        data.append({'id': self.job_id, 'level': None, 'committee': i.getText()})
        return data
    
    def parse_groups(self, tree, level=1):
        """ 
        A recursive function to all find all subgroups in a committee including the hierarchical level.
        Note, this grouping element is part of NISO STS only.
        """
        tree = tree.find('comm-ref-group')
    
        if not tree:
            return [] 
        else:    
            refs = tree.find_all('comm-ref', recursive=False)        
            committees = []
            for i in refs:
                committees.append({'id': self.job_id, 'level': level, 'committee': i.getText()})
            return self.parse_groups(tree, level=level+1) + committees

    
class TbxProcessor(Processor):
    """A class to extract terminological data from a standard."""
    
    fieldnames = ['id', 'tds_id', 'label', 'note', 'lang', 'definition', 'source', 'term_id', 'term', 'pos', 'norm_auth']
    """
    Column names.
    
    | Name       | Description                       | Element             | Attribute         |
    |------------|-----------------------------------|---------------------|-------------------|
    | id         | Job id                            |                     |                   |
    | tds_id     | Terminology section               | [&lt;term-sec&gt;](https://www.iso.org/schema/isosts/v1.1/doc/n-qc70.html)                                        | [id](https://www.iso.org/schema/isosts/v1.1/doc/n-8ag0.html) |
    | label      | Label of element                  | [&lt;label&gt;](https://www.iso.org/schema/isosts/v1.1/doc/n-aia0.html)                                           |   |
    | note       | Additional information            | [&lt;tbx:note&gt;](https://www.iso.org/schema/isosts/v1.1/doc/tbx/ISO-TBX_xsd_Element_tbx_note.html)              |   |   [id](https://www.iso.org/schema/isosts/v1.1/doc/n-8ag0.html)
    | lang       | Language                          | [&lt;tbx:langSet&gt;](https://www.iso.org/schema/isosts/v1.1/doc/tbx/ISO-TBX_xsd_Element_tbx_langSet.html)        | [xml:lang](https://www.iso.org/schema/isosts/v1.1/doc/tbx/xml_xsd_Attribute_xml_lang.html) |
    | definition | Definition                        | [&lt;tbx:definition&gt;](https://www.iso.org/schema/isosts/v1.1/doc/tbx/ISO-TBX_xsd_Element_tbx_definition.html)  |   |
    | source     | Authoritive source                | [&lt;tbx:source&gt;](https://www.iso.org/schema/isosts/v1.1/doc/tbx/ISO-TBX_xsd_Element_tbx_source.html)          |   | 
    | term_id    | Term information group identifier | [&lt;tig&gt;](https://www.iso.org/schema/isosts/v1.1/doc/tbx/ISO-TBX_xsd_Element_tbx_tig.html)                    | [id](https://www.iso.org/schema/isosts/v1.1/doc/n-8ag0.html) |
    | term       | Term                              | [&lt;tbx:term&gt;](https://www.iso.org/schema/isosts/v1.1/doc/tbx/ISO-TBX_xsd_Element_tbx_term.html)              |   |
    | pos        | PartOfSpeech                      | [&lt;tbx:partOfSpeech&gt;](https://www.iso.org/schema/isosts/v1.1/doc/tbx/ISO-TBX_xsd_Element_tbx_partOfSpeech.html)                     |   |
    | norm_auth  | The status of the term            | [&lt;tbx:normativeAuthorization&gt;](https://www.iso.org/schema/isosts/v1.1/doc/tbx/ISO-TBX_xsd_Element_tbx_normativeAuthorization.html) |   |
    """

    def converter(self, data):
        """
        Parse XML and extract TBX records.

        Args:
            data (str): XML document
        
        Returns:
            list: A list with dictionaries.   
        """
        soup = BeautifulSoup(data, 'lxml')
 
        data = []
           
        # term sections    
        tds = soup.find_all('term-sec');
        
        for i in tds:
            
            tds_id = None # <term-sec id="">
            if (hasattr(i, 'id')):
                tds_id = i.get('id')
            
            label = i.find('label') # <term-sec><label>
            label = label.getText() if label else None
            
            # TBX records
            languages = i.find_all('tbx:langset')
            for j in languages:    
                lang = j.get('xml:lang')
                definition = j.find('tbx:definition')
                
                source = None            
                if definition:
                    source = definition.find('std-ref')
                    source = source.getText() if source else None
                
                if (hasattr(definition, 'text')):
                    definition = definition.text.replace('\n', ' ').strip()
                
                note = j.find('tbx:note')
                note = note.getText() if note else None
                
                tig = j.find('tbx:tig')
                if tig is not None:
                    term_id = None
                    if (hasattr(tig, 'id')):
                        term_id = tig.get('id') 
    
                    term = tig.find('tbx:term').text.replace('\n', ' ').strip()
                    
                    pos = tig.find('tbx:partofspeech')                
                    if (hasattr(pos, 'value')):
                        pos = pos.get('value')
    
                    norm_auth = tig.find('tbx:normativeauthorization')
                    if (hasattr(norm_auth, 'value')):
                        norm_auth = norm_auth.get('value')
                    
                    data.append({
                        'id': self.job_id,
                        'tds_id': tds_id, 
                        'label': label, 
                        'note': note, 
                        'lang': lang, 
                        'definition': definition, 
                        'source': source, 
                        'term_id': term_id, 
                        'term': term,
                        'pos': pos,
                        'norm_auth': norm_auth
                    })
        return data


class RefListProcessor(Processor):
    """A class to extract bibliographic references from a standard."""
    
    fieldnames = ['id', 'content_type', 'std_type', 'std_id', 'std_ref_type', 'std_ref', 'count']
    """
    Column names.
    
    | Name             | Description                              | Element             | Attribute         |
    |------------------|------------------------------------------|---------------------|-------------------|
    | id               | Job id                                   |                     |                   |
    | content_type     | Type of content                          | [&lt;ref&gt;](https://www.iso.org/schema/isosts/v1.1/doc/n-hqx0.html)     | [content-type](https://www.iso.org/schema/isosts/v1.1/doc/n-x3f0.html) |
    | std_type         | Type of standard, e.g. dated or undated  | [&lt;std&gt;](https://www.iso.org/schema/isosts/v1.1/doc/n-ui40.html)     | [type](https://www.iso.org/schema/isosts/v1.1/doc/n-tr60.html)         |    
    | std_id           | Identifier of cited standard             | [&lt;std&gt;](https://www.iso.org/schema/isosts/v1.1/doc/n-ui40.html)     | [std-id](https://www.iso.org/schema/isosts/v1.1/doc/n-7760.html)              |
    | std_ref_type     | Type of reference, e.g. dated or undated | [&lt;std-ref&gt;](https://www.iso.org/schema/isosts/v1.1/doc/n-5b40.html) |              |    
    | std_ref          | Standard reference                       | [&lt;std-ref&gt;](https://www.iso.org/schema/isosts/v1.1/doc/n-5b40.html) |              |    
    | count            | Number of occurrences in the document    | NA                  |                   |
    """
    
    def converter(self, data):
        """
        Parse XML and extract references.
        
        Args:
            data (str): XML document
        
        Returns:
            list: A list with dictionaries.  
        """
        soup = BeautifulSoup(data, 'lxml')

        data = []
            
        refs = set() # set of references

        # reference lists
        ref_list = soup.find_all('ref-list')
        
        for i in ref_list:
            ref = i.find_all('ref')

            for j in ref:
                content_type = j.get('content-type')

                std = j.find('std')
                if std:
                    if (hasattr(std, 'type')):
                        std_type = std.get('type')
                    if (hasattr(std, 'std-id')):
                        std_id = std.get('std-id')
                    
                    std_ref = std.find('std-ref')
                    if std_ref:
                        if (hasattr(std_ref, 'type')):
                            std_ref_type = std_ref.get('type')
                            
                        std_ref = std_ref.getText().strip()
                    
                        if std_ref not in refs:
                            count = 0
                            if (len(std_ref) > 2):
                                count = len(soup.find_all(text=lambda text: text and std_ref in text))
                                
                                data.append({
                                    'id': self.job_id,
                                    'content_type': content_type, 
                                    'std_type': std_type,
                                    'std_id': std_id,
                                    'std_ref_type': std_ref_type,
                                    'std_ref': std_ref,
                                    'count': count
                                })
                            refs.add(std_ref)
        return data


class StdRefProcessor(Processor):
    """A class to extract the metadata describing a standard."""
    
    fieldnames = ['id', 'ref_dated', 'ref_undated', 'doc_ref', 'rel_date', 'secretariat', 'sdo', 'proj_id', 'doc_lang', 'rel_version', 'urn', 'originator', 'doc_type', 'doc_nr', 'part_nr', 'edition', 'version', 'year', 'pub_date', 'content_language']
    """
    Column names.
    
    | Name             | Description                | Element                      |
    |------------------|----------------------------|------------------------------|
    | id               | Job id                     |                              |    
    | ref_dated        | Dated standard reference   | [&lt;std-ref&gt;](https://www.iso.org/schema/isosts/v1.1/doc/n-5b40.html)          |
    | ref_undated      | Undated standard reference | [&lt;std-ref&gt;](https://www.iso.org/schema/isosts/v1.1/doc/n-5b40.html)          |
    | doc_ref          | Document reference         | [&lt;doc-ref&gt;](https://www.iso.org/schema/isosts/v1.1/doc/n-g7v0.html)          |
    | secretariat      | Secretariat                | [&lt;secretariat&gt;](https://www.iso.org/schema/isosts/v1.1/doc/n-9a40.html)      |
    | sdo              | Standards Development Organization | [&lt;sdo&gt;](https://www.iso.org/schema/isosts/v1.1/doc/n-dzv0.html)      |
    | proj_id          | Project identifier         | [&lt;proj-id&gt;](https://www.iso.org/schema/isosts/v1.1/doc/n-iix0.html)          |
    | doc_lang         | Document language          | [&lt;doc-lang&gt;](https://www.iso.org/schema/isosts/v1.1/doc/n-upa0.html)         |
    | rel_version      | Release version            | [&lt;release-version&gt;](https://www.iso.org/schema/isosts/v1.1/doc/n-7ev0.html)  |
    | urn              | Unique Resource Name       | [&lt;urn&gt;](https://www.iso.org/schema/isosts/v1.1/doc/n-g3e0.html)              |
    | originator       | Originator of the document | [&lt;originator&gt;](https://www.iso.org/schema/isosts/v1.1/doc/n-kbw0.html)       |
    | doc_type         | Document type              | [&lt;doc-type&gt;](https://www.iso.org/schema/isosts/v1.1/doc/n-6g50.html)         |
    | doc_nr           | Document number            | [&lt;doc-number&gt;](https://www.iso.org/schema/isosts/v1.1/doc/n-qe50.html)       |
    | part_nr          | Part number                | [&lt;part-number&gt;](https://www.iso.org/schema/isosts/v1.1/doc/n-gxx0.html)      |
    | edition          | Edition number             | [&lt;edition&gt;](https://www.iso.org/schema/isosts/v1.1/doc/n-r650.html)          | 
    | version          | Type of event              | [&lt;version&gt;](https://www.iso.org/schema/isosts/v1.1/doc/n-3xe0.html)          |
    | year             | Year                       | [&lt;year&gt;](https://www.iso.org/schema/isosts/v1.1/doc/n-k7e0.html)             |
    | pub_date         | Publication date           | [&lt;pub-date&gt;](https://www.iso.org/schema/isosts/v1.1/doc/n-syx0.html)         |
    | rel_date         | Release date               | [&lt;release-date&gt;](https://www.iso.org/schema/isosts/v1.1/doc/n-g7v0.html)     |
    | content_language | Content language           | [&lt;content-language&gt;](https://www.iso.org/schema/isosts/v1.1/doc/n-vs30.html) |
    """
    
    def converter(self, data):
        """
        Parse XML and extract metadata.

        Args:
            data (str): XML document
        
        Returns:
            list: A list with dictionaries.
        """
        soup = BeautifulSoup(data, 'lxml')

        data = []

        content_language = soup.find('content-language')
        content_language = content_language.getText() if content_language else None

        ref_dated = soup.find('std-ref', type='dated')
        ref_dated = ref_dated.getText().upper() if ref_dated else None
        
        ref_undated = soup.find('std-ref', type='undated')
        ref_undated = ref_undated.getText().upper() if ref_undated else None
            
        doc_ref = soup.find('doc-ref')
        doc_ref = doc_ref.getText() if doc_ref else None
        
        pub_date = soup.find('pub-date')
        pub_date = pub_date.getText() if pub_date else None
        
        rel_date = soup.find('release-date')
        rel_date = rel_date.getText() if rel_date else None
        
        secretariat = soup.find('secretariat')
        secretariat = secretariat.getText() if secretariat else None

        ### Standard Identification Block
        sib = soup.find('std-ident')        
        
        originator = sib.find('originator')
        originator = originator.getText() if originator else None
    
        doc_type = sib.find('doc-type')
        doc_type = doc_type.getText() if doc_type else None
    
        doc_nr = sib.find('doc-number')
        doc_nr = doc_nr.getText() if doc_nr else None
    
        part_nr = sib.find('part-number')
        part_nr = part_nr.getText() if part_nr else None
    
        edition = sib.find('edition')
        edition = edition.getText() if edition else None
    
        version = sib.find('version')
        version = version.getText() if version else None
    
        year = sib.find('year')
        year = year.getText() if year else None

        ### Document Identification Block
        sdo = proj_id = doc_lang = rel_version = urn = None
        
        dib = soup.find('doc-ident')
        
        if dib:        
            sdo = dib.find('sdo')
            sdo = sdo.getText() if sdo else None
        
            proj_id = dib.find('proj-id')
            proj_id = proj_id.getText() if proj_id else None
        
            doc_lang = dib.find('language')
            doc_lang = doc_lang.getText() if doc_lang else None
        
            rel_version = dib.find('release-version')
            rel_version = rel_version.getText() if rel_version else None
        
            urn = dib.find('urn')
            urn = urn.getText() if urn else None
        
        data.append({
            'id': self.job_id,
            'ref_dated': ref_dated,
            'ref_undated': ref_undated,
            'doc_ref': doc_ref,
            'rel_date': rel_date,
            'secretariat': secretariat,
            'sdo': sdo,
            'proj_id': proj_id,
            'doc_lang': doc_lang,
            'rel_version': rel_version,
            'urn': urn,
            'originator': originator,
            'doc_type': doc_type,
            'doc_nr': doc_nr, 
            'part_nr': part_nr, 
            'edition': edition, 
            'version': version, 
            'year': year, 
            'pub_date': pub_date, 
            'content_language': content_language
        })
        return data


class DateProcessor(Processor):
    """A classs to extract dates from a standard."""
    
    fieldnames = ['id', 'date_type', 'date_val']
    """
    Column names.

    | Name      | Description         | Element             | Attribute         |
    |-----------|---------------------|---------------------|-------------------|
    | id        | Job id              |                     |                   |    
    | date_type | Type of event       | [&lt;meta-date&gt;](https://www.iso.org/schema/isosts/v1.1/doc/n-isu0.html) | [type](https://www.iso.org/schema/isosts/v1.1/doc/n-tr60.html) |
    | date_val  | Date of event       | [&lt;meta-date&gt;](https://www.iso.org/schema/isosts/v1.1/doc/n-isu0.html) |   |
    """
    
    def converter(self, data):
        """
        Parse XML and extract metadata.

        Args:
            data (str): XML document
        
        Returns:
            list: A list with dictionaries.
        """
        soup = BeautifulSoup(data, 'lxml')

        data = []
        
        # publication date
        pub_date = soup.find('pub-date')
        pub_date = pub_date.getText() if pub_date else None
        data.append({'id': self.job_id, 'date_type': 'publication', 'date_val': pub_date})

        # release date
        rel_date = soup.find('release-date')
        rel_date = rel_date.getText() if rel_date else None
        data.append({'id': self.job_id, 'date_type': 'release', 'date_val': rel_date})
        
        # meta dates
        for i in soup.find_all('meta-date'):
            date_type = None # type
            if (hasattr(i, 'type')):
                date_type = i.get('type').upper()
            date_val = i.getText() # date
            
            data.append({
                'id': self.job_id,
                'date_type': date_type, 
                'date_val': date_val
            })
        return data


class IcsProcessor(Processor):
    """
    A class to extract ICS classifications from a standard.
    
    @see [International Classification for Standards (ICS)](http://35.157.143.22/skosmos/ics/nl/)
    """   
    
    fieldnames = ['id', 'ics']
    """
    Column names.
    
    | Name      | Description         | Element                       |
    |-----------|---------------------|-------------------------------|
    | id        | Job id              |                               |   
    | ics       | ICS code            | [&lt;ics&gt;](https://www.iso.org/schema/isosts/v1.1/doc/n-bz80.html)     |
    """    
    
    def converter(self, data):
        """
        Parse XML and extract ICS classifications.
        
        Args:
            data (str): XML document
        
        Returns:
            list: A list with dictionaries.
        """
        soup = BeautifulSoup(data, 'lxml') # replace <break> tag by space character
        
        data = []
            
        # container elements for meta data
        containers = ['iso-meta', 'nat-meta', 'reg-meta', 'std-meta']
        
        for c in containers:
            meta = soup.find(c)
            
            if meta is not None:
                for i in meta.find_all('ics'):
                    ics = i.getText() if i else None
                    
                    if ics is not None:
                        data.append({'id': self.job_id, 'ics': ics})                   
        return data


class TitleProcessor(Processor):
    """A class to extract the titles of a standard."""
    
    fieldnames = ['id', 'lang', 'intro', 'main', 'compl', 'full']
    """
    Column names.
    
    | Name             | Description                  | Element             | Attribute         |
    |------------------|------------------------------|---------------------|-------------------|
    | id               | Job id                       |                     |                   |
    | lang             | Language                     | &lt;title-wrap&gt;  | [xml:lang](https://www.iso.org/schema/isosts/v1.1/doc/n-cvd0.html) | |
    | intro            | Introductory title element   | [&lt;intro&gt;](https://www.iso.org/schema/isosts/v1.1/doc/n-tua0.html)         | | |
    | main             | Main title element           | [&lt;main&gt;](https://www.iso.org/schema/isosts/v1.1/doc/n-pau0.html)                   | | |
    | compl            | Complementary title elemnent | [&lt;compl&gt;](https://www.iso.org/schema/isosts/v1.1/doc/n-2830.html)         | | |
    | full             | Full title                   | [&lt;full&gt;](https://www.iso.org/schema/isosts/v1.1/doc/n-nt80.html)    |
    """
    
    def converter(self, data):
        """
        Parse XML and extract titles.
        
        Args:
            data (str): XML document
        
        Returns:
            list: A list with dictionaries.  
        """
        soup = BeautifulSoup(data, 'lxml')

        data = []
    
        for i in soup.find_all('title-wrap'):
            lang = None
            if (hasattr(i, 'xml:lang')):
                lang = i.get('xml:lang')
            
            intro = i.find('intro')
            intro = intro.getText() if intro else None
            
            main = i.find('main').getText()
            
            compl = i.find('compl')
            compl = compl.getText() if compl else None
            
            full = i.find('full')
            full = full.getText() if full else None
            
            data.append({
                'id': self.job_id,
                'lang': lang,
                'intro': intro,
                'main': main,
                'compl': compl,
                'full': full
            })
        return data


class SectionProcessor(Processor):
    """A class to extract the sections in a standard."""
    
    fieldnames = ['id', 'section_id', 'section_type', 'section']

    """
    Column names.
    
    | Name             | Description         | Element             | Attribute         |
    |------------------|---------------------|---------------------|-------------------|
    | id               | Job id              |                     |                   |    
    | section_id       | Section identifier  |                     |                   |
    | section_type     | Section type        |                     |                   |
    | section          | Section             |                     |                   |
    """
    
    def converter(self, data):
        """
        Parse XML and extract sections.
        
        Args:
            data (str): XML document
        
        Returns:
            list: A list with dictionaries.  
        """
        soup = BeautifulSoup(data, 'lxml')

        data = []
    
        for i in soup.find_all('sec'):
            if (hasattr(i, 'id')):
                si = i.get('id')
            else:
                si = None
            if (hasattr(i, 'sec-type')):
                st = i.get('sec-type')
            else:
                st = None
            section = i.getText()
            data.append({
                'id': self.job_id,
                'section_id': si, 
                'section_type': st, 
                'section': section.encode("utf-8")
            })
        return data


class MathMLProcessor(Processor):
    """A class to extract MathML."""
    
    fieldnames = ['mathml']
    """
    Column names.
    
    | Name             | Description      | Element             |
    |------------------|------------------|---------------------|
    | id               | Job id           |                     |
    | math             | MathML           | [&lt;mml:math&gt;](https://www.iso.org/schema/isosts/v1.1/doc/n-ybu0.html) |
    """
    
    def converter(self, data):
        """
        Parse XML and extract titles.
        
        Args:
            data (str): XML document
        
        Returns:
            list: A list with dictionaries.  
        """
        soup = BeautifulSoup(data, 'lxml')

        data = []
    
        for i in soup.find_all('mml:math'):
            data.append({
                'id': self.job_id,
                'math': i.encode('utf-8')
            })
        return data