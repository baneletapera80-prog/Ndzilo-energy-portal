import random

import httpx

URL = "https://6adcce31fa5e73d4ab2db866.mockapi.io/outage_report"

records = httpx.get(URL, timeout=10).json()
print("Deleting", len(records), "records...")
for rec in records:
    r = httpx.delete(f"{URL}/{rec['id']}", timeout=10)
    if r.status_code != 200:
        print("Delete problem:", rec["id"], r.status_code)

random.seed(7)
SUBURBS = [
    "Klarinet (sample)",
    "Reyno Ridge (sample)",
    "Tasbet Park (sample)",
    "Del Judor (sample)",
]
HOURS = [6, 7, 12, 17, 18, 18, 19, 19, 19, 20]

for i in range(24):
    record = {
        "suburb": random.choice(SUBURBS),
        "hour": random.choice(HOURS),
        "duration_mins": random.randint(30, 150),
    }
    r = httpx.post(URL, json=record, timeout=10)
    if r.status_code != 201:
        print("Save problem:", r.status_code, record)

print("Now in database:", len(httpx.get(URL, timeout=10).json()))