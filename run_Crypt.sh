export IDA_PATH=/home/lilian/ida-pro-9.1/idat
export IDA32_PATH=/home/lilian/ida-pro-9.1/idat
cd IDA_scripts
python3 generate_idbs.py --dbcrypt
cd IDA_flowchart
python3 cli_flowchart.py -i ../../IDBs/Dataset-Crypt -o ../../DBs/Dataset-Crypt/features/flowchart_Dataset-Crypt.csv
cd ../../DBs/Dataset-Crypt
python3 Dataset-Crypt_creation.py
cd ../../IDA_scripts/IDA_acfg_disasm
python3 cli_acfg_disasm.py -j ../../DBs/Dataset-Crypt/features/selected_Dataset-Crypt.json -o ../../DBs/Dataset-Crypt/features/acfg_disasm_Dataset-Crypt
cd ../IDA_acfg_features
python3 cli_acfg_features.py -j ../../DBs/Dataset-Crypt/features/selected_Dataset-Crypt.json -o ../../DBs/Dataset-Crypt/features/acfg_features_Dataset-Crypt
