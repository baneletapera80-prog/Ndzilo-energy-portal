import flet as ft
from sizing import size_system


def main(page: ft.Page):
    page.title = "Ndzilo Energy Portal"
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO

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

    page.add(
        ft.Text("Ndzilo Energy Portal", size=26, weight=ft.FontWeight.BOLD),
        ft.Text("Find out what solar could save your business."),
        bill_input,
        ft.Button("Calculate", on_click=calculate),
        error,
        result,
        ft.Text("Estimates only. Get a quote from an installer.", size=12),
    )


ft.run(main)