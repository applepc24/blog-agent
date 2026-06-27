import httpx
from config import WP_URL, WP_USERNAME, WP_APP_PASSWORD
import markdown as md


def upload_post(title: str, content: str, tags: list[str] = [], status: str = "draft", focus_keyword: str = "") -> dict:
    url = f"{WP_URL}/wp-json/wp/v2/posts"
    auth = (WP_USERNAME, WP_APP_PASSWORD)

    data = {
        "title": title,
        "content": md.markdown(content, extensions=["fenced_code", "tables"]),
        "status": status,
        "tags_input": ",".join(tags),
        "meta": {
            "rank_math_focus_keyword": focus_keyword,
        },
    }

    response = httpx.post(url, json=data, auth=auth)
    response.raise_for_status()
    return response.json()


def update_post(post_id: int, status: str = None, title: str = None, content: str = None, tags: list[str] = None, focus_keyword: str = None) -> dict:
    url = f"{WP_URL}/wp-json/wp/v2/posts/{post_id}"
    auth = (WP_USERNAME, WP_APP_PASSWORD)

    data = {}
    if status is not None:
        data["status"] = status
    if title is not None:
        data["title"] = title
    if content is not None:
        data["content"] = md.markdown(content, extensions=["fenced_code", "tables"])
    if tags is not None:
        data["tags_input"] = ",".join(tags)
    if focus_keyword is not None:
        data["meta"] = {"rank_math_focus_keyword": focus_keyword}

    response = httpx.post(url, json=data, auth=auth)
    response.raise_for_status()
    return response.json()


def delete_post(post_id: int) -> dict:
    url = f"{WP_URL}/wp-json/wp/v2/posts/{post_id}"
    auth = (WP_USERNAME, WP_APP_PASSWORD)
    response = httpx.delete(url, auth=auth, params={"force": True})
    response.raise_for_status()
    return response.json()
