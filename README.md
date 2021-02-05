physcomp-drawio-library
=======================
A draw.io library for IDeATe physical computing

## Installation
1. You will need Python 3.6+ with Pip (included with Python in most cases)
2. Clone this repo or download the latest archive and extract it
3. (optional) Create a venv and activate it if you are able to
4. Run `python3 -m pip install -e .`
5. Run `python3 -m physcomp_drawio_generate` from this directory to run the tool

## Definitions

### Styles

These YAML files in `styles/` define the sizes and spacings of different parts. The filename of this YAML files corresponds to the `style:` field in a drawing YAML file. See the [example style](styles/example.yaml) for more information.

### Drawings

These YAML files in `drawings/` define each part. The first-level of a subdirectories separate the drawings into different component libraries. See the [main example drawing](drawings/examples/example.yaml) for all options.
