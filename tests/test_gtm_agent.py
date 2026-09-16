import os
import unittest

os.environ.setdefault("OPENAI_API_KEY", "sk-test")
os.environ.setdefault("LANGSMITH_TRACING", "false")

from langchain.tools import ToolRuntime
from gtm_agent.gtm_agent import send_prospect_email
from gtm_agent.gtm_records import REP_IDS


class SendProspectEmailTest(unittest.TestCase):
    def test_resolves_sender_from_run_metadata_when_from_rep_is_omitted(self):
        rep = REP_IDS[0]
        runtime = ToolRuntime(
            state={},
            context={},
            config={"metadata": {"user_id": rep["rep_id"]}},
            stream_writer=lambda _: None,
            tool_call_id=None,
            store=None,
        )

        result = send_prospect_email.func(
            {"name": "Test Prospect", "email": "prospect@example.com"},
            "Hello",
            "Body",
            runtime,
            None,
        )

        self.assertEqual(result["from"], rep["email"])
        self.assertEqual(result["from_name"], rep["name"])


if __name__ == "__main__":
    unittest.main()
