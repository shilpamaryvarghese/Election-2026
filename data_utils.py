import pandas as pd

def process_data(df):
    df["Votes"] = pd.to_numeric(df["Votes"], errors="coerce").fillna(0)
    winners = df.loc[df.groupby("Constituency")["Votes"].idxmax()]
    seat_count = winners["Party"].value_counts()
    return df, winners, seat_count
