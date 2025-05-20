export IDA_PATH=/home/lilian/ida-pro-9.1/idat
export IDA32_PATH=/home/lilian/ida-pro-9.1/idat
cd IDA_scripts
python3 generate_idbs.py --dbft
cd IDA_flowchart
python3 cli_flowchart.py -i ../../IDBs/Dataset-Finetuning -o ../../DBs/Dataset-Finetuning/features/flowchart_Dataset-Finetuning.csv
cd ../../DBs/Dataset-Finetuning
python3 'Dataset-Finetuning creation.py'
cd ../../IDA_scripts/IDA_acfg_disasm
python3 cli_acfg_disasm.py -j ../../DBs/Dataset-Finetuning/features/training/selected_training_Dataset-Finetuning.json -o ../../DBs/Dataset-Finetuning/features/training/acfg_disasm_Dataset-Finetuning
python3 cli_acfg_disasm.py -j ../../DBs/Dataset-Finetuning/features/testing/selected_testing_Dataset-Finetuning.json -o ../../DBs/Dataset-Finetuning/features/testing/acfg_disasm_Dataset-Finetuning
python3 cli_acfg_disasm.py -j ../../DBs/Dataset-Finetuning/features/validation/selected_validation_Dataset-Finetuning.json -o ../../DBs/Dataset-Finetuning/features/validation/acfg_disasm_Dataset-Finetuning
cd ../IDA_acfg_features
python3 cli_acfg_features.py -j ../../DBs/Dataset-Finetuning/features/training/selected_training_Dataset-Finetuning.json -o ../../DBs/Dataset-Finetuning/features/training/acfg_features_Dataset-Finetuning
python3 cli_acfg_features.py -j ../../DBs/Dataset-Finetuning/features/testing/selected_testing_Dataset-Finetuning.json -o ../../DBs/Dataset-Finetuning/features/testing/acfg_features_Dataset-Finetuning
python3 cli_acfg_features.py -j ../../DBs/Dataset-Finetuning/features/validation/selected_validation_Dataset-Finetuning.json -o ../../DBs/Dataset-Finetuning/features/validation/acfg_features_Dataset-Finetuning
