from flask import Flask, render_template, jsonify
import pandas as pd
import requests

app = Flask(__name__)

CSV_FILE = "kerala_2026_candidates.csv"
API_URL = "https://api.opendatakerala.org/api/kla2026/results/all.json"


# ---------------- LOAD CSV ----------------
def load_data():
    df = pd.read_csv(CSV_FILE)

    df["Candidate_Name"] = df["Candidate_Name"].astype(str)
    df["Party"] = df["Party"].astype(str)
    df["Constituency_Name"] = df["Constituency_Name"].astype(str)

    return df


# ---------------- FETCH LIVE DATA ----------------
def get_live_data():
    try:
        res = requests.get(API_URL, timeout=10)
        return res.json()
    except:
        return []


# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("dashboard.html")


# ---------------- API: CONSTITUENCIES ----------------
@app.route("/api/constituencies")
def constituencies():
    df = load_data()
    return jsonify({
        "data": sorted(df["Constituency_Name"].unique())
    })


# ---------------- API: CONSTITUENCY DATA ----------------
@app.route("/api/constituency/<name>")
def constituency(name):
    df = load_data()
    df = df[df["Constituency_Name"] == name]

    live = get_live_data()

    if live:
        live_df = pd.DataFrame(live)

        live_df["candidate"] = live_df["candidate"].str.lower()
        live_df["party"] = live_df["party"].str.lower()

        df["Candidate_Name"] = df["Candidate_Name"].str.lower()
        df["Party"] = df["Party"].str.lower()

        merged = pd.merge(
            df,
            live_df,
            left_on=["Candidate_Name", "Party"],
            right_on=["candidate", "party"],
            how="left"
        )

        merged["votes"] = merged["votes"].fillna(0)
        merged["status"] = merged["status"].fillna("NA")

        return jsonify({"data": merged.to_dict(orient="records")})

    else:
        df["votes"] = 0
        df["status"] = "Dummy"

        return jsonify({"data": df.to_dict(orient="records")})


if __name__ == "__main__":
    app.run(debug=True)
