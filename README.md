
# Book Scraper

## Overview

This project fetches around 1000+ books data from an website, processes it, and stores it in Parquet.

## Setup

### Set Environment

```
python -m venv env
env/Scripts/activate
```

### Install Dependencies

```sh
pip install -r requirements.txt
```

### Run command

#### Scrapping:

```
python -m scrapping.src.main

```

#### Processing:

```
python -m processing.src.main
```

### Test Command

```
pytest scrapping/src/test.py
```

```
pytest processing/src/test.py
```
