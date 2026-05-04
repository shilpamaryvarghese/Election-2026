import pandas as pd


def process_data(df):
    if df is None or df.empty:
        return pd.DataFrame(), pd.DataFrame(), pd.Series()

    df = df.dropna(subset=["Constituency", "Party"])

    df["Votes"] = pd.to_numeric(
        df["Votes"], errors="coerce"
    ).fillna(0)

    winners = (
        df.sort_values("Votes", ascending=False)
        .drop_duplicates("Constituency")
    )

    seat_count = winners["Party"].value_counts()

    return df, winners, seat_count
