import pandas as pd

def process_data(df):
    df["Votes"] = pd.to_numeric(df["Votes"], errors="coerce").fillna(0)

    # Winner per constituency
    winners = df.loc[df.groupby("Constituency")["Votes"].idxmax()]

    # Party seat count
    seat_count = winners["Party"].value_counts()

    return df, winners, seat_count
