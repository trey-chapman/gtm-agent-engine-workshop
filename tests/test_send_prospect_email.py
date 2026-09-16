import unittest
import os
from types import SimpleNamespace

os.environ.setdefault("OPENAI_API_KEY", "test-key")

from gtm_agent.gtm_agent import send_prospect_email


def _runtime():
    return SimpleNamespace(config={"metadata": {}})


class SendProspectEmailTests(unittest.TestCase):
    def test_blocks_disqualified_prospect(self):
        result = send_prospect_email.func(
            {
                "prospect_id": "LEAD-50001",
                "name": "Priya Nair",
                "email": "priya.nair@brightwaveapps.com",
                "disqualified": False,
            },
            "Checking in",
            "Hello",
            _runtime(),
        )

        self.assertEqual(result, {
            "status": "blocked",
            "reason": "prospect is disqualified - outreach suppressed",
            "prospect_id": "LEAD-50001",
        })
        self.assertNotIn("message_id", result)

    def test_sends_eligible_prospect(self):
        result = send_prospect_email.func(
            {
                "prospect_id": "LEAD-12853",
                "name": "Omar Okafor",
                "email": "omar.okafor@northstaranalytics.com",
            },
            "Checking in",
            "Hello",
            _runtime(),
        )

        self.assertEqual(result["status"], "sent")
        self.assertTrue(result["message_id"].startswith("msg-"))
