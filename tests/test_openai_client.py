"""Offline tests for OpenAI Responses client; no API key or network required."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from openprover.llm.openai import OpenAIClient


class TestOpenAIClient(unittest.TestCase):
    def make_client(self, root):
        return OpenAIClient(archive_dir=Path(root), api_key="fake-key")

    def test_defaults_and_model_overrides(self):
        with tempfile.TemporaryDirectory() as d:
            c = self.make_client(d)
            p = c._payload([{"role": "user", "content": "hello"}])
            self.assertEqual(p["model"], "gpt-6-astra")
            self.assertEqual(p["reasoning"]["mode"], "pro")
            self.assertEqual(p["reasoning"]["effort"], "max")
            self.assertEqual(p["reasoning"]["summary"], "auto")
            self.assertFalse(p["store"])
            self.assertIn("reasoning.encrypted_content", p["include"])
            c2 = OpenAIClient(model="gpt-6.1-sol", api_key="fake-key",
                              reasoning_mode="standard", reasoning_effort="high",
                              reasoning_summary="off")
            self.assertEqual(c2._payload([])["reasoning"], {
                "mode": "standard", "effort": "high"})

    def test_usage_and_summary(self):
        raw = {"status": "completed", "output": [
            {"type": "reasoning", "summary": [{"text": "Summary, not raw CoT"}]},
            {"type": "message", "content": [{"type": "output_text", "text": "Answer"}]}],
            "usage": {"input_tokens": 100, "output_tokens": 200,
                      "input_tokens_details": {"cached_tokens": 30},
                      "output_tokens_details": {"reasoning_tokens": 120}}}
        result = OpenAIClient._decode(raw)
        self.assertEqual(result["result"], "Answer")
        self.assertEqual(result["thinking"], "Summary, not raw CoT")
        self.assertEqual(result["raw"]["usage"]["cache_read_input_tokens"], 30)
        self.assertEqual(result["raw"]["usage"]["output_tokens"], 200)

    def test_tool_continuation_replays_reasoning_items(self):
        with tempfile.TemporaryDirectory() as d:
            c = self.make_client(d)
            response = {"status": "completed", "output": [
                {"id": "rs_1", "type": "reasoning", "encrypted_content": "opaque"},
                {"type": "function_call", "call_id": "call_1",
                 "name": "lean_verify", "arguments": '{"code":"example"}'}],
                "usage": {"input_tokens": 5, "output_tokens": 10}}
            with patch.object(c, "_request", return_value=response):
                first = c.chat([{"role": "user", "content": "prove"}],
                               tools=[{"type": "function", "function": {
                                   "name": "lean_verify", "description": "verify",
                                   "parameters": {"type": "object", "properties": {}}}}])
            self.assertEqual(first["finish_reason"], "tool_calls")
            self.assertEqual(first["tool_calls"][0]["id"], "call_1")
            items = c._input([
                {"role": "user", "content": "prove"},
                {"role": "assistant", "content": None, "tool_calls": first["tool_calls"]},
                {"role": "tool", "tool_call_id": "call_1", "content": "OK"},
            ])
            self.assertEqual(items[1]["encrypted_content"], "opaque")
            self.assertEqual(items[2]["call_id"], "call_1")
            self.assertEqual(items[3]["type"], "function_call_output")

    def test_archive_and_stream_callback(self):
        with tempfile.TemporaryDirectory() as d:
            c = self.make_client(d)
            seen = []
            raw = {"status": "completed", "output": [
                {"type": "message", "content": [
                    {"type": "output_text", "text": "Proof"}]}],
                "usage": {"input_tokens": 1, "output_tokens": 2}}
            def fake_request(payload, callback):
                callback("Proof", "text")
                return raw
            with patch.object(c, "_request", side_effect=fake_request):
                result = c.call("problem", "system", stream_callback=lambda t,k: seen.append((t,k)))
            self.assertEqual(result["result"], "Proof")
            self.assertEqual(seen, [("Proof", "text")])
            self.assertTrue(list(Path(d).glob("call_*.raw.json")))

    def test_missing_api_key(self):
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaisesRegex(ValueError, "OPENAI_API_KEY"):
                OpenAIClient(api_key=None)


if __name__ == "__main__":
    unittest.main()
