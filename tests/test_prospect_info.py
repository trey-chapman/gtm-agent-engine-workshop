import os
import unittest

os.environ["OPENAI_API_KEY"] = "test-key"
os.environ["LANGSMITH_TRACING"] = "false"

from gtm_agent import data_service
from gtm_agent.gtm_agent import build_prospect_profile


class ProspectInfoTest(unittest.TestCase):
    def test_update_persists_and_invalidates_cached_profile(self):
        prospect_id = "LEAD-12853"
        technology = "Test Technology"
        data_service._PROFILES.pop(prospect_id, None)
        original_tech_stack = list(data_service.PROSPECTS[prospect_id]["tech_stack"])

        try:
            cached_profile = build_prospect_profile.invoke({"prospect_id": prospect_id})
            self.assertNotIn(technology, cached_profile["prospect_profile"]["tech_stack"])

            data_service.update_prospect_info(prospect_id, technology)

            self.assertIn(technology, data_service.fetch_tech_stack(prospect_id))
            refreshed_profile = build_prospect_profile.invoke({"prospect_id": prospect_id})
            self.assertIn(technology, refreshed_profile["prospect_profile"]["tech_stack"])
        finally:
            data_service.PROSPECTS[prospect_id]["tech_stack"] = original_tech_stack
            data_service._PROFILES.pop(prospect_id, None)


if __name__ == "__main__":
    unittest.main()
