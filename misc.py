from pms import adduser
import pandas as pd


def batchhandler(file):
    df = pd.read_csv(file)
    templist = []
    df_new = df.drop(["Role", "AppID"], axis=1)
    for i in range(len(df)):
        result, passw = adduser(df.iloc[i, 0], df.iloc[i, 1], df.iloc[i, 2])
        if result:
            templist.append(passw)
        else:
            templist.append("Duplicate user")
    df_new["Password"] = templist
    return df_new