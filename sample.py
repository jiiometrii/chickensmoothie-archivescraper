import requests
try:
    page = requests.get("https://www.chickensmoothie.com/archive/2024/December/", timeout=2.50)
except Exception as e:
    print('Encountered error:', e)