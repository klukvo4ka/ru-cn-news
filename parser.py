import feedparser
from datetime import datetime

SOURCES = [
    {"url": "https://tass.ru/rss/v2.xml", "source": "ТАСС", "lang": "ru"},
    {"url": "https://ria.ru/export/rss2/archive/index.xml", "source": "РИА Новости", "lang": "ru"},
    {"url": "http://www.xinhuanet.com/english/rss/chinavoice.xml", "source": "Синьхуа", "lang": "en"},
    {"url": "https://www.globaltimes.cn/rss/outbrain.xml", "source": "Global Times", "lang": "en"},
]

KEYWORDS = ["China", "Китай", "Russia", "Россия", "РФ", "中国", "俄罗斯", "российско-китайский"]


def _matches(title, description):
    text = f"{title} {description}".lower()
    return any(kw.lower() in text for kw in KEYWORDS)


def _parse_date(entry):
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        return datetime(*entry.published_parsed[:6]).isoformat()
    return datetime.utcnow().isoformat()


def fetch_articles():
    results = []
    for src in SOURCES:
        try:
            feed = feedparser.parse(src["url"])
        except Exception:
            continue
        for entry in feed.entries:
            title = entry.get("title", "")
            description = entry.get("summary", "")
            link = entry.get("link", "")
            if not link or not _matches(title, description):
                continue
            results.append({
                "title": title,
                "description": description,
                "link": link,
                "pub_date": _parse_date(entry),
                "source": src["source"],
                "lang": src["lang"],
            })
    return results
