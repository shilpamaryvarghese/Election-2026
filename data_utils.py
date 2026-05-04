import pandas as pd

def process_data(df):
    if df is None or df.empty:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    # Clean
    df = df.dropna(subset=["Constituency", "Party"])

    # Ensure numeric votes
    df["Votes"] = pd.to_numeric(df["Votes"], errors="coerce").fillna(0)

    # 🏆 Winners / Leading
    winners = df.copy()

    # 📺 Party seat count
    seat_count = df["Party"].value_counts()

    return df, winners, seat_count
