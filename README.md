# GeneForge: Applications and Pipelines for GeneForgeLang

## Overview

This repository hosts the **applications, pipelines, examples, and utility scripts** that extend and leverage the **GeneForgeLang (GFL) DSL** (Domain-Specific Language). It serves as the practical implementation layer, demonstrating how GFL can be used to build and execute complex biological workflows.

## Relationship with GeneForgeLang

GeneForge relies on the **core GeneForgeLang engine** (available in the [GeneForgeLang repository](https://github.com/Fundacion-de-Neurociencias/GeneForgeLang.git)) for parsing, evaluating, and reasoning about biological workflows. This repository focuses on the **applications and pipelines** that utilize this engine.

## Recent Updates

As of July 2025, the **GeneForgeLang (GFL) engine** has received significant improvements in the clarity of its error and warning messages, making workflow development more intuitive. This project (GeneForge applications) now includes **enhanced GFL parser and inference engine logic**, resulting in more robust handling of GFL workflows. For details on the DSL's roadmap, please refer to the [GeneForgeLang repository](https://github.com/Fundacion-de-Neurociencias/GeneForgeLang.git).

## Project Structure

The structure of this repository is organized as follows:

* **`applications/`**: Contains the core applications built with GFL.
* **`launcher/`**: Scripts to launch GFL-based workflows.
* **`datasets/`**: Test datasets for example pipelines.
* **`examples/`**: Example GFL pipelines and usage scenarios.
* **`README.md`**: This documentation file.
* **`QC checklist`**: Quality control checklist for applications and pipelines.
* **`src/tools/alphagenome/`**: Integration components for AlphaGenome tools.
* **`sync_with_existing_repo.sh`**: Utility script for repository synchronization.
* **`run_chatnt_cli.py`**: The new command-line interface for interacting with the conversational AI agent.
* **`integrations/chatnt_plugin.py`**: The core plugin for integrating the multimodal conversational AI agent (Gemini API).

---

## Environment Setup and Large Files

This project uses Python and manages dependencies and large files as follows:

### Virtual Environment (`venv`)

To ensure an isolated and reproducible development environment, we recommend using a virtual environment. The `venv/` directory, where dependencies are installed, is **excluded from Git version control** (`.gitignore`).

To set up your environment:

1.  Ensure you have Python (version 3.9 or higher recommended) and `pip` installed.
2.  Create the virtual environment (if you don't have one already):
    ```bash
    python3 -m venv venv
    ```
3.  Activate the environment:
    ```bash
    source venv/bin/activate
    ```
4.  Install project dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Models and Large Data (Managed Outside GitHub)

Due to their large size, fine-tuned Artificial Intelligence (AI) models and some large datasets **are not stored directly in this GitHub repository**. Instead, they are hosted on specialized platforms.

* **Fine-Tuned T5 Model (`fine_tuned_t5_model`):**
    This model, fundamental to GeneForge, is located on **Hugging Face Hub**. You can access it directly here:
    [https://huggingface.co/fneurociencias/GeneForge-T5-FineTuned](https://huggingface.co/fneurociencias/GeneForge-T5-FineTuned)

    To use the model in your local environment, you will need to download or load it directly from Hugging Face Hub using the appropriate libraries (e.g., `transformers`). A basic example for loading it in Python would be:

    ```python
    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

    model_name = "fneurociencias/GeneForge-T5-FineTuned"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    ```

* **Training Data (`data/nlp_training_data.json`):**
    This file is also large and is not in this repository. If required for training or replication, it is located at **[PENDING: indicate here if it was also uploaded to Hugging Face as a dataset, will be made accessible otherwise, or is currently just a placeholder]**.

### Specific External Dependencies (`external_libs/alphagenome`)

This project uses the [AlphaGenome by Google DeepMind](https://github.com/google-deepmind/alphagenome) library as a **Git submodule**. This means it is an independent Git repository included within this project.

**To clone the project including AlphaGenome:**
If you are cloning GeneForge for the first time, use the following command to ensure submodules are also downloaded:

```bash
git clone --recurse-submodules https://github.com/Fundacion-de-Neurociencias/GeneForge.git
```

**If you already cloned the project without submodules, or to initialize/update existing submodules:**
You can initialize and update them as follows:

```bash
git submodule update --init --recursive
```

This will download the contents of AlphaGenome into the `external_libs/alphagenome` folder.

---

## Installation

Here, you should detail the specific steps to install and set up GeneForge applications. This might include:

1.  Any additional system requirements (compilers, etc.).
2.  Instructions for configuring paths or environment variables if necessary.
3.  Any post-installation steps for Python dependencies.
    *(If the GFL engine requires a separate installation prior to this, reference it here).*

---

## Usage

Provide clear and concise examples of how to use GeneForge applications and pipelines. Include:

* How to run the launcher scripts (`launcher/`).
* Example commands to execute specific pipelines in `examples/`.
* Brief descriptions of expected results or how to interpret outputs.
    *(Consider linking to Jupyter notebooks if you have interactive demonstrations in the `examples/` folder).*

### New: Conversational AI Interface

GeneForge now features a command-line interface for interacting with a multimodal conversational AI agent (powered by Google Gemini). This allows users to perform biological tasks using natural language prompts.

To use the conversational AI interface:

1.  Ensure your `GEMINI_API_KEY` is set as an environment variable (e.g., in PowerShell: `$env:GEMINI_API_KEY="YOUR_API_KEY"`).
2.  Run the `run_chatnt_cli.py` script from the project root:
    ```bash
    python3 run_chatnt_cli.py <modality> <task> "<your natural language prompt>"
    ```
    * **`<modality>`**: The biological modality (e.g., `DNA`, `RNA`, `Protein`).
    * **`<task>`**: The specific task (e.g., `"promoter prediction"`, `"protein folding"`).
    * **`<your natural language prompt>`**: Your detailed instruction, which can include biological sequences (e.g., `"Analyze this DNA sequence: ATGCGT... and predict promoter regions."`).

    **Example:**
    ```bash
    python3 run_chatnt_cli.py DNA "promoter prediction" "Analyze this DNA sequence: ATGCGTACGTATATAAT... and predict promoter regions."
    ```

---

### Results Output

GeneForge now includes functionality to save execution results. You should find a new directory named `results/` in your project root. Inside this directory, a file named `stable_guides_output.json` will contain the results of guides that passed the stability filter.

---

## Contributions

Contributions are welcome! If you wish to contribute to GeneForge, please:

1.  Refer to the [contribution guidelines](link_to_CONTRIBUTING.md_if_exists) (highly recommended to create one).
2.  Follow the code and style guidelines.
3.  Open an issue to discuss any significant changes before submitting a pull request.

---

## License

This repository's software (GeneForge applications and pipelines) is **proprietary software** developed by Fundacion de Neurociencias. It is licensed under specific terms and conditions. For commercial use, distribution, or licensing inquiries, please contact: admin @fneurociencias.org.

Please note that GeneForge leverages the **GeneForgeLang (GFL) engine**, which is **open-source software**. The open-source license terms of GeneForgeLang apply only to the GFL engine itself, not to the proprietary GeneForge applications and pipelines contained in this repository.

All rights reserved by Fundacion de Neurociencias.

---

## Contact

For any questions or feedback, you can contact:
admin @fneurociencias.org