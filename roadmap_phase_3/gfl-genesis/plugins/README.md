# GFL Genesis Plugins

This directory contains the plugins developed for the GFL Genesis project:

1. `gfl-plugin-ontarget-scorer` - Plugin to predict on-target cutting efficiency
2. `gfl-plugin-offtarget-scorer` - Plugin to identify and score potential off-target sites
3. `gfl-crispr-evaluator` - Orchestrator plugin that calls the other two

## Plugin Development Guide

Each plugin should follow the GFL plugin development guidelines and implement the appropriate interface:

- GeneratorPlugin for design blocks
- OptimizerPlugin for optimize blocks
- AnalyzerPlugin for analyze blocks

## Installation

To install these plugins, follow the standard GFL plugin installation process:

```bash
pip install -e ./gfl-plugin-ontarget-scorer
pip install -e ./gfl-plugin-offtarget-scorer
pip install -e ./gfl-crispr-evaluator
```