from functools import lru_cache

from transformers import pipeline

from .common import pipeline_options

MODEL_ID = "sshleifer/distilbart-cnn-6-6"


@lru_cache(maxsize=1)
def get_summarizer_pipeline():
    return pipeline("summarization", model=MODEL_ID, **pipeline_options())


def summarize_text(text):
    result = get_summarizer_pipeline()(
        text,
        max_length=180,
        min_length=30,
        do_sample=False,
        truncation=True,
    )
    summary = result[0]["summary_text"].strip()
    return {
        "summary": summary,
        "original_length": len(text),
        "summary_length": len(summary),
        "summary_ratio": len(summary) / len(text) * 100,
    }
