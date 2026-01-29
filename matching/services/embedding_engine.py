import requests

HF_ML_URL = "https://alaa95mrs-smart-recruitment-ml.hf.space/similarity"

def similarity(text1, text2):
    response = requests.post(
        HF_ML_URL,
        json={
            "cv": text1,
            "job": text2
        },
        timeout=20
    )

    response.raise_for_status()
    return response.json()["score"]
