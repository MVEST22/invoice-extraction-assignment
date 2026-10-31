import os, subprocess, sys
model=os.getenv("LOW_COST_MODEL","gpt-6-luna")
subprocess.run([sys.executable, "methods/llm_extract.py", model, "method2_low_cost.csv", "method2_low_cost_usage.json"], check=True)
