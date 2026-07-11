import pandas as pd


def read_csv(file):

    df = pd.read_csv(file.file)

    return df