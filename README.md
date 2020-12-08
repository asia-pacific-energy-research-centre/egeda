# EGEDA Data Transformations

## Input data
Save the following files in `./data/`
- EGEDA_2018.xlsx
- order_2018.csv

## Final output
Two Excel files are saved in `./results/`
- EGEDA_2018_years.xlsx
- EGEDA_2018_items.xlsx

## To use
You can either run the notebook `EGEDA_2018` or the Python file `transform.py`.

## Set up
### Create the Conda environment

`conda env create --prefix ./egeda-env --file ./workflow/envs/egeda-env.yml`

`conda activate ./egeda-env`

### Update the Conda environment

`conda env update --prefix ./egeda-env --file ./workflow/envs/egeda-env.yml --prune`
