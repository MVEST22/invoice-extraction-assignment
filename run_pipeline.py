import subprocess,sys
steps=[
 [sys.executable,'methods/method1_programmatic.py'],
 [sys.executable,'methods/method2_low_cost.py'],
 [sys.executable,'methods/method3_expensive.py'],
 [sys.executable,'evaluation/compare_results.py'],
 [sys.executable,'methods/method4_refined.py'],
 [sys.executable,'evaluation/compare_results.py'],
 [sys.executable,'scripts/calculate_costs.py'],
 [sys.executable,'scripts/build_db.py'],
 [sys.executable,'scripts/build_report.py'],
]
for step in steps:
 print('>', ' '.join(step)); subprocess.run(step,check=True)
