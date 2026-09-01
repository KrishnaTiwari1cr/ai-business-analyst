import unittest
from unittest.mock import patch

import pandas as pd

from app.analytics.monthly_analysis import compare_months
from app.analytics.question_parser import get_target_month
from app.analytics.root_cause_request import parse_root_cause_request
from app.agents.business_agent import is_root_cause_question
from app.graph.nodes import root_cause_analysis_node


class RootCausePipelineTests(unittest.TestCase):

    def setUp(self):
        self.monthly = pd.DataFrame(
            {
                "month": pd.to_datetime(
                    ["2025-10-01", "2025-08-01", "2025-09-01"]
                ),
                "revenue": [180.0, 200.0, 150.0],
            }
        )

    def test_parser_accepts_full_and_abbreviated_months(self):
        self.assertEqual(
            get_target_month("Why did revenue drop in September 2025?"),
            {"month": 9, "year": 2025},
        )
        self.assertEqual(
            get_target_month("Why did revenue drop in Oct 2025?"),
            {"month": 10, "year": 2025},
        )

    def test_comparisons_are_chronological(self):
        compared = compare_months(self.monthly)
        self.assertEqual(compared["month"].dt.month.tolist(), [8, 9, 10])
        self.assertEqual(compared.loc[1, "previous_revenue"], 200.0)
        self.assertEqual(compared.loc[2, "previous_revenue"], 150.0)

    def test_root_cause_question_metadata_is_consistent(self):
        self.assertEqual(
            parse_root_cause_request(
                "Which products caused the largest revenue loss?"
            ),
            {"focus": "products", "direction": "decline"},
        )
        self.assertEqual(
            parse_root_cause_request(
                "Which categories drove the revenue increase?"
            ),
            {"focus": "categories", "direction": "increase"},
        )
        self.assertTrue(
            is_root_cause_question(
                "What factors contributed to product sales decline?"
            )
        )

    @patch("app.graph.nodes.generate_deep_root_cause_insight")
    @patch("app.graph.nodes.analyze_product_change")
    @patch("app.graph.nodes.analyze_category_change")
    @patch("app.graph.nodes.get_monthly_revenue")
    def test_explicit_months_pass_distinct_periods_to_insight(
        self,
        get_monthly_revenue,
        analyze_category_change,
        analyze_product_change,
        generate_insight,
    ):
        get_monthly_revenue.return_value = self.monthly
        analyze_category_change.return_value = pd.DataFrame()
        analyze_product_change.return_value = pd.DataFrame()
        generate_insight.return_value = ("test insight", "test")

        september = root_cause_analysis_node(
            {"question": "Why did revenue drop in September 2025?"}
        )
        october = root_cause_analysis_node(
            {"question": "Why did revenue drop in October 2025?"}
        )

        self.assertEqual(september["previous_month"], "2025-08-01")
        self.assertEqual(september["current_month"], "2025-09-01")
        self.assertEqual(october["previous_month"], "2025-09-01")
        self.assertEqual(october["current_month"], "2025-10-01")

        self.assertEqual(
            generate_insight.call_args_list[0].kwargs["question"],
            "Why did revenue drop in September 2025?",
        )
        self.assertEqual(
            generate_insight.call_args_list[1].kwargs["question"],
            "Why did revenue drop in October 2025?",
        )
        self.assertEqual(
            generate_insight.call_args_list[0].kwargs["period_source"],
            "user_specified",
        )
        self.assertEqual(
            september["root_cause_focus"],
            "overall",
        )
        self.assertEqual(
            october["root_cause_direction"],
            "decline",
        )


if __name__ == "__main__":
    unittest.main()
