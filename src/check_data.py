import httpx
from analysis import clean

URL = "https://6adcce31fa5e73d4ab2db866.mockapi.io/outage_report"

data = httpx.get(URL, timeout=10).json()
print("Total in database:", len(data))
print("Passed cleaning:", len(clean(data)))
print("First record:", data[0])
print("Last record:", data[-1])