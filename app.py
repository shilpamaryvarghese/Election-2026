from flask import Flask, render_template, jsonify
import pandas as pd
import requests

app = Flask(__name__)

CSV_FILE = "kerala_2026_candidates.csv"
API_URL = "https://api.opendatakerala.org/api/kla2026/results/all.json"


def load_data():
    df = pd.read_csv(CSV_FILE)
    return df


def get_live_data():
    try:
        return requests.get(API_URL, timeout=10).json()
    except:
        return []


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/constituency")
def constituency_page():
    return render_template("constituency.html")


@app.route("/partywise")
def partywise_page():
    return render_template("partywise.html")


@app.route("/candidates")
def candidates_page():
    return render_template("candidates.html")


# ---------------- APIs ----------------

@app.route("/api/constituencies")
def constituencies():
    df = load_data()
    return jsonify({
        "data": sorted(df["Constituency_Name"].unique())
    })


@app.route("/api/constituency/<name>")
def constituency(name):

    df = load_data()
    df = df[df["Constituency_Name"] == name]

    live = get_live_data()

    if live:
        live_df = pd.DataFrame(live)

        merged = pd.merge(
            df,
            live_df,
            left_on="Candidate_Name",
            right_on="candidate",
            how="left"
        )

        merged["votes"] = merged["votes"].fillna(0)
        merged["status"] = merged["status"].fillna("NA")

        return jsonify({"data": merged.to_dict(orient="records")})

    else:
        df["votes"] = 0
        df["status"] = "Dummy"
        return jsonify({"data": df.to_dict(orient="records")})


@app.route("/api/summary")
def summary():

    live = get_live_data()
    df = pd.DataFrame(live)

    def alliance(p):
        p = str(p).upper()
        if p in ["INC","IUML"]: return "UDF"
        if p in ["CPIM","CPI"]: return "LDF"
        if p in ["BJP"]: return "NDA"
        return "Others"

    df["Alliance"] = df["party"].apply(alliance)

    summary = df.groupby("Alliance").agg(
        Seats=("status", lambda x: (x.str.lower()=="won").sum()),
        Votes=("votes","sum")
    ).reset_index()

    return jsonify({"data": summary.to_dict(orient="records")})


@app.route("/api/partywise")
def partywise():
    live = get_live_data()
    df = pd.DataFrame(live)

    df["party"] = df["party"].str.upper()

    summary = df.groupby("party").agg(
        Seats=("status", lambda x: (x.str.lower()=="won").sum()),
        Votes=("votes","sum")
    ).reset_index()

    return jsonify({"data": summary.to_dict(orient="records")})


@app.route("/api/search/<query>")
def search(query):
    live = get_live_data()
    df = pd.DataFrame(live)

    df = df[df["candidate"].str.lower().str.contains(query.lower())]

    return jsonify({"data": df.to_dict(orient="records")})


if __name__ == "__main__":
    app.run(debug=True)
