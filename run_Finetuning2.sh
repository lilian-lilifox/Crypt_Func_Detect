mkdir -p DBs/Dataset-Finetuning/cfg_summary/training
mkdir -p DBs/Dataset-Finetuning/cfg_summary/testing
mkdir -p DBs/Dataset-Finetuning/cfg_summary/validation
python lifting/dataset_summary.py --cfg_summary DBs/Dataset-Finetuning/cfg_summary/training/ --dataset_info_csv DBs/Dataset-Finetuning/training_Dataset-Finetuning.csv --cfgs_folder DBs/Dataset-Finetuning/features/training/acfg_features_Dataset-Finetuning/
python lifting/dataset_summary.py --cfg_summary DBs/Dataset-Finetuning/cfg_summary/testing/ --dataset_info_csv DBs/Dataset-Finetuning/testing_Dataset-Finetuning.csv --cfgs_folder DBs/Dataset-Finetuning/features/testing/acfg_features_Dataset-Finetuning/
python lifting/dataset_summary.py --cfg_summary DBs/Dataset-Finetuning/cfg_summary/validation/ --dataset_info_csv DBs/Dataset-Finetuning/validation_Dataset-Finetuning.csv --cfgs_folder DBs/Dataset-Finetuning/features/validation/acfg_features_Dataset-Finetuning/
python lifting/pcode_lifter.py --cfg_summary ./DBs/Dataset-Finetuning/cfg_summary/training/ --output_dir ./DBs/Dataset-Finetuning/features/training/pcode_raw_Dataset-Finetuning-training --graph_type ALL --verbose 1 --nproc 80
python lifting/pcode_lifter.py --cfg_summary ./DBs/Dataset-Finetuning/cfg_summary/testing/ --output_dir ./DBs/Dataset-Finetuning/features/testing/pcode_raw_Dataset-Finetuning-testing --graph_type ALL --verbose 1 --nproc 80
python lifting/pcode_lifter.py --cfg_summary ./DBs/Dataset-Finetuning/cfg_summary/validation/ --output_dir ./DBs/Dataset-Finetuning/features/validation/pcode_raw_Dataset-Finetuning-validation --graph_type ALL --verbose 1 --nproc 80
python preprocess/preprocessing_pcode.py --training --freq-mode -f pkl -s Dataset-Finetuning_training -i DBs/Dataset-Finetuning/features/training/pcode_raw_Dataset-Finetuning-training/ -o inputs/fine_tuning
python preprocess/preprocessing_pcode.py --freq-mode -f pkl -s Dataset-Finetuning_testing -i DBs/Dataset-Finetuning/features/testing/pcode_raw_Dataset-Finetuning-testing/ -o inputs/fine_tuning
python preprocess/preprocessing_pcode.py --freq-mode -f pkl -s Dataset-Finetuning_validation -i DBs/Dataset-Finetuning/features/validation/pcode_raw_Dataset-Finetuning-validation/ -o inputs/fine_tuning
python preprocess/generate_validation_csv.py
python model/main.py --inputdir DBs --config ./model/configures/e06_fine_tuning.json --dataset=Finetuning
cp outputs/experiments/hermes_sim/0 outputs/Finetuned
