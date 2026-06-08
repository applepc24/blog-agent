import json
import re

def parse_seo(raw: str) -> dict:
    cleaned = re.sub(r"```(?:json)?\s*|\s*```", "", raw).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    title, meta_description, tags = "", "", []
    for line in cleaned.splitlines():
        line = line.strip()
        if match := re.match(r"^[-*]\s*제목\s*:\s*(.*)", line):
            title = match.group(1).strip(" \"'[]")
        elif match := re.match(r"^[-*]\s*메타디스크립션\s*:\s*(.*)", line):
            meta_description = match.group(1).strip(" \"'[]")
        elif match := re.match(r"^[-*]\s*태그\s*:\s*(.*)", line):
            tags = [t.strip(" \"'[]") for t in match.group(1).split(",") if t.strip()]
    
    return {"title": title, "meta_description": meta_description, "tags": tags}