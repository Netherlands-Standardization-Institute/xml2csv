# -*- coding: utf-8 -*-
"""
This is an example of how to use the xml2csv module to create a data pipeline to process a directory with xml files.

@author: Robert Matousek
@email: rmatousek@kweri.nl
@created: 14/01/2022
"""

from xml2csv import IcsProcessor, CommRefProcessor, TbxProcessor, DateProcessor, RefListProcessor, StdRefProcessor, TitleProcessor
from csv import DictWriter
import os

# configuration
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT_DIR, 'data')

# input/output directories
IN_DIR = os.path.join(DATA_DIR, 'xml')
OUT_DIR = os.path.join(DATA_DIR, 'csv')

# processors and filepaths of CSV files
pipeline = [
     (IcsProcessor, os.path.join(OUT_DIR, 'ics.csv')),
     (CommRefProcessor, os.path.join(OUT_DIR, 'committees.csv')),
     (TbxProcessor, os.path.join(OUT_DIR, 'terms.csv')),
     (DateProcessor, os.path.join(OUT_DIR, 'dates.csv')),
     (RefListProcessor, os.path.join(OUT_DIR, 'references.csv')),
     (StdRefProcessor, os.path.join(OUT_DIR, 'standards.csv')),
     (TitleProcessor, os.path.join(OUT_DIR, 'titles.csv'))]

# Create CSV files and add headers
def config(pipeline):
    for i, t in enumerate(pipeline):
        writer = DictWriter(open(t[1], 'a'), delimiter=',', lineterminator='\n', fieldnames=t[0].fieldnames)
        writer.writeheader()

# Transform XML to CSV  
def process_file(file, uid, pipeline):
    
    for i, t in enumerate(pipeline):
        with open(t[1], 'a') as f:
            
            obj = t[0](open(file, 'r', encoding='utf-8'), 
                               DictWriter(f, delimiter=',', lineterminator='\n', fieldnames=t[0].fieldnames), 
                               job_id=uid)
            obj.process()
        
# Process XML files in a directory    
def process_dir(directory, pipeline):
    for filename in os.listdir(directory):
        f = os.path.join(directory, filename)
        if os.path.isfile(f):
            ext = os.path.splitext(f)[-1].lower()
            if ext == '.xml':
                uid = os.path.splitext(os.path.basename(f))[0]
                process_file(f, uid, pipeline)
                

if __name__ == "__main__":  
    config(pipeline)
    process_dir(IN_DIR, pipeline)