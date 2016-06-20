# reportgen 

[![Build Status](https://travis-ci.org/ClinSeq/reportgen.svg?branch=master)](https://travis-ci.org/ClinSeq/reportgen)

`reportgen` creates beautiful reports from clinseq data. 


[![Coverage Status](https://coveralls.io/repos/github/ClinSeq/reportgen/badge.svg?branch=master)](https://coveralls.io/github/ClinSeq/reportgen?branch=master)

## Setup

~~~bash
git clone https://bitbucket.org/twhitington/reportgen.git
pip install ./reportgen
~~~

## Run

~~~bash

# Example execution with some dummy input files:
cat << EOF > meta.json
{
    "personnummer": "19501010-1234",
    "blood_sample_id": 123456,
    "tumor_sample_id": 123456,
    "blood_sample_date": "2016-04-29",
    "tumor_sample_date": "2016-05-20",
    "doctor": "Dr Namn Namnsson",
    "doctor_address": "Onkologimottagningen\nStora Lasaretet\n123 45 Stadsby"
}
EOF

FIXME: THIS EXAMPLE IS WRONG; CONFORM WITH DEFINITION
cat << EOF > report.json
{
    "PI3K_pathway": "Mutation class A",
    "MSI_status": "MSS/MSI-L",
    "KRAS": ["Mutated", "G12D"],
    "BRAF": ["Not mutated", null],
    "NRAS": ["Not determined", null]
}
EOF

reportgen meta.json report.json
~~~

## BNF definition of metadata and genomic report JSON files:

# Metadata:
XXX

# Genomic report:
<genomicFeatures> ::= {[<featureNameAndValues>,]*} # NOTE: I mean a comma-separated list, zero or more elements
<featureNameAndValues> ::=  "msiReport" : <msiReportValues> |
                            "alasscaReport" : <alasscaReportValues> |
                            "simpleSomaticMutationsReport" : <simpleSomaticMutationsReportValues>
<msiReportValues> ::= {<msiStatus>}
<msiStatus> ::= "MSS/MSI-L" | "MSI-H" | <notDetermined>
<alasscaReportValues> ::= {<alasscaClass>}
<alasscaClass> ::= "A" | "B" | <noMutations>
<notDetermined> ::= "NotDetermined"
<notMutated> ::= "NotMutated"
<mutated> ::= "Mutated"
<simpleSomaticMutationsReportValues> ::= {<ENSEMBLgeneID> : <mutationInfo>}
<ENSEMBLgeneID> ::= "ENSG"[0-9]{11}
<mutationInfo> ::= [<notMutated> | <notDetermined> | <mutated>, <mutationSet>]
<mutationSet> ::= {[<mutation> : <mutationFlag>,]*} # NOTE: I mean a comma-separated list, zero or more elements
<mutationFlag> ::= # Not defined exactly yet. Some e.g.s: "KRAS_COMMON", "KRAS_UNCOMMON", "BRAF_COMMON"
<mutation> ::= [A-Z][0-9]+[A-Z] | [0-9]+

## Contact

* Tom Whitington
* Daniel Klevebring









































