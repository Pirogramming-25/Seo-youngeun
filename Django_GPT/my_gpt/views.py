import json
import logging

from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .decorators import model_login_required
from .models import InferenceHistory
from .services.moderator import MODEL_ID as MODERATOR_MODEL, moderate_text
from .services.sentiment import MODEL_ID as SENTIMENT_MODEL, analyze_sentiment
from .services.summarizer import MODEL_ID as SUMMARY_MODEL, summarize_text

logger = logging.getLogger(__name__)

RULES = {
    "sentiment": (1, 1000, "분석할 문장을 입력해주세요.", "문장은 1,000자 이하로 입력해주세요."),
    "summarize": (100, 5000, "요약할 문서를 100자 이상 입력해주세요.", "문서는 5,000자 이하로 입력해주세요."),
    "moderate": (1, 1000, "분석할 문장을 입력해주세요.", "문장은 1,000자 이하로 입력해주세요."),
}


def home(request):
    return redirect("my_gpt:sentiment")


def _histories(request, task):
    if not request.user.is_authenticated:
        return []
    return InferenceHistory.objects.filter(user=request.user, task=task)[:5]


def _page(request, template, task, model):
    context = {
        "active_tab": task,
        "model_id": model,
        "histories": _histories(request, task),
    }
    return render(request, template, context)


def sentiment_page(request):
    return _page(request, "my_gpt/sentiment.html", "sentiment", SENTIMENT_MODEL)


@model_login_required
def summarize_page(request):
    return _page(request, "my_gpt/summarize.html", "summarize", SUMMARY_MODEL)


@model_login_required
def moderate_page(request):
    return _page(request, "my_gpt/moderate.html", "moderate", MODERATOR_MODEL)


def _read_text(request, task):
    try:
        payload = json.loads(request.body or b"{}")
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None, "올바른 JSON 요청이 아닙니다."

    text = payload.get("text")
    if not isinstance(text, str):
        return None, "텍스트 형식으로 입력해주세요."

    clean = text.strip()
    minimum, maximum, short_error, long_error = RULES[task]
    if len(clean) < minimum:
        return None, short_error
    if len(clean) > maximum:
        return None, long_error
    return clean, None


def _execute(request, task, service, output_getter):
    text, error = _read_text(request, task)
    if error:
        return JsonResponse({"error": error}, status=400)

    try:
        data = service(text)
        output = output_getter(data)
        if request.user.is_authenticated:
            history = InferenceHistory.objects.create(
                user=request.user,
                task=task,
                input_text=text,
                output_text=output,
                result_data=data,
            )
            history_data = {
                "input_text": text,
                "output_text": output,
                "created_at": history.created_at.isoformat(),
            }
        else:
            history_data = {"input_text": text, "output_text": output}
        return JsonResponse({"result": data, "history": history_data})
    except Exception:
        logger.exception("Model inference failed for task=%s", task)
        return JsonResponse(
            {"error": "모델 실행에 실패했습니다. 잠시 후 다시 시도해주세요."},
            status=502,
        )


@require_POST
def sentiment_run(request):
    return _execute(
        request,
        "sentiment",
        analyze_sentiment,
        lambda data: f"{data['label']}: {data['score']:.2%}",
    )


@require_POST
@model_login_required
def summarize_run(request):
    return _execute(request, "summarize", summarize_text, lambda data: data["summary"])


@require_POST
@model_login_required
def moderate_run(request):
    return _execute(
        request,
        "moderate",
        moderate_text,
        lambda data: f"{data['label']}: {data['score']:.2%}",
    )

