"""
Unit tests for app.services.tariff_service.

These map to the manual test cases already documented in the thesis Testing
chapter (TAR-01, TAR-02, TAR-03) and turn them into real, automated,
isolated tests. tariff_service has no Flask/DB/API dependency, so it can be
tested as a pure function with no app context or fixtures required.
"""
import pytest
from app.services.tariff_service import calculate_bill, get_consumption_level, get_tier_label


# ---------------------------------------------------------------------------
# TAR-01: Consumption level badge matches predicted kWh
# ---------------------------------------------------------------------------
class TestConsumptionLevelBadge:

    @pytest.mark.parametrize("units, expected", [
        (0,   "Low"),
        (30,  "Low"),
        (60,  "Low"),       # upper boundary of Low, inclusive
        (61,  "Moderate"),  # first unit of Moderate
        (120, "Moderate"),
        (180, "Moderate"),  # upper boundary of Moderate, inclusive
        (181, "High"),      # first unit of High
        (500, "High"),
    ])
    def test_badge_matches_kwh(self, units, expected):
        assert get_consumption_level(units) == expected


# ---------------------------------------------------------------------------
# TAR-02: Bill calculated correctly for every schedule
# ---------------------------------------------------------------------------
class TestBillCalculatedPerSchedule:

    def test_schedule_1_low_partial_tier(self):
        # 20 units: entirely inside the first Low tier (0-30 @ Rs 5.00) + Rs 80 fixed
        assert calculate_bill(20) == pytest.approx(180.00)

    def test_schedule_1_low_crossing_tier(self):
        # 45 units: 30 @ Rs 5.00 + 15 @ Rs 9.00, fixed charge Rs 210 (31-60 band)
        assert calculate_bill(45) == pytest.approx(495.00)

    def test_schedule_1_low_upper_boundary(self):
        # 60 units: last unit still billed under Schedule 1
        assert calculate_bill(60) == pytest.approx(630.00)

    def test_schedule_2_mid_just_above_boundary(self):
        # 61 units: first unit of Schedule 2, fixed charge jumps to Rs 400
        assert calculate_bill(61) == pytest.approx(1260.00)

    def test_schedule_2_mid_upper_boundary(self):
        # 180 units: last unit still billed under Schedule 2, fixed charge Rs 1500
        assert calculate_bill(180) == pytest.approx(6420.00)

    def test_schedule_3_high_just_above_boundary(self):
        # 181 units: first unit of Schedule 3, fixed charge jumps to Rs 2500
        assert calculate_bill(181) == pytest.approx(8450.00)

    def test_bill_increases_monotonically_across_schedule_boundaries(self):
        # A basic sanity property: more consumption should never produce a cheaper bill,
        # even across a schedule change.
        samples = [0, 30, 60, 61, 90, 120, 180, 181, 250, 500]
        bills = [calculate_bill(u) for u in samples]
        assert bills == sorted(bills)


# ---------------------------------------------------------------------------
# TAR-03: Negative units handled safely
# ---------------------------------------------------------------------------
class TestNegativeUnitsHandledSafely:

    def test_calculate_bill_does_not_raise_on_negative_input(self):
        # Should not throw; negative consumption is clamped to 0 rather than crashing
        result = calculate_bill(-15)
        assert result == pytest.approx(80.00)  # same as 0 units: fixed charge only

    def test_calculate_bill_negative_equals_zero(self):
        assert calculate_bill(-1) == calculate_bill(0)

    def test_get_consumption_level_does_not_raise_on_negative_input(self):
        # Should not throw, and should not be classified as anything above "Low"
        assert get_consumption_level(-15) == "Low"


# ---------------------------------------------------------------------------
# TAR4: tier label boundaries (supports NFR-03's cross-check claim
# that boundary values match the PUCSL 2026 schedule exactly)
# ---------------------------------------------------------------------------
class TestTierLabelBoundaries:

    @pytest.mark.parametrize("units, expected", [
        (30,  "Tier 1 (0–30 units)"),
        (31,  "Tier 2 (31–60 units)"),
        (60,  "Tier 2 (31–60 units)"),
        (61,  "Tier 3 (61–90 units)"),
        (120, "Tier 4 (91–120 units)"),
        (180, "Tier 5 (121–180 units)"),
        (360, "Tier 6 (181–360 units)"),
        (361, "Tier 7 (360+ units)"),
    ])
    def test_tier_label_boundary(self, units, expected):
        assert get_tier_label(units) == expected
