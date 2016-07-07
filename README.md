# netcdf-download-tester

*NOT CURRENTLY WORKING. HERE FOR ARCHIVAL PURPOSES*

## Installation

```bash
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

At the time, this was used with something like the following:

```bash
./download_requests.sh < request_list.txt
python test_downloads.py
```

The first step downloads a number of different data files from the pdp, then the second step compares the downloaded files to the on-disk source data.

This was used to generate the results see [here](https://github.com/pacificclimate/pydap.responses.netcdf/issues/2)