from django.contrib.auth.models import Group, User
from django.test import TestCase

from inspection.models import Inspection
from inspection.rules import judge


class JudgeBearingTests(TestCase):
    def test_bearing_three_degrees_bright_is_bearing_failure(self):
        # 偏角三度、亮度充足：必须判方位偏差过大，不再被旁路判成合格
        verdict, note = judge(1400, 1200, 3.0)
        self.assertEqual(verdict, "不合格")
        self.assertEqual(note, "方位偏差过大")

    def test_dim_seed_still_light_failure(self):
        # 偏暗种子（光强不足、偏角在限内）：结论保持光强不足，不被本次修改改写
        verdict, note = judge(800, 1200, 0.2)
        self.assertEqual(verdict, "不合格")
        self.assertEqual(note, "光强不足")


class RegistrationAndDetailTests(TestCase):
    def setUp(self):
        group = Group.objects.create(name="inspector")
        self.user = User.objects.create_user(username="keeper", password="x")
        self.user.groups.add(group)
        self.client.force_login(self.user)

    def test_register_three_degrees_records_angle_and_bearing_failure(self):
        response = self.client.post(
            "/inspections/new/",
            {
                "aid_code": "LH-77",
                "measured_cd": "1400",
                "required_cd": "1200",
                "bearing_error_deg": "3",
            },
        )
        self.assertEqual(response.status_code, 302)
        row = Inspection.objects.get(aid_code="LH-77")
        # 提交的角度原样落库，未被旁路抹掉
        self.assertEqual(row.bearing_error_deg, 3.0)
        self.assertEqual(row.verdict, "不合格")
        self.assertEqual(row.note, "方位偏差过大")

    def test_detail_shows_bearing_angle(self):
        response = self.client.post(
            "/inspections/new/",
            {
                "aid_code": "LH-78",
                "measured_cd": "1400",
                "required_cd": "1200",
                "bearing_error_deg": "3",
            },
        )
        detail = self.client.get(response["Location"])
        self.assertEqual(detail.status_code, 200)
        body = detail.content.decode()
        self.assertIn("方位偏差 3.0 度", body)
        self.assertNotIn("方位角待复核", body)

    def test_register_dim_seed_keeps_light_failure(self):
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
        self.assertEqual(row.verdict, "不合格")
        self.assertEqual(row.note, "光强不足")
        detail = self.client.get(response["Location"])
        self.assertIn("方位偏差 0.2 度", detail.content.decode())
