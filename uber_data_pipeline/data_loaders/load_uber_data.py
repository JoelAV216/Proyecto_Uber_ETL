import io
import pandas as pd
from mage_ai.io.file import FileIO

if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader

@data_loader
def load_data_from_file(**kwargs) -> pd.DataFrame:
    filepath = '/home/src/data/uber_data.csv'
    return pd.read_csv(filepath)