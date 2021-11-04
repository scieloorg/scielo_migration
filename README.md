# scielo_migration




# Models Builder 

```console
python scielo_migration/iid2json/models_builder.py generate_json_data_dictionary tests/models_builder_result/isis_records_definitions.csv tests/models_builder_result/data_dict.json
```

```console
python scielo_migration/iid2json/models_builder.py generate_module_py tests/models_builder_result/data_dict.json h H_Record /path/output/h_record.py
```

```console
python scielo_migration/iid2json/models_builder.py generate_model /path/input/h_record.csv h HRecord /path/output/h_record.py
```