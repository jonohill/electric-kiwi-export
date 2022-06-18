# Electric Kiwi Export

A script to export consumption data from Electric Kiwi.

Data is exported (roughly) in the [Electricity Authority EIEP13A](https://www.ea.govt.nz/assets/dms-assets/30/EIEP13A-HHR-and-NHH-combined-v1.4.pdf) format.

## Set up

This project uses [Poetry](https://python-poetry.org) to manage dependencies.

```
poetry install
```

You also need to initialise any git submodules:
```
git submodule update --init
```

## Usage

Set the environment variables `EK_USERNAME` and `EK_PASSWORD` to the username and password for your Electric Kiwi account.

Initialise the virtual environment with `poetry shell`, or prefix commands with `poetry run`.
Data is written to stdout, so you could for example save it to a file by suffixing with `>filename.csv`.

```
❯ python -m electric-kiwi-export --help
usage: electric-kiwi-export [-h] [--start START] [--end END]

options:
  -h, --help     show this help message and exit
  --start START  Start date
  --end END      End date
```

## Acknowledgements

The script uses [matthuisman's electrickiwi.api](https://github.com/matthuisman/electrickiwi.api), imported as a git submodule.
