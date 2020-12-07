# EGEDA Data Transformations
xxx

## Using Conda

### Creating the Conda environment

`conda env create --prefix ./egeda-env --file ./workflow/envs/egeda-env.yml`

`conda activate ./ose-env`

`pip install -r ./workflow/envs/requirements.txt`



### Updating the Conda environment

If you add (remove) dependencies to (from) the `environment.yml` file after the environment has 
already been created, then you can update the environment with the following command.

`conda env update --prefix ./egeda-env --file ./workflow/egeda-env.yml --prune`
