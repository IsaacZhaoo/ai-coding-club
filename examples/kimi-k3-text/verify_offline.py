"""Execute the unchanged tutorial script using synthetic HTTP responses only."""

import contextlib
import io
import json
import os
from pathlib import Path
import runpy
import unittest
from unittest import mock

import httpx
import openai


SCRIPT = Path(__file__).with_name("kimi_text.py")
REAL_CLIENT = openai.OpenAI
EXPECTED_BODY = {
    "model": "kimi-k3",
    "reasoning_effort": "low",
    "max_completion_tokens": 4096,
    "messages": [
        {"role": "user", "content": "Describe a code review in one sentence."}
    ],
}


class TutorialRequestTests(unittest.TestCase):
    def run_tutorial(self, base_url, *, finish_reason="stop", content="Mock answer."):
        requests = []

        def handler(request):
            self.assertEqual(request.method, "POST")
            self.assertEqual(str(request.url), base_url + "/chat/completions")
            self.assertEqual(request.headers["authorization"], "Bearer offline-test-key")
            self.assertEqual(json.loads(request.content), EXPECTED_BODY)
            requests.append(request)
            return httpx.Response(
                200,
                json={
                    "id": "chatcmpl-offline-fixture",
                    "object": "chat.completion",
                    "created": 0,
                    "model": "kimi-k3",
                    "choices": [{
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": content,
                            "reasoning_content": "Synthetic hidden reasoning.",
                        },
                        "finish_reason": finish_reason,
                    }],
                    "usage": {
                        "prompt_tokens": 12,
                        "completion_tokens": 8,
                        "total_tokens": 20,
                    },
                },
            )

        def client_factory(**kwargs):
            return REAL_CLIENT(
                **kwargs,
                max_retries=0,
                http_client=httpx.Client(
                    transport=httpx.MockTransport(handler),
                    trust_env=False,
                ),
            )

        output = io.StringIO()
        env = {"MOONSHOT_API_KEY": "offline-test-key", "MOONSHOT_BASE_URL": base_url}
        with mock.patch.dict(os.environ, env), mock.patch.object(
            openai, "OpenAI", side_effect=client_factory
        ), mock.patch(
            "socket.socket.connect", side_effect=AssertionError("Network forbidden")
        ), contextlib.redirect_stdout(output):
            runpy.run_path(str(SCRIPT), run_name="__main__")
        self.assertEqual(len(requests), 1)
        return output.getvalue()

    def test_global_endpoint_and_final_answer(self):
        self.assertEqual(
            self.run_tutorial("https://api.moonshot.ai/v1"), "Mock answer.\n"
        )

    def test_cn_endpoint_and_final_answer(self):
        self.assertEqual(
            self.run_tutorial("https://api.moonshot.cn/v1"), "Mock answer.\n"
        )

    def test_incomplete_response_is_not_printed_as_success(self):
        with self.assertRaisesRegex(RuntimeError, "finish_reason=length"):
            self.run_tutorial("https://api.moonshot.ai/v1", finish_reason="length")

    def test_empty_final_answer_is_not_success(self):
        with self.assertRaisesRegex(RuntimeError, "No complete text answer"):
            self.run_tutorial("https://api.moonshot.ai/v1", content="")


if __name__ == "__main__":
    unittest.main(verbosity=2)
