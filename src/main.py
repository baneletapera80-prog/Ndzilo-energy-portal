import os
from datetime import datetime, timedelta, timezone

import flet as ft
import httpx

from analysis import analyse_reports
from sizing import size_battery, size_system

API_URL = "https://6adcce31fa5e73d4ab2db866.mockapi.io/outage_report"
SAST = timezone(timedelta(hours=2))

DARK = "#064E3B"
GREEN = "#0F7B42"
TEXT = "#111827"
MUTED = "#4B5563"
RED = "#B91C1C"


def tile(icon, label, value, bg, fg, note="", size=22):
    controls = [
        ft.Row(
            [ft.Icon(icon, color=fg, size=22), ft.Text(label, size=13, color=MUTED)],
            spacing=8,
        ),
        ft.Text(value, size=size, weight=ft.FontWeight.BOLD, color=TEXT),
    ]
    if note:
        controls.append(ft.Text(note, size=12, color=MUTED))
    return ft.Container(
        content=ft.Column(controls, spacing=4),
        padding=14,
        bgcolor=bg,
        border_radius=14,
        col={"xs": 6, "md": 4},
    )


def card(controls):
    return ft.Container(
        content=ft.Column(controls, spacing=12),
        padding=18,
        bgcolor="#FFFFFF",
        border_radius=18,
    )


def heading(icon, text):
    return ft.Row(
        [
            ft.Icon(icon, color=GREEN, size=26),
            ft.Text(text, size=20, weight=ft.FontWeight.BOLD, color=TEXT),
        ],
        spacing=10,
    )


def field(label, icon, value="", number=True):
    return ft.TextField(
        label=label,
        value=value,
        prefix_icon=icon,
        border_radius=14,
        filled=True,
        color=TEXT,
        keyboard_type=ft.KeyboardType.NUMBER if number else ft.KeyboardType.TEXT,
    )


