
import os
import numpy as np
import pandas as pd
import re 

def createFolder(unique_id):
    unique_data = f'DATA/{unique_id}'
    unique_data_check = os.path.exists(unique_data)
    if unique_data_check == False:
        os.makedirs(unique_data)

def convert_dict_to_csv(data_dict, unique_id):
    max_length = max(len(v) for v in data_dict.values())
    # Pad the lists with NaN to make them of equal length
    padded_data = {key: values + [np.nan] * (max_length - len(values)) for key, values in data_dict.items()}
    # Convert the dictionary to a DataFrame
    df = pd.DataFrame(padded_data)
    df.to_csv(f"DATA/{unique_id}/output.csv", index=False)

def extract_time(filename):
    match = re.search(r'\d{2}\.\d{2}\.\d{2}', filename)
    if match:
        return match.group()
    return ''