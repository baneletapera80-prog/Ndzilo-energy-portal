import math

# ASSUnPTIONS  replace with real values (installer.quote, municipal bill)
ELECTRICITY_TARIFF = 3.10    # R per kWh
KWH_PER_KWP_MONTH = 125      # solar yield; about 1500 kWh per kWp per year
DAYTIME_SHARE = 0.60         # share of usage during daylight hours
SELF_USE = 0.85              # share of solar power used on site
COST_PER_KWP = 13750         # R per kWp installed.no battery
CO2_KG_PER_KWH = 0.95        # grid emission factor


def size_system(monthly_bill, tariff=ELECTRICITY_TARIFF):
    """Estimate solar size, savings, payback and CO2 from a monthly bill (R)."""
    if monthly_bill <= 0:
        raise ValueError("the monthly bill must be a positive value.")

    monthly_kwh = monthly_bill / tariff
    daytime_kwh = monthly_kwh * DAYTIME_SHARE
    solar_kwp = max(1, math.floor(daytime_kwh / KWH_PER_KWP_MONTH))

    used_kwh = solar_kwp * KWH_PER_KWP_MONTH * SELF_USE
    monthly_saving = used_kwh * tariff
    install_cost = solar_kwp * COST_PER_KWP

    return {
        "monthly_kwh": round(monthly_kwh),
        "system_kwp": solar_kwp,
        "monthly_saving": round(monthly_saving),
        "saving_pct": round(monthly_saving / monthly_bill * 100),
        "install_cost": install_cost,
        "payback_years": round(install_cost / (monthly_saving * 12), 1),
        "co2_tonnes_year": round(used_kwh * 12 * CO2_KG_PER_KWH / 1000, 1),
    }


def size_battery(critical_load_kw, backup_hours, usable_fraction=0.8):
    """Estimate battery capacity needed for essential loads."""
    if critical_load_kw <= 0:
        raise ValueError("Critical load must be positive.")
    if backup_hours <= 0:
        raise ValueError("Backup hours must be positive.")
    if not 0 < usable_fraction <= 1:
        raise ValueError("Usable fraction must be above 0 and at most 1.")

    return round(
        critical_load_kw * backup_hours / usable_fraction, 1
    )


def main():
    print("NDZILO ENERGY SOLUTIONS")
    print("=" * 45)

    for bill in (3000, 8000, 25000):
        result = size_system(bill)
        print(f"\nMonthly bill: R{bill:,.2f}")
        print(f"Estimated monthly consumption: {result['monthly_kwh']} kWh")
        print(f"Estimated solar capacity: {result['system_kwp']} kWp")
        print(f"Estimated monthly saving: R{result['monthly_saving']:,} ({result['saving_pct']}%)")
        print(f"Estimated install cost: R{result['install_cost']:,}")
        print(f"Estimated payback: {result['payback_years']} years")
        print(f"CO2 avoided: {result['co2_tonnes_year']} tonnes/year")
        print("-" * 45)

    # Fridge, lights and card machine: about 0.8 kW for 4 hours
    print(f"\nBattery for 0.8 kW over 4 hours: {size_battery(0.8, 4)} kWh")


if __name__ == "__main__":
    main()