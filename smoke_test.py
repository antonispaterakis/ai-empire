import time
import urllib.request
import json

base_url = "http://localhost:8000"

print("Starting smoke test...")

# 1. Start generation
print("Posting to /generate...")
req = urllib.request.Request(f"{base_url}/generate", data=json.dumps({"topic": "AI Agents in 2026"}).encode(), headers={'Content-Type': 'application/json'})
res = urllib.request.urlopen(req)
data = json.loads(res.read())
print("Response:", data)
task_id = data["task_id"]

# 2. Poll status
print(f"Polling status for task {task_id}...")
status = "PENDING"
while status not in ["SUCCESS", "FAILURE"]:
    time.sleep(2)
    s_req = urllib.request.Request(f"{base_url}/status/{task_id}")
    s_res = urllib.request.urlopen(s_req)
    s_data = json.loads(s_res.read())
    status = s_data["status"]
    print("Status:", status)

if status != "SUCCESS":
    print("Task failed:", s_data)
    exit(1)

print("Task successful:", s_data)

# 3. Check history file
print("Checking data/production_history.json...")
try:
    with open("data/production_history.json", "r") as f:
        history = json.load(f)
        last_entry = history[-1]
        print("Latest entry topic:", last_entry.get("topic"))
        print("Latest entry hook:", last_entry.get("hook"))
        print("Latest entry strategy_brief snippet:", last_entry.get("strategy_brief", "")[:50])
        print("Smoke test PASSED!")
except Exception as e:
    print("Smoke test FAILED on history check:", e)
    exit(1)
