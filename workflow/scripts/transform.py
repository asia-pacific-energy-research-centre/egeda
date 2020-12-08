import numpy as np
import pandas as pd
from collections import OrderedDict

# read raw data

print('Read in EGEDA data...\n')

RawEGEDA = pd.read_excel('../../data/EGEDA_2018.xlsx',
                         sheet_name = None,
                         na_values = ['x', 'X', '']) # I don't think there's any x's or X's in the EGEDA xlsx file, but leaving as is (shouldn't make a difference)

years = list(range(1980, 2019, 1))

df_list = []

economies = RawEGEDA.keys()

for economy in economies:
    _df_economy = RawEGEDA[economy]
    _df = pd.melt(_df_economy, 
                  id_vars = ['Product Code', 'Item Code'], 
                  value_vars = years, 
                  var_name = 'year',
                  value_name = 'value'
                )
    #_df = _df.pivot_table(index=['Year','Product Code'],columns='Item Code',values='Value')
    _df['economy'] = economy
    _df = _df.set_index(['economy', 'year'])
    df_list.append(_df)

df = pd.concat(df_list)

df.columns = [c.replace(' ', '_') for c in df.columns]
df.columns = map(str.lower, df.columns)

print('Remove multiple spaces from variables...\n')

# And remove multiple spaces from variables
df['product_code'] = df['product_code'].replace('\s+', ' ', regex = True)
df['item_code'] = df['item_code'].replace('\s+', ' ', regex = True)

df['fuel_code'] = df['product_code']
df['item_code_new'] = df['item_code']

# new fuel_code
df['fuel_code'] = df['fuel_code'].str.lower()
df['fuel_code'] = df['fuel_code'].str.replace(' ', '_').str.replace('.', '_').str.replace('/', '_').str.replace('(', '').str.replace(')', '').str.replace('-', '') \
.str.replace(',', '').str.replace('&', 'and').str.rstrip('_')

# item_code_new
df['item_code_new'] = df['item_code_new'].str.lower()
df['item_code_new'] = df['item_code_new'].str.replace(' ', '_').str.replace('.', '_').str.replace('/', '_').str.replace('(', '').str.replace(')', '').str.replace('-', '') \
.str.replace(',', '').str.replace('&', 'and').str.rstrip('_')

# Remove duplicate columns
df = df[['fuel_code', 'item_code_new', 'value']]

print('Add thermal coal and NGL aggregates...\n')

# Input thermal coal variable/subtotal

thermal_df = df[df['fuel_code'].isin(['1_2_other_bituminous_coal', '1_3_subbituminous_coal', '1_4_anthracite', '3_peat','4_peat_products'])]
assert thermal_df.value.isna().sum() == 0

df1 = thermal_df.groupby(['economy', 'year', 'item_code_new'])['value'].sum().reset_index().assign(fuel_code = '1_x_coal_thermal').set_index(['economy', 'year']).append(df)

# And also insert NGL aggregate variable

NGL_df = df1[df1['fuel_code'].isin(['6_2_natural_gas_liquids', '6_3_refinery_feedstocks', '6_4_additives_oxygenates', '6_5_other_hydrocarbons'])]

assert NGL_df.value.isna().sum() == 0

df2 = NGL_df.groupby(['economy', 'year', 'item_code_new'])['value'].sum().reset_index().assign(fuel_code = '3_x_ngls').set_index(['economy', 'year']).append(df1)

# Before changing ktoe to PJ, remove rows with data in Gwh

gwh_to_pj_df = df2[df2['item_code_new'] == '18__electricity_output_in_gwh']

gwh_to_pj_conversion = 0.0036

# electricity gwh data changed to pj
 
gwh_to_pj_df = gwh_to_pj_df.assign(pj = np.multiply(gwh_to_pj_df['value'], gwh_to_pj_conversion))  
gwh_to_pj_df['item_code_new'] = '18__electricity_output_in_gwh'

gwh_to_pj_df.columns = ['item_code_new', 'ktoe', 'fuel_code', 'pj']
gwh_to_pj_df = gwh_to_pj_df[['fuel_code', 'item_code_new', 'ktoe', 'pj']]

# Conversion to PJ

print('Convert to PJ...\n')

conversion_to_PJ = 1 # 41.868 PJ = 1 million tonnes of oil equivalent
# http://w.astro.berkeley.edu/~wright/fuel_energy.html

df_pj = df2[df2['item_code_new'] != '18__electricity_output_in_gwh']

df_pj = df_pj.assign(pj = np.multiply(df_pj['value'], conversion_to_PJ))
df_pj.columns = ['item_code_new', 'ktoe', 'fuel_code', 'pj']
df_pj = df_pj[['fuel_code', 'item_code_new', 'ktoe', 'pj']]

# Now append df_pj to gwh_pj_df (so all data is now in PJ)

df = df_pj.append(gwh_to_pj_df)

df_tidy = df.reset_index()

print('Reorder the table...\n')

ordered = pd.read_csv('../../data/order_2018.csv')

list(ordered['fuel_code'].unique())[:-1]

# This grabs the unique values of fuel_code and item_code_new in the order they appear in the original dataframe. It removes 'na' by calling '[:-1]' 

order1 = list(ordered['fuel_code'].unique())[:-1]
order2 = list(ordered['item_code_new'])

# Take order defined above and define each of the variables as categorical in that already established order (for the benefit of viewing data later)

df_tidy['fuel_code'] = pd.Categorical(df_tidy['fuel_code'], 
                                      categories = order1, 
                                      ordered = True)

df_tidy['item_code_new'] = pd.Categorical(df_tidy['item_code_new'],
                                          categories = order2,
                                          ordered = True)

df_tidy_sorted = df_tidy.sort_values(['fuel_code', 'item_code_new']).reset_index()

#df_tidy_sorted = df_tidy_sorted.drop(['index', 'ktoe'], axis = 1)
#df_tidy_sorted.to_csv("../../results/EGEDA_2018_tidy.csv", index = False)

print('Final pivot of the data...\n')

# Now, pivot the tidy dataset to provide it in wide format similar to RawEGEDA (so years are across the top)
df_years = df_tidy_sorted.pivot_table(index = ['economy', 'fuel_code', 'item_code_new'], columns = 'year', values = 'pj').reset_index(drop = False)

print('Write Excel file with years as columns...\n')

#df_years.to_csv("../../results/EGEDA_2018_years.csv", index = False)
df_years.to_excel("../../results/EGEDA_2018_years.xlsx", index = False)

# And now pivot so item codes are along the top
df_items = df_tidy_sorted
df_items['item_code_new'] = df_items['item_code_new'].astype(str)

df_items = df_items.pivot_table(index = ['economy', 'fuel_code', 'year'], columns = 'item_code_new', values = 'pj').reset_index()

# Reorder columns based on order2 defined above

NewOrder = ['economy', 'fuel_code', 'year']
NewOrder.extend(order2) 

df_items = df_items[NewOrder]

print('Write Excel file with items as columns...\n')

#df_items.to_csv("../../results/EGEDA_2018_items.csv", index = True)
df_items.to_excel("../../results/EGEDA_2018_items.xlsx", index = False)
