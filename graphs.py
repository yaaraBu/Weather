import pandas as pd
import pygwalker as pyg

data_json_path = "/home/bina/Desktop/GitHubYaara/weather_data.json"
df = pd.read_json(data_json_path)
#print(df.to_string())

#pyg.walk(df)