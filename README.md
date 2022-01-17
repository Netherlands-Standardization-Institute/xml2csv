# xml2csv
xml2csv is a Python module to transform standards from semi-structured to structured data.
It provides a set of classes to parse XML that uses the [ISO Standard Tag Set](https://www.iso.org/schema/isosts/v1.1/doc/index.html) (ISO STS) and/or [NISO Standard Tag Suite](https://www.niso-sts.org/) (NISO STS). The results are written to CSV. 

The [API documentation](http://35.157.143.22/docs/xml2csv.html) and additional information are available via [data.nen.nl](https://data.nen.nl).

## Description
Parses standards as XML and outputs data as CSV. The output includes:

- committees
- ICS codes
- dates, e.g. review or withdrawal
- references
- meta data
- terms and definitions
- titles, e.g. NL and EN
- sections
- equations

## How it works
1. Create an instance of a Processor and call the process method. 
2. Pass a reader oject and writer object as parameters to the constructor of the class.

```
from xml2csv import IcsProcessor
from csv import DictWriter

reader = open('input.xml', 'r', encoding='utf-8')
writer = DictWriter(open('output.csv', 'a'), delimiter=',', lineterminator='\n', fieldnames=IcsProcessor.fieldnames)

p = IcsProcessor(reader, writer)
p.process()
```

To implement your own parser: 
1. Create a subclass of the Processor class
2. Overwrite the converter method

## Installation 
How to install the project locally:
1. Clone the repository
2. Copy the XML documents to */data/xml* directory. 
 
Note the */data/xml* directory contains a sample document (NISO-STS-Standard-1-0.XML)

## Usage
2. Run *main.py* which defines a pipeline (list of processors)
3. The output is written to the */data/csv* directory (set of CSV files)

## License
Exclusive copyright:  GNU GPLv3
