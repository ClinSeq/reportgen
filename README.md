# reportgen

`reportgen` creates beautiful reports from clinseq data. 

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

## Contact

* Tom Whitington
* Daniel Klevebring