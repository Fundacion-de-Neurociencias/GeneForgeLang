# {{ cookiecutter.plugin_name }}

{{ cookiecutter.description }}

## Installation

```bash
pip install {{ cookiecutter.plugin_name }}
```

## Usage

```python
from {{ cookiecutter.module_name }} import {{ cookiecutter.module_name.split('_')[-1].title() }}Plugin

# Initialize the plugin
plugin = {{ cookiecutter.module_name.split('_')[-1].title() }}Plugin()

# Run the plugin
result = plugin.run(input_data, params={"param1": "value1"})
print(result)
```

## Configuration

The plugin accepts optional configuration parameters:

```python
config = {
    "setting1": "value1",
    "setting2": "value2"
}

plugin = {{ cookiecutter.module_name.split('_')[-1].title() }}Plugin(config=config)
```

## Development

### Setup

```bash
git clone <repository-url>
cd {{ cookiecutter.plugin_name }}
pip install -e ".[dev]"
```

### Testing

```bash
pytest
```

### Code Formatting

```bash
black {{ cookiecutter.module_name }}/
ruff check {{ cookiecutter.module_name }}/
```

## License

This plugin is part of the GeneForgeLang ecosystem.

## Author

{{ cookiecutter.author_name }} - {{ cookiecutter.author_email }}
