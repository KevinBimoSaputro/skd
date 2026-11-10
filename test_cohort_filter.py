import unittest
import pandas as pd
import datetime
from unittest.mock import patch, MagicMock

class TestCohortSelection(unittest.TestCase):
    def test_sidebar_cohort_prioritizes_latest_year(self):
        # Scenario: 10 users in 2026, 1 user in 2027
        users_for_filter = [
            {"id": i, "nama": f"User {i}", "tahun_aktif": 2026} for i in range(1, 11)
        ] + [
            {"id": 11, "nama": "User 11", "tahun_aktif": 2027}
        ]

        df_u_filter = pd.DataFrame(users_for_filter)
        filter_options = ["Semua"]
        unique_years = []
        if "tahun_aktif" in df_u_filter.columns:
            raw_years = df_u_filter["tahun_aktif"].dropna().unique()
            unique_years = sorted([int(y) for y in raw_years])
            filter_options.extend(unique_years)

        year_now = 2025  # Even if current year is 2025
        latest_year = max(unique_years) if unique_years else year_now
        default_idx = filter_options.index(latest_year)

        self.assertEqual(filter_options, ["Semua", 2026, 2027])
        self.assertEqual(latest_year, 2027)
        self.assertEqual(filter_options[default_idx], 2027)

    def test_sidebar_cohort_fallback_empty_data(self):
        users_for_filter = []
        df_u_filter = pd.DataFrame(users_for_filter)
        filter_options = ["Semua"]
        unique_years = []
        if not df_u_filter.empty and "tahun_aktif" in df_u_filter.columns:
            raw_years = df_u_filter["tahun_aktif"].dropna().unique()
            unique_years = sorted([int(y) for y in raw_years])
            filter_options.extend(unique_years)

        year_now = datetime.date.today().year
        latest_year = max(unique_years) if unique_years else year_now
        try:
            default_idx = filter_options.index(latest_year)
        except (ValueError, IndexError):
            default_idx = 0

        self.assertEqual(default_idx, 0)
        self.assertEqual(filter_options[default_idx], "Semua")

    def test_prepare_admin_data_filters_by_latest_year(self):
        import os
        os.environ["SUPABASE_URL"] = "http://localhost:54321"
        os.environ["SUPABASE_KEY"] = "testkey"

        with patch("main.fetch_all_users") as mock_users, \
             patch("main.fetch_all_scores") as mock_scores, \
             patch("main.st") as mock_st:

            # Setup users: 10 in 2026, 1 in 2027, 1 admin
            mock_users.return_value = [
                {"id": str(i), "nama": f"User {i}", "role": "user", "tahun_aktif": 2026} for i in range(1, 11)
            ] + [
                {"id": "11", "nama": "User Baru 2027", "role": "user", "tahun_aktif": 2027},
                {"id": "99", "nama": "Admin", "role": "admin", "tahun_aktif": 2026}
            ]
            mock_scores.return_value = [
                {"id": "s1", "user_id": "11", "twk": 100, "tiu": 120, "tkp": 180, "created_at": "2026-11-10T00:00:00Z"},
                {"id": "s2", "user_id": "1", "twk": 90, "tiu": 100, "tkp": 160, "created_at": "2026-11-09T00:00:00Z"}
            ]

            # Session state does not have filter_tahun_aktif set initially
            mock_st.session_state.get.return_value = None

            import main
            data = main.prepare_admin_data()

            self.assertIsNotNone(data)
            # Should have filtered to 2027 by default!
            df_users = data["df_users"]
            self.assertEqual(len(df_users[df_users["role"] == "user"]), 1)
            self.assertEqual(df_users[df_users["role"] == "user"].iloc[0]["nama"], "User Baru 2027")

            # Merged df scores should also only contain scores for 2027
            df_scores = data["df"]
            self.assertEqual(len(df_scores), 1)
            self.assertEqual(df_scores.iloc[0]["nama"], "User Baru 2027")

    def test_prepare_admin_data_respects_explicit_filter(self):
        import os
        os.environ["SUPABASE_URL"] = "http://localhost:54321"
        os.environ["SUPABASE_KEY"] = "testkey"

        with patch("main.fetch_all_users") as mock_users, \
             patch("main.fetch_all_scores") as mock_scores, \
             patch("main.st") as mock_st:

            mock_users.return_value = [
                {"id": str(i), "nama": f"User {i}", "role": "user", "tahun_aktif": 2026} for i in range(1, 11)
            ] + [
                {"id": "11", "nama": "User Baru 2027", "role": "user", "tahun_aktif": 2027}
            ]
            mock_scores.return_value = []

            # Admin explicitly selected 2026
            mock_st.session_state.get.return_value = 2026

            import main
            data = main.prepare_admin_data()

            self.assertIsNotNone(data)
            df_users = data["df_users"]
            self.assertEqual(len(df_users[df_users["role"] == "user"]), 10)

if __name__ == "__main__":
    unittest.main()
