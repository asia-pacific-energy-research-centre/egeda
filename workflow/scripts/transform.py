import numpy as np
import pandas as pd
from collections import OrderedDict

# read raw data

RawEGEDA = pd.read_excel('../../data/00APEC_EGEDA_20Feb2020.xlsx',sheet_name = None,na_values = ['x', 'X', '']) # I don't think there's any x's or X's in the EGEDA xlsx file, but leaving as is (shouldn't make a difference)
