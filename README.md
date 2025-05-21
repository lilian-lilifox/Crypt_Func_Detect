# Cryptographic Function Detector for Router Firmware

This project is the author’s undergraduate thesis work. The core code is adapted from two open-source repositories: [NSSL-SJTU/HermesSim](https://github.com/NSSL-SJTU/HermesSim) and [Cisco-Talos/binary_function_similarity](https://github.com/Cisco-Talos/binary_function_similarity). These were integrated and extended for the task of identifying and locating cryptographic functions in router firmware. This repository contains the corresponding automation scripts and tooling.

Additionally, two datasets were constructed:

- `Dataset-Finetuning`: for fine-tuning the similarity model.
- `Dataset-Crypt`: for the cryptographic function identification task.
  (_Put the binaries to be analyzed in the `Binaries/Dataset-Crypt/vul/` folder following the naming convention._)

## Project Structure

```
Binaries/         # Raw binary files
DBs/              # Preprocessed graph/data outputs
IDA_script/       # IDA Python scripts for extracting ACFG graphs
IDBs/             # IDA analysis database files
bin/              # External tools and dependencies
lifting/          # Scripts for lifting binary functions into Pcode based graphs
preprocess/       # Scripts for graph normalization and encodin
model/            # Neural network model and related experiments configures
postprocess       # scripts for testing pairs generation, fast evaluation and visualization
inputs/           # Inputs for the model (iscg, tscg, sog)
outputs/          # Outputs for the model (checkpoint files, inferred embeddings, log)
Dockerfile        # An OpenWrt 23.05-specific cross-compilation environment
```

> **Notice:** External tool [gsat-1.0.jar](https://github.com/sgfvamll/gsat/releases/tag/v1.0.0) is needed to be downloaded and place in `bin/`.
>
> _The author's intermediate and final experimental results are published in the **Releases** section._

## Setup Instructions

1. **Python Environment** (Python 3.10 required)

```bash
conda create -n cfd python=3.10
conda activate cfd
pip install -r requirements.txt \
    --extra-index-url https://download.pytorch.org/whl/cu116 \
    -f https://data.pyg.org/whl/torch-1.13.1+cu116.html
```

2. **IDA Pro Requirement**
   IDA Pro 9.1 for Linux is required.
   Please update the paths in `run_Finetuning.sh` and `run_Crypt.sh` accordingly.

## How to Use

1. **Prepare firmware binaries**
   Unpack IoT firmware images and place the target binaries under:

   ```
   Binaries/Dataset-Crypt/vul/
   ```

2. **(Optional - already provided)**
   Fine-tune the HermesSim model using:

   ```bash
   ./run_Finetuning.sh
   ./run_Finetuning2.sh
   ```

3. **Update config**
   In `outputs/Finetuned/config.json`, set:

   ```json
   "checkpoint_name": "checkpoint_*.pt"
   ```

   to the desired checkpoint (e.g., best-performing one).

4. **Run cryptographic function detection**

   ```bash
   ./run_Crypt.sh
   ./run_Crypt2.sh
   ```

5. **Outputs**

   - Fine-tuned checkpoints:
     `outputs/Finetuned/graph-ggnn-batch_pair-pcode_sog`
   - Detection results:
     `outputs/Crypt`

6. **(Optional)**
   To extract top-K most similar functions from output similarity CSVs:

   ```bash
   python postprocess/3.pp_results/top_k.py <*_sim.csv> <num_of_results>
   ```

## Q&A

**Q: I want to avoid matching very small functions. What can I do?**

**A:** Edit the filtering rule in `DBs/Dataset-Crypt/Dataset-Crypt_creation.py`, line 8:

```python
flowchart = flowchart[flowchart["bb_num"] >= 0]
```

Increase the threshold (e.g., to `>= 5`) to exclude short functions from matching.

**Q: How can I create my own `Dataset-Finetuning` samples?**

**A:** The source code includes a `Dockerfile` for building an OpenWrt 23.05-specific cross-compilation environment. You can use it to compile your own binaries for dataset generation:

```bash
docker build -t openwrt-crosscompile .
docker run -it --rm -v $(pwd)/src:/workspace openwrt-crosscompile
```

Inside the Docker container, place and build your source files under `/workspace`. The resulting binaries can be used to construct new samples for fine-tuning the model.
