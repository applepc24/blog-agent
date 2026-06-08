import time
from datetime import datetime, timedelta
import requests
from pytrends.request import TrendReq
from config import NAVER_CLIENT_ID, NAVER_CLIENT_SECRET

NAVER_DATALAB_URL = "https://openapi.naver.com/v1/datalab/search"


def get_naver_trends(keywords: list[str]) -> dict[str, float]:
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET,
        "Content-Type": "application/json"
    }
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d")
    results = {}

    for i in range(0, len(keywords), 5):
        batch = keywords[i:i+5]
        body = {
            "startDate": start_date,
            "endDate": end_date,
            "timeUnit": "month",
            "keywordGroups": [{"groupName": kw, "keywords": [kw]} for kw in batch]
        }
        try:
            resp = requests.post(NAVER_DATALAB_URL, json=body, headers=headers, timeout=10)
            resp.raise_for_status()
            for result in resp.json().get("results", []):
                ratios = [item["ratio"] for item in result.get("data", [])]
                results[result["title"]] = sum(ratios) / len(ratios) if ratios else 0
        except Exception:
            for kw in batch:
                results[kw] = 0
        time.sleep(0.5)

    return results


def get_google_trends(keywords: list[str]) -> dict[str, float]:
    results = {kw: 0.0 for kw in keywords}
    try:
        pytrends = TrendReq(hl='ko', tz=540, timeout=(10, 25))
        for i in range(0, len(keywords), 5):
            batch = keywords[i:i+5]
            pytrends.build_payload(batch, timeframe='today 12-m', geo='KR')
            data = pytrends.interest_over_time()
            if not data.empty:
                for kw in batch:
                    if kw in data.columns:
                        results[kw] = float(data[kw].mean())
            time.sleep(1)
    except Exception:
        pass
    return results


def score_keywords(keywords: list[str]) -> list[dict]:
    naver_scores = get_naver_trends(keywords)
    google_scores = get_google_trends(keywords)

    scored = []
    for kw in keywords:
        naver = naver_scores.get(kw, 0)
        google = google_scores.get(kw, 0)
        scored.append({
            "keyword": kw,
            "naver_score": round(naver, 1),
            "google_score": round(google, 1),
            "score": round((naver + google) / 2, 1)
        })

    return sorted(scored, key=lambda x: x["score"], reverse=True)
