from config import *

import pickle
import pandas as pd


def load_df(dataset: str) -> pd.DataFrame:
    df_abs_path = DATASETS_ABS_PATHS[dataset]
    
    df = pd.read_csv()
    df.rename(columns=lambda x: x.replace(' ', '_'), inplace=True) # Replace spaces with underscores in column names
    df = df.convert_dtypes()

    if dataset == "BWSAS":
        df.Measurement_Timestamp = pd.to_datetime(df.Measurement_Timestamp, format="%m/%d/%Y %I:%M:%S %p")


def load_dfs(datasets: list) -> list[pd.DataFrame]:
    dfs = []
    
    for dataset in datasets:
        dfs.append(load_df(dataset))
    
    return dfs


def pickle_dfs(datasets: list):
    dfs = load_dfs()
    dfs_pkl = [pickle.loads(df) for df in dfs]
