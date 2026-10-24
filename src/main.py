import flet as ft
import httpx
from sizing import size_system

API_URL = "https://6adcce31fa5e73d4ab2db866.mockapi.io/outage_report"


def main(page: ft.Page):
    page.title = "Ndzilo Energy Portal"
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO

    # ---------- Solar calculator ----------
    bill_input = ft.TextField(
        label="Monthly electricity bill (R)",
        keyboard_type=ft.KeyboardType.NUMBER,
    )
    error = ft.Text("", color=ft.Colors.RED)
    result = ft.Text("")

    def calculate(e):
        error.value = ""
        result.value = ""
        try:
            bill = float(bill_input.value)
        except (TypeError, ValueError):
            error.value = "Please enter your bill as a number, for example 8000."
            page.update()
            return
        if bill <= 0 or bill > 500_000:
            error.value = "Please enter a bill between R1 and R500,000."
            page.update()
            return

        r = size_system(bill)
        result.value = (
            f"Estimated system size: {r['system_kwp']} kWp\n"
            f"Estimated monthly saving: R{r['monthly_saving']:,} ({r['saving_pct']}%)\n"
            f"Estimated install cost: R{r['install_cost']:,}\n"
            f"Payback: about {r['payback_years']} years\n"
            f"CO2 avoided: {r['co2_tonnes_year']} tonnes a year"
        )
        page.update()

    # ---------- Outage reports ----------
    suburb_input = ft.TextField(label="Suburb or area (for example Klarinet)")
    hour_input = ft.TextField(
        label="Hour the power went off (0-23)",
        keyboard_type=ft.KeyboardType.NUMBER,
    )
    duration_input = ft.TextField(
        label="How long it lasted (minutes)",
        keyboard_type=ft.KeyboardType.NUMBER,
    )
    report_msg = ft.Text("")
    reports_list = ft.Column()

    def load_reports():
        reports_list.controls.clear()
        try:
            resp = httpx.get(API_URL, timeout=10)
            resp.raise_for_status()
            data = resp.json()
        except Exception as ex:
            print("LOAD ERROR:", repr(ex))
            reports_list.controls.append(
                ft.Text(f"Could not load: {ex}", color=ft.Colors.RED)
            )
            page.update()
            return

        if not data:
            reports_list.controls.append(ft.Text("No reports yet."))
        for item in reversed(data[-5:]):
            reports_list.controls.append(
                ft.Text(
                    f"{item.get('suburb')} - around {item.get('hour')}:00 - "
                    f"{item.get('duration_mins')} min"
                )
            )
        page.update()

    def submit_report(e):
        report_msg.color = ft.Colors.RED
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

        report_msg.color = ft.Colors.GREEN
        report_msg.value = "Thank you. Your outage report was saved."
        suburb_input.value = ""
        hour_input.value = ""
        duration_input.value = ""
        load_reports()

    # ---------- Page layout ----------
    page.add(
        ft.Text("Ndzilo Energy Portal", size=26, weight=ft.FontWeight.BOLD),
        ft.Text("Find out what solar could save your business."),
        bill_input,
        ft.Button("Calculate", on_click=calculate),
        error,
        result,
        ft.Text("Estimates only. Get a quote from an installer.", size=12),
        ft.Divider(),
        ft.Text("Report a power outage", size=20, weight=ft.FontWeight.BOLD),
        ft.Text("No names or street addresses. Only the area and time."),
        suburb_input,
        hour_input,
        duration_input,
        ft.Button("Submit report", on_click=submit_report),
        report_msg,
        ft.Text("Latest reports", size=16, weight=ft.FontWeight.BOLD),
        reports_list,
    )
    load_reports()


ft.run(main)