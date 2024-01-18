from config import *

import pandas as pd


def get_dfs(datasets: list):
    dfs = []
    
    for dataset in datasets:
        df = pd.read_csv(DATASETS_ABS_PATHS[dataset])
        df.rename(columns=lambda x: x.replace(' ', '_'), inplace=True) # Replace spaces with underscores in column names
        df = df.convert_dtypes()

        if dataset == "BWSAS":
            df.Measurement_Timestamp = pd.to_datetime(df.Measurement_Timestamp, format="%m/%d/%Y %I:%M:%S %p")
        
        dfs.append(df)
    
    return dfs
