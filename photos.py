import requests

def get_candidate_photo(name):
    try:
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{name}"
        res = requests.get(url).json()

        if "thumbnail" in res:
            return res["thumbnail"]["source"]

    except:
        pass

    return "https://via.placeholder.com/100"
