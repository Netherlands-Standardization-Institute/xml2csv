# Design notes 

## Requirements 

### Extraction from XML 
All `<P>` tags contained in `<body><sec>`, with the exception of the following: 
- [x] `<P>` contained in a section with type `scope` or `terms`
- [ ] `<P>` contained in a section with id `sec_forword`
- [ ] ... ? 
### CSV format 
The format of the CSV output file is the following: 

    Req_UUID,Text,Standard,Section

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

    Req_UUID,AdditionInfo_Type, AdditionalInfo_UUID, StandardID, SectionID, ID, AdditionalInfo_Body.  

The additonalInfo UUID is empty for references to norms. 