def _generate_recommendations(data: dict, units: float, bill: float) -> list:
    recs = []

    ac_count          = data.get("ac_count", 0)
    ac_hours_per_month = data.get("ac_hours_per_month", 0)
    ac_hours_daily    = ac_hours_per_month / 30
    ac_tons           = data.get("ac_tons", 1.5)
    fan_count         = data.get("fan_count", 0)
    fridge_count      = data.get("fridge_count", 0)
    washer_hours      = data.get("washer_hours_per_month", 0)
    heater_hours      = data.get("heater_hours_per_month", 0)
    members           = data.get("members", 4)

    # ------------------------------------------------------------------
    # STEP 1 — Detect which schedule boundary the user is near
    # ------------------------------------------------------------------
    BOUNDARY_1 = 60    # Schedule 1 → Schedule 2
    BOUNDARY_2 = 180   # Schedule 2 → Schedule 3
    NEAR_THRESHOLD = 20  # within 20 kWh of a boundary = "near"

    if units <= BOUNDARY_1:
        gap = None  # already in lowest schedule, no boundary to chase
        target_boundary = None
    elif units <= BOUNDARY_1 + NEAR_THRESHOLD:
        gap = units - BOUNDARY_1
        target_boundary = BOUNDARY_1
    elif units <= BOUNDARY_2:
        gap = units - BOUNDARY_2 if units > BOUNDARY_2 else None
        target_boundary = BOUNDARY_2 if units > BOUNDARY_2 else None
    else:
        gap = units - BOUNDARY_2
        target_boundary = BOUNDARY_2

    # Recalculate what bill would be if they crossed the boundary
    if target_boundary and gap:
        reduced_units = units - gap - 1  # just under the boundary
        bill_if_reduced = calculate_bill(reduced_units)
        bill_saving_lkr = round(bill - bill_if_reduced, 2)
    else:
        gap = None
        bill_saving_lkr = 0
        target_boundary = None

    # ------------------------------------------------------------------
    # STEP 2 — Calculate reducible kWh per appliance
    # ------------------------------------------------------------------
    # AC: reduce to 6 hours/day max
    ac_reducible = 0.0
    if ac_count > 0 and ac_hours_daily > 6:
        ac_reducible = round(
            ac_count * (ac_hours_daily - 6) * ac_tons * 0.7 * 30, 1
        )

    # Water heater: cut usage by half
    heater_reducible = round(heater_hours * 0.5 * 1.5, 1) if heater_hours > 4 else 0.0

    # Washing machine: cut usage by half
    washer_reducible = round(washer_hours * 0.5 * 2.0, 1) if washer_hours > 8 else 0.0

    total_reducible = ac_reducible + heater_reducible + washer_reducible

    # ------------------------------------------------------------------
    # STEP 3 — Boundary-aware priority recommendation
    # ------------------------------------------------------------------
    if gap and target_boundary and bill_saving_lkr > 0:
        if total_reducible >= gap:
            # User CAN cross the boundary with habit changes
            actions = []
            remaining_gap = gap
            used_ac = used_heater = used_washer = 0.0

            if ac_reducible > 0 and remaining_gap > 0:
                used_ac = min(ac_reducible, remaining_gap)
                remaining_gap -= used_ac
                daily_reduction = round(used_ac / (ac_count * ac_tons * 0.7 * 30), 1)
                actions.append(
                    f"reduce AC by {daily_reduction} hrs/day (saves {round(used_ac, 1)} kWh)"
                )

            if heater_reducible > 0 and remaining_gap > 0:
                used_heater = min(heater_reducible, remaining_gap)
                remaining_gap -= used_heater
                actions.append(
                    f"cut water heater usage by half (saves {round(used_heater, 1)} kWh)"
                )

            if washer_reducible > 0 and remaining_gap > 0:
                used_washer = min(washer_reducible, remaining_gap)
                remaining_gap -= used_washer
                actions.append(
                    f"reduce washing machine usage by half (saves {round(used_washer, 1)} kWh)"
                )

            action_text = " and ".join(actions)
            recs.append({
                "title": f"Save LKR {bill_saving_lkr:,.0f} by dropping to a lower tariff schedule",
                "description": (
                    f"You are {round(gap, 1)} kWh above the {target_boundary} kWh CEB schedule "
                    f"boundary. Crossing it recalculates your entire bill at lower rates — saving "
                    f"LKR {bill_saving_lkr:,.0f} this month. To get there: {action_text}. "
                    f"No hardware changes needed, just usage adjustments."
                ),
                "category": "Tariff Boundary",
                "saving_kwh": round(gap + 1, 1),
                "saving_lkr": bill_saving_lkr,
                "icon": "plug",
                "priority": "high",
            })
        else:
            # User cannot fully cross but can still reduce significantly
            partial_saving = calculate_bill(units - total_reducible)
            partial_lkr = round(bill - partial_saving, 2)
            recs.append({
                "title": f"Reduce your bill by LKR {partial_lkr:,.0f} with simple habit changes",
                "description": (
                    f"You need to save {round(gap, 1)} kWh to drop to a lower CEB tariff schedule "
                    f"(saving LKR {bill_saving_lkr:,.0f}), but your current reducible usage is "
                    f"{round(total_reducible, 1)} kWh. While you may not cross the boundary this "
                    f"month, applying all habit changes below can still save LKR {partial_lkr:,.0f}."
                ),
                "category": "Tariff Boundary",
                "saving_kwh": round(total_reducible, 1),
                "saving_lkr": partial_lkr,
                "icon": "plug",
                "priority": "high",
            })

    # ------------------------------------------------------------------
    # STEP 4 — Individual appliance recommendations
    # ------------------------------------------------------------------
    if ac_count > 0 and ac_hours_daily > 6:
        recs.append({
            "title": "Reduce AC usage hours",
            "description": (
                f"Your AC runs {ac_hours_daily:.0f} hrs/day. Reducing to 6 hrs/day saves "
                f"~{ac_reducible} kWh/month. In Colombo's climate, switching the AC off "
                f"at night and using a ceiling fan instead is the single most impactful "
                f"habit change for your bill."
            ),
            "category": "Air Conditioner",
            "saving_kwh": ac_reducible,
            "saving_lkr": round(bill - calculate_bill(units - ac_reducible), 2),
            "icon": "ac",
            "priority": "high" if ac_reducible >= 10 else "medium",
        })

    if ac_count > 0:
        thermostat_saving = round(ac_count * ac_hours_daily * 0.18 * 30, 1)
        recs.append({
            "title": "Set AC thermostat to 24°C",
            "description": (
                "Each degree below 24°C increases energy use by about 6%. Setting your "
                "AC to 24°C instead of 18°C can cut AC electricity costs by up to 36% "
                "— no hardware change needed, just a setting adjustment."
            ),
            "category": "Air Conditioner",
            "saving_kwh": thermostat_saving,
            "saving_lkr": round(bill - calculate_bill(units - thermostat_saving), 2),
            "icon": "temperature",
            "priority": "medium",
        })

    if ac_count > 0 and fan_count > 0:
        fan_saving = round(ac_count * ac_hours_daily * 0.12 * 30, 1)
        recs.append({
            "title": "Use ceiling fan with AC at higher temperature",
            "description": (
                "Running a ceiling fan alongside the AC lets you set the thermostat "
                "2–3°C higher while feeling equally cool. A fan uses only 60W compared "
                "to 1,000W+ for an AC — one of the most cost-effective habits for "
                "Colombo households."
            ),
            "category": "Air Conditioner",
            "saving_kwh": fan_saving,
            "saving_lkr": round(bill - calculate_bill(units - fan_saving), 2),
            "icon": "fan",
            "priority": "medium",
        })

    if ac_count > 0:
        filter_saving = round(ac_count * ac_hours_daily * ac_tons * 0.7 * 0.1 * 30, 1)
        recs.append({
            "title": "Clean AC filters monthly",
            "description": (
                "Dirty AC filters increase electricity use by 5–15%. Cleaning takes "
                "10 minutes and costs nothing — especially important in Colombo's "
                "dusty urban environment."
            ),
            "category": "Air Conditioner",
            "saving_kwh": filter_saving,
            "saving_lkr": round(bill - calculate_bill(units - filter_saving), 2),
            "icon": "ac",
            "priority": "low",
        })

    if heater_hours > 4:
        recs.append({
            "title": "Switch water heater on only before use",
            "description": (
                f"Switch the heater on 15–20 minutes before use instead of leaving "
                f"it on all day. This can save ~{heater_reducible} kWh/month at no cost."
            ),
            "category": "Water Heater",
            "saving_kwh": heater_reducible,
            "saving_lkr": round(bill - calculate_bill(units - heater_reducible), 2),
            "icon": "heater",
            "priority": "high" if heater_reducible >= 10 else "medium",
        })

    if washer_hours > 8:
        recs.append({
            "title": "Wash with full loads only",
            "description": (
                "Running the washing machine with full loads reduces the number of "
                "cycles needed. In Sri Lanka, washing with cold water also saves "
                "significantly as water heating accounts for a large portion of "
                "washer energy use."
            ),
            "category": "Washing Machine",
            "saving_kwh": washer_reducible,
            "saving_lkr": round(bill - calculate_bill(units - washer_reducible), 2),
            "icon": "washer",
            "priority": "medium",
        })

    if fridge_count >= 1:
        fridge_saving = round(fridge_count * 0.15 * 24 * 0.1 * 30, 1)
        recs.append({
            "title": "Keep fridge away from heat sources",
            "description": (
                "Placing the fridge away from direct sunlight or the stove improves "
                "efficiency by up to 15%. Also check door seals are tight — a loose "
                "seal wastes electricity continuously."
            ),
            "category": "Refrigerator",
            "saving_kwh": fridge_saving,
            "saving_lkr": round(bill - calculate_bill(units - fridge_saving), 2),
            "icon": "fridge",
            "priority": "low",
        })

    if fridge_count >= 2:
        recs.append({
            "title": "Consider running only one refrigerator",
            "description": (
                "Each additional fridge consumes approximately 108 kWh/month. "
                "At higher CEB tariff schedules this can add LKR 4,000–8,000 "
                "to your bill. Unplugging a second fridge during low-usage months "
                "is an easy saving."
            ),
            "category": "Refrigerator",
            "saving_kwh": 108.0,
            "saving_lkr": round(bill - calculate_bill(units - 108.0), 2),
            "icon": "fridge",
            "priority": "medium",
        })

    # ------------------------------------------------------------------
    # STEP 5 — General habits
    # ------------------------------------------------------------------
    led_saving = round(members * 0.25 * 30, 1)
    recs.append({
        "title": "Switch all bulbs to LED",
        "description": (
            f"LED bulbs use 75% less electricity than incandescent bulbs. Replacing "
            f"5 bulbs saves approximately {led_saving} kWh/month. LED bulbs are "
            f"available at LKR 200–400 each and pay for themselves within 1–2 months."
        ),
        "category": "Lighting",
        "saving_kwh": led_saving,
        "saving_lkr": round(bill - calculate_bill(units - led_saving), 2),
        "icon": "bulb",
        "priority": "low",
    })

    standby_saving = round(units * 0.08, 1)
    recs.append({
        "title": "Unplug devices not in use",
        "description": (
            "Televisions, phone chargers, microwaves, and set-top boxes consume "
            "electricity even on standby. In a typical Colombo household, standby "
            "power accounts for 8–10% of the total bill."
        ),
        "category": "General",
        "saving_kwh": standby_saving,
        "saving_lkr": round(bill - calculate_bill(units - standby_saving), 2),
        "icon": "plug",
        "priority": "low",
    })

    # Sort by priority: high first, then medium, then low
    priority_order = {"high": 0, "medium": 1, "low": 2}
    recs.sort(key=lambda r: priority_order.get(r.get("priority", "low"), 2))

    return recs