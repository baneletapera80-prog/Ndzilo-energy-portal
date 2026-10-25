# Ndzilo Energy Portal

Mobile-friendly web app that helps small businesses in Mpumalanga
estimate solar and battery needs and plan for power outages.

Built for the FNB App of the Year Hackathon 2026
(Climate Resilience and Essential Services). Team: Ndzilo Group.

## Features
- Solar calculator: monthly bill gives estimated system size, savings,
  payback and CO2 avoided
- Outage reporting saved to a cloud database (MockAPI)
- Outage insights: peak hours, most affected area, next likely outage
  window and suggested battery size (demo data is labelled as sample data)

All results are estimates, not quotes.

## Tech
Python, Flet, httpx, MockAPI (JSON)

## Run locally
    python -m venv .venv
    .venv\Scripts\activate
    pip install flet httpx
    flet run src\main.py

## Team
Ndzilo Group (Pty) Ltd, eMalahleni, Mpumalanga

## Live demo
https://ndzilo-energy-portal-1.onrender.com
(Free hosting: the first load can take about a minute to wake up.)
