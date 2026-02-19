import os
from dotenv import load_dotenv
load_dotenv()

from app.services.report import report_service

print("Testing Report Service...")
species_name = "Tiger"
species_data = {
    "status": "Endangered",
    "estimated_population": 3700,
    "biological_traits": {"kingdom": "Animalia", "class": "Mammalia"},
    "population_history": [{"year": "2024", "count": 3700}]
}
env_context = {
    "risk_score": 0.3,
    "avg_ndvi": 0.6,
    "avg_temp": 28,
    "avg_rain": 1200,
    "hdi": 0.4
}
conservation_plan = [{"action_type": "Protection", "description": "Protect habitat"}]

print("Generating LLM Report...")
report = report_service.generate_llm_report(species_name, species_data, env_context, conservation_plan)
print("-" * 20)
print(report)
print("-" * 20)

if "Offline" in report:
    print("FAILURE: Report is offline (check API key)")
else:
    print("SUCCESS: Report generated")

print("Generating PDF...")
pdf_path = report_service.generate_pdf_report(species_name, report)
if pdf_path:
    print(f"SUCCESS: PDF generated at {pdf_path}")
else:
    print("FAILURE: PDF generation failed")
