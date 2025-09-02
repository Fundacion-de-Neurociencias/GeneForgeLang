# GFL Genesis Project

This is a comprehensive example project demonstrating advanced GeneForgeLang (GFL) capabilities in a real-world genomic workflow scenario.

## Project Overview

GFL Genesis showcases how to build a complete genomic engineering project using GFL, including custom plugins, schema definitions, and complex workflow orchestration.

## Directory Structure

```
gfl-genesis/
├── genesis.gfl                 # Main GFL workflow definition
├── main.py                     # Entry point for executing the workflow
├── requirements.txt            # Python dependencies
├── setup.py                    # Project setup script
├── Makefile                    # Build and execution commands
├── data/                       # Input data files
├── docs/                       # Project documentation
│   ├── project_plan.md         # Technical documentation
│   └── planning/               # Project planning documents
│       ├── GFL_GENESIS_PROJECT_PLAN.md
│       └── PHASE_3_INITIATIVES.md
├── gfl_genesis/                # Python package for project-specific code
├── plugins/                    # Custom GFL plugins
│   ├── gfl-crispr-evaluator/
│   ├── gfl-plugin-offtarget-scorer/
│   └── gfl-plugin-ontarget-scorer/
├── results/                    # Output results
├── schemas/                    # Custom schema definitions
└── tests/                      # Project tests
```

## Getting Started

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Install plugins:
   ```bash
   # Install each plugin
   cd plugins/gfl-crispr-evaluator
   pip install -e .
   
   cd ../gfl-plugin-offtarget-scorer
   pip install -e .
   
   cd ../gfl-plugin-ontarget-scorer
   pip install -e .
   ```

3. Run the workflow:
   ```bash
   python main.py
   ```

## Features Demonstrated

- Advanced GFL syntax and constructs
- Custom plugin development
- Schema registry usage
- Complex workflow orchestration
- Testing strategies for GFL projects

## Documentation

For detailed project documentation, see:
- [Project Plan](docs/project_plan.md)
- [Planning Documents](docs/planning/)