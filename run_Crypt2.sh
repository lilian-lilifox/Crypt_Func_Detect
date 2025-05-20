mkdir -p DBs/Dataset-Crypt/cfg_summary/testing
python lifting/dataset_summary.py --cfg_summary DBs/Dataset-Crypt/cfg_summary/testing --dataset_info_csv DBs/Dataset-Crypt/testing_Dataset-Crypt.csv --cfgs_folder DBs/Dataset-Crypt/features/acfg_features_Dataset-Crypt/
python lifting/pcode_lifter.py --cfg_summary ./DBs/Dataset-Crypt/cfg_summary/testing/ --output_dir ./DBs/Dataset-Crypt/features/pcode_raw_testing --graph_type ALL --verbose 1 --nproc 80
python preprocess/preprocessing_pcode.py --freq-mode -f pkl -s Dataset-Crypt_testing -i DBs/Dataset-Crypt/features/pcode_raw_testing/ -o inputs/pcode_raw
python model/main.py --inputdir DBs --config ./model/configures/e04_crypt_test.json --dataset=Crypt
python postprocess/1.generate_testing/add_idx_for_pairs.py --pairs_csv=DBs/Dataset-Crypt/pairs/pairs_testing_Dataset-Crypt.csv --ds_info_csv=DBs/Dataset-Crypt/testing_Dataset-Crypt.csv
python postprocess/2.summarize_results/compute_sim_df_for_HermesSim.py --pair_csv_or_dir=DBs/Dataset-Crypt/pairs/pairs_testing_Dataset-Crypt_with_idx.csv --target_dir=outputs/Crypt --pkl_fp=outputs/experiments/hermes_sim/0/last/testing_Dataset-Crypt.pkl
