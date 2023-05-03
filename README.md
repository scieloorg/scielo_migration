# scielo_migration

## Instalação

Após clonar o projeto e entrar na pasta, digite:

```
# Crie uma virtualenv
python -m venv .venv

# Ative
source .venv/bin/activate

# Instale os pacotes
pip install -r requirements.txt
```

# Models Builder

## CSV input format
```
record,tag,subfield,subfield_name,multi_val,composite,field_name,name,description
Issue,31,,,,,volume,volume,Volume
Issue,32,,,,,number,number,Number
Issue,43,,,,,_start_end_months, start end months, Start End Months
Issue,,,,,,start_month,start month,Start Month
Issue,,,,,,end_month,end month,End Month
Issue,131,,,,,supplement_volume,supplement volume,Supplement Volume
Issue,132,,,,,supplement_number,supplement number,Supplement Number
Issue,,,,,,is_ahead_of_print,is ahead of print,Is Ahead Of Print

```


## Commands

Create a JSON version of `tests/fixtures/models_builder/issue_record.csv` (`/path/output/issue.json`)

```console
python scielo_classic_website/cli/models_builder.py generate_json_data_dictionary tests/fixtures/models_builder/issue_record.csv /path/output/issue.json
```

Create the python modules `/path/output/base_issue.py` and `/path/output/issue.py` given a CSV file (`issue_record.csv`)

```console
python scielo_classic_website/cli/models_builder.py generate_model tests/fixtures/models_builder/issue_record.csv Issue Issue /path/output/issue.py
```