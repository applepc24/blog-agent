import httpx
from config import WP_URL, WP_USERNAME, WP_APP_PASSWORD
import markdown as md


def upload_post(title: str, content: str, tags: list[str] = [], status: str = "draft", focus_keyword: str = "") -> dict:
    url = f"{WP_URL}/wp-json/wp/v2/posts"
    auth = (WP_USERNAME, WP_APP_PASSWORD)

    data = {
        "title": title,
        "content": md.markdown(content),
        "status": status,
        "tags_input": ",".join(tags),
        "meta": {
            "rank_math_focus_keyword": focus_keyword,
        },
    }

    response = httpx.post(url, json=data, auth=auth)
    response.raise_for_status()
    return response.json()
