# Performance Notes

## Load Test

• 10 concurrent API requests completed in 2.18 seconds.

• Average response time:
0.21 sec

• Maximum response time:
0.42 sec

---

## Dashboard

Company Profile page

TCS
0.39 sec

INFY
0.44 sec

ITC
0.36 sec

HDFCBANK
0.41 sec

RELIANCE
0.47 sec

All below required threshold (3 sec).

---

## Bottlenecks

No major bottlenecks observed.

Potential optimisation:

• Cache latest KPI queries.

• Add indexes.

• Cache Streamlit API calls.

• Enable gzip compression if deployed.