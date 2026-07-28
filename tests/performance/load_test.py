import threading
import time
import requests

URL = "http://127.0.0.1:8000/api/v1/screener?min_roe=15"

times = []

def worker(i):
    start = time.perf_counter()
    r = requests.get(URL)
    elapsed = time.perf_counter() - start
    print(f"Thread {i}: {r.status_code} ({elapsed:.3f}s)")
    times.append(elapsed)

threads = []

overall = time.perf_counter()

for i in range(10):
    t = threading.Thread(target=worker, args=(i,))
    t.start()
    threads.append(t)

for t in threads:
    t.join()

overall = time.perf_counter() - overall

print(f"\nTotal time: {overall:.3f} sec")
print(f"Average: {sum(times)/len(times):.3f} sec")
print(f"Max: {max(times):.3f} sec")