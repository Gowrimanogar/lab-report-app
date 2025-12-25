import pandas as pd
from datetime import date

def save_data(parameters):
    try:
        df = pd.read_csv("patient_data.csv")  # try to read existing CSV
    except:
        df = pd.DataFrame(columns=["Date", "Parameter", "Value", "Status"])  # create new

    today = date.today()

    for param, info in parameters.items():
        df.loc[len(df)] = [today, param, info["value"], info["status"]]

    df.to_csv("patient_data.csv", index=False)
