import json
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from .models import InferenceHistory
from .services.moderator import get_moderator_pipeline
from .services.sentiment import get_sentiment_pipeline
from .services.summarizer import get_summarizer_pipeline


SENTIMENT_RESULT = {
    "label": "positive",
    "score": 0.9,
    "scores": [{"label": "positive", "score": 0.9}],
}


class AiViewsTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username="tester",
            password="secret123",
        )
        self.other_user = user_model.objects.create_user(
            username="other",
            password="secret123",
        )

    def post_json(self, name, text, client=None, **headers):
        test_client = client or self.client
        return test_client.post(
            reverse(name),
            data=json.dumps({"text": text}),
            content_type="application/json",
            **headers,
        )

    def test_home_redirects_to_public_sentiment_page(self):
        response = self.client.get(reverse("my_gpt:home"))
        self.assertRedirects(response, reverse("my_gpt:sentiment"))

    def test_sentiment_page_is_public_and_renders_korean_ui(self):
        response = self.client.get(reverse("my_gpt:sentiment"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "감정 분석")
        self.assertContains(response, "cardiffnlp/twitter-roberta-base-sentiment-latest")

    def test_all_restricted_pages_redirect_with_required_and_next(self):
        for name in ("summarize", "moderate"):
            with self.subTest(name=name):
                response = self.client.get(reverse(f"my_gpt:{name}"))
                self.assertEqual(response.status_code, 302)
                self.assertIn("required=1", response.url)
                self.assertIn("next=", response.url)

    def test_all_restricted_run_endpoints_require_login(self):
        samples = {
            "summarize_run": "a" * 100,
            "moderate_run": "test",
        }
        for name, text in samples.items():
            with self.subTest(name=name):
                response = self.post_json(f"my_gpt:{name}", text)
                self.assertEqual(response.status_code, 302)
                self.assertIn("required=1", response.url)

    def test_login_returns_user_to_original_restricted_page(self):
        destination = reverse("my_gpt:summarize")
        restricted_response = self.client.get(destination)

        login_response = self.client.post(
            restricted_response.url,
            {"username": "tester", "password": "secret123"},
        )

        self.assertRedirects(login_response, destination)

    def test_required_login_page_keeps_username_input_usable(self):
        restricted_response = self.client.get(reverse("my_gpt:moderate"))
        login_page = self.client.get(restricted_response.url)

        self.assertEqual(login_page.status_code, 200)
        self.assertContains(login_page, "로그인 후 이용해주세요.")
        self.assertContains(login_page, 'id="id_username"')
        self.assertContains(login_page, "usernameInput.focus()")
        self.assertNotContains(login_page, 'id="id_username" disabled')

    def test_server_rejects_invalid_json_and_non_string_input(self):
        invalid_json = self.client.post(
            reverse("my_gpt:sentiment_run"),
            data="{",
            content_type="application/json",
        )
        self.assertEqual(invalid_json.status_code, 400)
        self.assertIn("JSON", invalid_json.json()["error"])

        non_string = self.client.post(
            reverse("my_gpt:sentiment_run"),
            data=json.dumps({"text": 123}),
            content_type="application/json",
        )
        self.assertEqual(non_string.status_code, 400)
        self.assertIn("텍스트", non_string.json()["error"])

    def test_server_validates_minimum_and_maximum_lengths(self):
        self.client.force_login(self.user)
        too_short = self.post_json("my_gpt:summarize_run", "too short")
        too_long = self.post_json("my_gpt:sentiment_run", "a" * 1001)
        whitespace = self.post_json("my_gpt:sentiment_run", "   ")

        self.assertEqual(too_short.status_code, 400)
        self.assertIn("100자", too_short.json()["error"])
        self.assertEqual(too_long.status_code, 400)
        self.assertIn("1,000자", too_long.json()["error"])
        self.assertEqual(whitespace.status_code, 400)

    def test_anonymous_sentiment_success_does_not_save(self):
        with patch("my_gpt.views.analyze_sentiment", return_value=SENTIMENT_RESULT):
            response = self.post_json("my_gpt:sentiment_run", "great")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(InferenceHistory.objects.count(), 0)

        refreshed_page = self.client.get(reverse("my_gpt:sentiment"))
        self.assertNotContains(refreshed_page, "great")

    def test_authenticated_success_is_saved_for_owner(self):
        self.client.force_login(self.user)
        with patch("my_gpt.views.analyze_sentiment", return_value=SENTIMENT_RESULT):
            response = self.post_json("my_gpt:sentiment_run", "great")

        self.assertEqual(response.status_code, 200)
        history = InferenceHistory.objects.get()
        self.assertEqual(history.user, self.user)
        self.assertEqual(history.task, InferenceHistory.Task.SENTIMENT)
        self.assertEqual(history.input_text, "great")
        self.assertEqual(history.result_data, SENTIMENT_RESULT)

    def test_failed_model_execution_is_not_saved(self):
        self.client.force_login(self.user)
        with patch("my_gpt.views.analyze_sentiment", side_effect=RuntimeError("failure")):
            response = self.post_json("my_gpt:sentiment_run", "great")

        self.assertEqual(response.status_code, 502)
        self.assertEqual(InferenceHistory.objects.count(), 0)
        self.assertNotIn("failure", response.json()["error"])

    def test_history_page_shows_only_latest_five_for_owner_and_task(self):
        for number in range(7):
            InferenceHistory.objects.create(
                user=self.user,
                task=InferenceHistory.Task.SENTIMENT,
                input_text=f"mine-{number}",
                output_text="positive",
            )
        InferenceHistory.objects.create(
            user=self.other_user,
            task=InferenceHistory.Task.SENTIMENT,
            input_text="other-user-secret",
            output_text="negative",
        )
        InferenceHistory.objects.create(
            user=self.user,
            task=InferenceHistory.Task.SUMMARIZE,
            input_text="different-task",
            output_text="summary",
        )
        self.client.force_login(self.user)

        response = self.client.get(reverse("my_gpt:sentiment"))
        histories = list(response.context["histories"])

        self.assertEqual(len(histories), 5)
        self.assertTrue(all(item.user == self.user for item in histories))
        self.assertTrue(
            all(item.task == InferenceHistory.Task.SENTIMENT for item in histories)
        )
        self.assertNotContains(response, "other-user-secret")
        self.assertNotContains(response, "different-task")

    def test_csrf_is_required_for_fetch_post(self):
        csrf_client = Client(enforce_csrf_checks=True)
        page = csrf_client.get(reverse("my_gpt:sentiment"))
        csrf_token = page.cookies["csrftoken"].value

        without_token = self.post_json(
            "my_gpt:sentiment_run",
            "great",
            client=csrf_client,
        )
        self.assertEqual(without_token.status_code, 403)

        with patch("my_gpt.views.analyze_sentiment", return_value=SENTIMENT_RESULT):
            with_token = self.post_json(
                "my_gpt:sentiment_run",
                "great",
                client=csrf_client,
                HTTP_X_CSRFTOKEN=csrf_token,
            )
        self.assertEqual(with_token.status_code, 200)


class ModelLoadingTests(TestCase):
    def test_all_pipelines_are_cached_instead_of_loaded_per_request(self):
        cases = (
            ("my_gpt.services.sentiment.pipeline", get_sentiment_pipeline),
            ("my_gpt.services.summarizer.pipeline", get_summarizer_pipeline),
            ("my_gpt.services.moderator.pipeline", get_moderator_pipeline),
        )

        for patch_target, getter in cases:
            with self.subTest(pipeline=patch_target), patch(patch_target) as pipeline_mock:
                pipeline_mock.return_value = object()
                getter.cache_clear()

                first = getter()
                second = getter()

                self.assertIs(first, second)
                pipeline_mock.assert_called_once()
                getter.cache_clear()
