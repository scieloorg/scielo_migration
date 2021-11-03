# scielo_migration




# Models Builder 

```console
python scielo_migration/iid2json/model_builders.py generate_json_data_dictionary tests/models_builder_result/isis_records_definitions.csv tests/models_builder_result/data_dict.json
```

```console
python scielo_migration/iid2json/model_builders.py generate_module_py tests/models_builder_result/data_dict.json f H_Record tests/models_builder_result/h_record.py
```