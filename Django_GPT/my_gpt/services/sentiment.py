from functools import lru_cache

from transformers import pipeline

from .common import pipeline_options

MODEL_ID = "cardiffnlp/twitter-roberta-base-sentiment-latest"


@lru_cache(maxsize=1)
def get_sentiment_pipeline():
    return pipeline(
        "text-classification",
        model=MODEL_ID,
        top_k=None,
        **pipeline_options(),
    )


def analyze_sentiment(text):
    raw = get_sentiment_pipeline()(text, truncation=True, max_length=512)
    rows = raw[0] if raw and isinstance(raw[0], list) else raw
    scores = sorted(
        (
            {"label": item["label"].lower(), "score": float(item["score"])}
            for item in rows
        ),
        key=lambda item: item["score"],
        reverse=True,
    )
    return {"label": scores[0]["label"], "score": scores[0]["score"], "scores": scores}
