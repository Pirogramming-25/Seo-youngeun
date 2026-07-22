from functools import lru_cache

from transformers import pipeline

from .common import pipeline_options

MODEL_ID = "unitary/toxic-bert"


@lru_cache(maxsize=1)
def get_moderator_pipeline():
    return pipeline(
        "text-classification",
        model=MODEL_ID,
        top_k=None,
        **pipeline_options(),
    )


def moderate_text(text):
    raw = get_moderator_pipeline()(text, truncation=True, max_length=512)
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
