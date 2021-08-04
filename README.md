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

## Opening a File with the Config

It may be desireable to open a file (i.e. given a URL) and apply the config at the same time. These URLs can be created programmatically.

1. Fetch [https://nsfsmartmakerspaces.github.io/physcomp-drawio-library/index.json](https://nsfsmartmakerspaces.github.io/physcomp-drawio-library/index.json). This file is updated just as `index.html` is updated when there is a new version of the diagram tool. This means that URLs to open files should be created on-the-fly or re-generated each time the drawing tool updates the diagrams.
2. There are currently two config modes in the drawing tool, you want to use `0_physcomp` to open the tool with the diagram config. The other resets the config.
3. Take the `url_base` and concatenate it with a location [URL open query string parameter](https://www.diagrams.net/doc/faq/supported-url-parameters) using a [location hash](https://www.diagrams.net/doc/faq/supported-location-hash-properties.html) (`open=prefix+ID`) and then the `url_hash`. For example:
   ```
   https://app.diagrams.net/?open=Uhttps%3A%2F%2Fnsfsmartmakerspaces.github.io%2Fphyscomp%2Fimages%2Fparts%2F4001_schematic1.svg#_CONFIG_7LzHtutIliX4LT3IVVWD...
   <------- url_base -------><----------------------------- URL open parameter with location hash -----------------------------><---------- url_hash ---------->
   ```
   In this example, the location parameter is:
   ```
   open=Uhttps%3A%2F%2Fnsfsmartmakerspaces.github.io%2Fphyscomp%2Fimages%2Fparts%2F4001_schematic1.svg
   ```
   The `U` signifies that it opens a URL, and the URL-encoded URL follows it. More info on the location hashes [here](https://www.diagrams.net/doc/faq/supported-location-hash-properties.html).
