import os, subprocess, sys
model=os.getenv("EXPENSIVE_MODEL","gpt-6.1-sol")
subprocess.run([sys.executable, "methods/llm_extract.py", model, "method3_expensive.csv", "method3_expensive_usage.json"], check=True)
