# Design notes 

## Requirements 

### Extraction from XML 
All `<P>` tags contained in `<body><sec>`, with the exception of the following: 
- [x] `<P>` contained in a section with type `scope` or `terms`
- [ ] `<P>` contained in a section with id `sec_forword`
- [ ] ... ? 
### CSV format 
The columns of the CSV format are the following: 

    Req_UUID,Text,Standard,Section
The CSV is UTF-8 encoded. 
The Req_UUID is unique for every requirement. It is also new for every iteration of the script. It is however used  to link requirements to additional information sets. (See the next section)

## Link Requirements with Additional Information such as Tables, etc. 

### Extraction from XML 
The following information elements are extracted: 
- [ ] References to other Norms. 
- [ ] References to tables/numerated lists/unnumerated lists with a ID link.
- [ ] tables/numerated lists/unnumerated in the same section as a paragraph without any ID link pointing to it. 
- [ ] ... ? 

### CSV Format
The format of the CSV output file is the following: 

    Req_UUID,AdditionalInfo_Type, AdditionalInfo_UUID, StandardID, SectionID, ID, AdditionalInfo_Body.  
References to norms only have the Req_UUID, AdditionalInfo_Type and StandardID filled in. The CSV is encoded in UTF-8. The Req_UUID is the same as the UUID used in the first iteration, if and only if both CSV files are created in the same iteration. 
