import unittest
from decimal import Decimal

import pandas as pd

from app.analytics.visualization import create_chart


class VisualizationTests(unittest.TestCase):
    def test_single_aggregate_is_a_kpi_not_a_bar_chart(self):
        figure = create_chart(
            pd.DataFrame({"total_revenue": [Decimal("43501095.73")]})
        )

        self.assertEqual(len(figure.data), 0)
        self.assertEqual(
            figure.layout.annotations[0].text,
            "Total Revenue",
        )


if __name__ == "__main__":
    unittest.main()