def main(page: ft.Page):
    page.title = "Ndzilo Energy Portal"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#F1F5F2"
    page.padding = 12
    page.scroll = ft.ScrollMode.AUTO

    # ---------- Hero ----------
    hero = ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(ft.Icons.WB_SUNNY, color="#FDE68A", size=34),
                        ft.Text(
                            "Ndzilo Energy Portal",
                            size=26,
                            weight=ft.FontWeight.BOLD,
                            color="#FFFFFF",
                        ),
                    ],
                    spacing=10,
                ),
                ft.Text(
                    "Plan your solar and battery backup, and prepare for power outages.",
                    size=15,
                    color="#D1FAE5",
                ),
                ft.Text(
                    "Prototype for small businesses in Mpumalanga. Estimates only.",
                    size=12,
                    color="#A7F3D0",
                ),
            ],
            spacing=6,
        ),
        padding=22,
        bgcolor=DARK,
        border_radius=20,
    )

    # ---------- Calculator ----------
    bill_input = field("Monthly electricity bill (R)", ft.Icons.PAYMENTS)
    load_input = field("Essential load to keep running (kW)", ft.Icons.ELECTRIC_BOLT, "0.8")
    hours_input = field("Backup hours needed", ft.Icons.SCHEDULE, "4")
    calc_error = ft.Text("", color=RED)
    results_box = ft.Column()

    def calculate(e):
        calc_error.value = ""
        results_box.controls.clear()
        try:
            bill = float(bill_input.value)
        except (TypeError, ValueError):
            calc_error.value = "Please enter your bill as a number, for example 8000."
            page.update()
            return
        if bill <= 0 or bill > 500_000:
            calc_error.value = "Please enter a bill between R1 and R500,000."
            page.update()
            return
        try:
            load_kw = float(load_input.value)
            hours = float(hours_input.value)
            if load_kw > 100 or hours > 48:
                raise ValueError
            battery_kwh = size_battery(load_kw, hours)
        except (TypeError, ValueError):
            calc_error.value = (
                "Essential load must be above 0 and up to 100 kW, "
                "and backup hours above 0 and up to 48."
            )
            page.update()
            return

        r = size_system(bill)
        annual = r["monthly_saving"] * 12
        tiles = [
            tile(ft.Icons.WB_SUNNY, "Solar size", f"{r['system_kwp']} kWp",
                 "#DCFCE7", "#15803D"),
            tile(ft.Icons.SAVINGS, "Monthly saving", f"R{r['monthly_saving']:,}",
                 "#FEF3C7", "#B45309",
                 f"About {r['saving_pct']}% of your bill (R{annual:,} a year)"),
            tile(ft.Icons.PAYMENTS, "Install cost", f"R{r['install_cost']:,}",
                 "#FEE2E2", RED, "System only, no battery"),
            tile(ft.Icons.HOURGLASS_BOTTOM, "Payback", f"{r['payback_years']} years",
                 "#EDE9FE", "#6D28D9"),
            tile(ft.Icons.ECO, "CO2 avoided", f"{r['co2_tonnes_year']} t/year",
                 "#CCFBF1", "#0F766E"),
            tile(ft.Icons.BATTERY_CHARGING_FULL, "Battery", f"{battery_kwh} kWh",
                 "#E0F2FE", "#0369A1", f"{load_kw:g} kW for {hours:g} h"),
        ]
        results_box.controls.append(ft.Text("Your energy plan", size=17,
                                            weight=ft.FontWeight.BOLD, color=TEXT))
        results_box.controls.append(ft.ResponsiveRow(tiles, spacing=10, run_spacing=10))
        results_box.controls.append(
            ft.Text("Estimates only, based on standard assumptions. "
                    "Get a quote from an installer.", size=12, color=MUTED)
        )
        page.update()

    calc_card = card(
        [
            heading(ft.Icons.CALCULATE, "Solar and battery calculator"),
            ft.Text("Enter your monthly bill and what you must keep running during outages.",
                    size=13, color=MUTED),
            bill_input,
            load_input,
            hours_input,
            ft.Button("Calculate my results", icon=ft.Icons.CALCULATE,
                      bgcolor=GREEN, color="#FFFFFF", on_click=calculate),
            calc_error,
            results_box,
        ]
    )

    # ---------- Outage reports ----------
    suburb_input = field("Suburb or area (for example Klarinet)", ft.Icons.LOCATION_ON,
                         number=False)
    hour_input = field("Hour the power went off (0-23)", ft.Icons.SCHEDULE)
    duration_input = field("How long it lasted (minutes)", ft.Icons.TIMER)
    report_msg = ft.Text("")
    reports_list = ft.Column(spacing=6)
    insights_box = ft.Column()

    def show_insights(data):
        insights_box.controls.clear()
        s = analyse_reports(data, datetime.now(SAST).hour)
        if not s["enough_data"]:
            insights_box.controls.append(
                ft.Text(f"Not enough reports yet ({s['count']} of {s['needed']} needed).",
                        color=MUTED)
            )
            return
        peak = s["peak_hour"]
        tiles = [
            tile(ft.Icons.SCHEDULE, "Peak outage hour", f"{peak:02d}:00",
                 "#FEF3C7", "#B45309", f"{s['peak_count']} reports"),
            tile(ft.Icons.LOCATION_ON, "Most affected area", s["worst_suburb"],
                 "#FEE2E2", RED, f"{s['worst_count']} reports, about {s['worst_avg']} min",
                 size=15),
            tile(ft.Icons.TIMER, "Typical outage", f"{s['avg_duration']} min",
                 "#EDE9FE", "#6D28D9", f"Most last under {s['p80']} min"),
            tile(ft.Icons.POWER_OFF, "Next likely window",
                 f"{s['next_day'].capitalize()} {peak:02d}:00",
                 "#DCFCE7", "#15803D", "Estimate from past reports", size=18),
        ]
        try:
            load_kw = float(load_input.value)
            kwh = size_battery(load_kw, s["backup_hours"])
            tiles.append(
                tile(ft.Icons.BATTERY_CHARGING_FULL, "Suggested battery", f"{kwh} kWh",
                     "#E0F2FE", "#0369A1", f"{load_kw:g} kW for {s['backup_hours']} h")
            )
        except ValueError:
            pass
        insights_box.controls.append(ft.ResponsiveRow(tiles, spacing=10, run_spacing=10))
        insights_box.controls.append(
            ft.Text(f"Based on {s['count']} reports (includes sample data). "
                    "Insights are estimates.", size=12, color=MUTED)
        )

    def load_reports():
        reports_list.controls.clear()
        try:
            resp = httpx.get(API_URL, timeout=10)
            resp.raise_for_status()
            data = resp.json()
        except Exception as ex:
            print("LOAD ERROR:", repr(ex))
            reports_list.controls.append(ft.Text(f"Could not load: {ex}", color=RED))
            insights_box.controls.clear()
            page.update()
            return

        if not data:
            reports_list.controls.append(ft.Text("No reports yet.", color=MUTED))
        for item in reversed(data[-5:]):
            reports_list.controls.append(
                ft.Row(
                    [
                        ft.Icon(ft.Icons.POWER_OFF, size=16, color=MUTED),
                        ft.Text(
                            f"{item.get('suburb')} - around {item.get('hour')}:00 - "
                            f"{item.get('duration_mins')} min",
                            size=13,
                            color=TEXT,
                        ),
                    ],
                    spacing=8,
                )
            )
        show_insights(data)
        page.update()

    def submit_report(e):
        report_msg.color = RED
        suburb = (suburb_input.value or "").strip()
        if not suburb or len(suburb) > 50:
            report_msg.value = "Please enter a suburb (up to 50 characters)."
            page.update()
            return
        try:
            hour = int(hour_input.value)
            duration = int(duration_input.value)
        except (TypeError, ValueError):
            report_msg.value = "Hour and duration must be whole numbers."
            page.update()
            return
        if not 0 <= hour <= 23:
            report_msg.value = "Hour must be between 0 and 23."
            page.update()
            return
        if not 1 <= duration <= 1440:
            report_msg.value = "Duration must be between 1 and 1440 minutes."
            page.update()
            return

        try:
            resp = httpx.post(
                API_URL,
                json={"suburb": suburb, "hour": hour, "duration_mins": duration},
                timeout=10,
            )
            resp.raise_for_status()
        except Exception as ex:
            print("SAVE ERROR:", repr(ex))
            report_msg.value = f"Could not save: {ex}"
            page.update()
            return

        report_msg.color = GREEN
        report_msg.value = "Thank you. Your outage report was saved."
        suburb_input.value = ""
        hour_input.value = ""
        duration_input.value = ""
        load_reports()

    report_card = card(
        [
            heading(ft.Icons.POWER_OFF, "Report a power outage"),
            ft.Text("No names or street addresses. Only the area and time.",
                    size=13, color=MUTED),
            suburb_input,
            hour_input,
            duration_input,
            ft.Button("Submit report", icon=ft.Icons.SEND, bgcolor=GREEN,
                      color="#FFFFFF", on_click=submit_report),
            report_msg,
            ft.Text("Latest reports", size=15, weight=ft.FontWeight.BOLD, color=TEXT),
            reports_list,
        ]
    )

    insights_card = card(
        [
            heading(ft.Icons.INSIGHTS, "Outage insights"),
            ft.Text("What the reports say about when and where outages happen.",
                    size=13, color=MUTED),
            insights_box,
            ft.Button("Refresh insights", icon=ft.Icons.REFRESH,
                      on_click=lambda e: load_reports()),
        ]
    )

    # ---------- Page layout ----------
    body = ft.Column([hero, calc_card, report_card, insights_card], spacing=16)
    page.add(
        ft.ResponsiveRow(
            [ft.Container(content=body, col={"xs": 12, "md": 10, "lg": 8})],
            alignment=ft.MainAxisAlignment.CENTER,
        )
    )
    load_reports()


if __name__ == "__main__":
    ft.run(
        main,
        view=ft.AppView.WEB_BROWSER,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "8000")),
    )