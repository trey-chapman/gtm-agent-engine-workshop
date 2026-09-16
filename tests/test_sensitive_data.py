import json
import os
import unittest
from unittest.mock import patch

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("LANGSMITH_TRACING", "false")

from gtm_agent import data_service, gtm_agent


class SensitiveDataTests(unittest.TestCase):
    def setUp(self):
        self.prospect_id = "TEST-SENSITIVE-001"
        self.record = {
            "name": "Synthetic Prospect",
            "email": "synthetic@example.com",
            "billing_qualification": {
                "tax_id": "TEST-TAX-ID",
                "date_of_birth": "2000-01-01",
                "card_on_file": "TEST-CARD",
                "credit_check_ref": "TEST-CREDIT-REF",
            },
            "engagement_history": [{"channel": "Synthetic event"}],
            "account_details": [{"account": "Synthetic Account"}],
            "tech_stack": ["Synthetic Stack"],
            "annual_revenue": 1000000,
        }
        self.offering = {
            "required_tech_stack": ["Synthetic Stack"],
            "min_annual_revenue": 1,
            "description": "Synthetic offering",
        }
        data_service._PROFILES.pop(self.prospect_id, None)

    def tearDown(self):
        data_service._PROFILES.pop(self.prospect_id, None)

    def test_prospect_tools_do_not_serialize_billing_fields(self):
        with patch.dict(data_service.PROSPECTS, {self.prospect_id: self.record}, clear=False):
            contact = gtm_agent.get_prospect.invoke({"prospect_id": self.prospect_id})
            profile = gtm_agent.build_prospect_profile.invoke({"prospect_id": self.prospect_id})
            unredacted_profile = {**profile["prospect_profile"], "billing_qualification": self.record["billing_qualification"]}

            with patch.object(gtm_agent, "_scoring_llm") as scoring_llm:
                scoring_llm.invoke.return_value.model_dump.return_value = {"score": 90}
                gtm_agent.score_prospect.invoke({
                    "prospect_profile": unredacted_profile,
                    "offering": self.offering,
                })

        contact_json = json.dumps(contact)
        profile_json = json.dumps(profile)
        scoring_payload = scoring_llm.invoke.call_args.args[0][1]["content"]
        for serialized in (contact_json, profile_json, scoring_payload):
            for sensitive_key in ("tax_id", "date_of_birth", "card_on_file", "credit_check_ref"):
                self.assertNotIn(sensitive_key, serialized)


if __name__ == "__main__":
    unittest.main()
