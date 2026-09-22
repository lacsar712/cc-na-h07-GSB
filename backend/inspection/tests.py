from django.contrib.auth.models import Group, User
from django.test import TestCase

from inspection.models import Inspection
from inspection.rules import judge


class JudgeRulesTest(TestCase):
    def test_bright_but_three_degrees_off_is_bearing_failure(self):
        # 亮度充足，但偏角绝对值三度（超过两度限值）。
        verdict, note = judge(1400, 1200, 3.0)
        self.assertEqual((verdict, note), ("不合格", "方位偏差过大"))

    def test_negative_three_degrees_off_is_bearing_failure(self):
        verdict, note = judge(1400, 1200, -3.0)
        self.assertEqual((verdict, note), ("不合格", "方位偏差过大"))

    def test_dim_seed_still_fails_on_light(self):
        # 偏暗种子（LH-09：800 < 1200）结论必须仍是光强不足。
        verdict, note = judge(800, 1200, 0.2)
        self.assertEqual((verdict, note), ("不合格", "光强不足"))

    def test_in_limit_passes(self):
        self.assertEqual(judge(1400, 1200, 0.4), ("合格", "光强与方位均在限内"))


class CreateAndDetailFlowTest(TestCase):
    def setUp(self):
        group = Group.objects.create(name="inspector")
        user = User.objects.create_user(username="keeper", password="x")
        user.groups.add(group)
        self.client.force_login(user)

    def test_three_degree_submission_fails_and_detail_shows_angle(self):
        response = self.client.post(
            "/inspections/new/",
            {
                "aid_code": "LH-77",
                "measured_cd": "1400",
                "required_cd": "1200",
                "bearing_error_deg": "3.0",
            },
        )
        self.assertEqual(response.status_code, 302)
        row = Inspection.objects.get(aid_code="LH-77")
        self.assertEqual(row.bearing_error_deg, 3.0)
        self.assertEqual(row.verdict, "不合格")
        self.assertEqual(row.note, "方位偏差过大")

        detail = self.client.get(response["Location"])
        self.assertEqual(detail.status_code, 200)
        body = detail.content.decode()
        self.assertIn("方位偏差 3.0 度", body)
        self.assertIn("方位偏差过大", body)
        self.assertNotIn("方位角待复核", body)

    def test_dim_submission_still_light_insufficient(self):
        response = self.client.post(
            "/inspections/new/",
            {
                "aid_code": "LH-09",
                "measured_cd": "800",
                "required_cd": "1200",
                "bearing_error_deg": "0.2",
            },
        )
        self.assertEqual(response.status_code, 302)
        row = Inspection.objects.get(aid_code="LH-09")
        self.assertEqual((row.verdict, row.note), ("不合格", "光强不足"))
