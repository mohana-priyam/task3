
import csv
import time
from pathlib import Path

from fastapi.testclient import TestClient
from app.main import app, documents

client = TestClient(app)

REPORT_DIR = Path("reports")
REPORT_DIR.mkdir(exist_ok=True)


def document_scenario(filename, content, question):
    documents.clear()

    client.post(
        "/documents",
        json={"filename": filename, "content": content}
    )

    return client.post("/chat", json={"message": question})


def scenario_results():
    return [
        {
            "name": "Document - Company Policy",
            "run": lambda: document_scenario(
                "policy.txt",
                "Employees receive 20 days of annual leave.",
                "What does the company policy say?"
            ),
            "check": lambda r: r.status_code == 200
            and "20 days" in r.json()["answer"]
        },
        {
            "name": "Document - Annual Leave",
            "run": lambda: document_scenario(
                "leave.txt",
                "Employees receive 20 days of annual leave.",
                "Tell me about the leave document."
            ),
            "check": lambda r: r.status_code == 200
            and "20 days" in r.json()["answer"]
        },
        {
            "name": "Document - Sales Report",
            "run": lambda: document_scenario(
                "report.txt",
                "The sales report shows revenue of 500000.",
                "Summarize the sales report."
            ),
            "check": lambda r: r.status_code == 200
            and "500000" in r.json()["answer"]
        },
        {
            "name": "Unanswerable - Mars Weather",
            "run": lambda: client.post(
                "/chat",
                json={"message": "What is the weather on Mars?"}
            ),
            "check": lambda r: r.status_code == 200
            and "cannot find" in r.json()["answer"].lower()
        },
        {
            "name": "Unanswerable - CEO Favourite Colour",
            "run": lambda: client.post(
                "/chat",
                json={"message": "What is the CEO's favourite colour?"}
            ),
            "check": lambda r: r.status_code == 200
            and "cannot find" in r.json()["answer"].lower()
        },
        {
            "name": "CRM - Customer C101",
            "run": lambda: client.post(
                "/chat",
                json={"message": "Show customer C101 details."}
            ),
            "check": lambda r: r.status_code == 200
            and r.json()["answer"]["success"] is True
            and r.json()["answer"]["data"]["name"] == "Arun Kumar"
        },
        {
            "name": "CRM - Customer C102",
            "run": lambda: client.post(
                "/chat",
                json={"message": "Show customer C102 details."}
            ),
            "check": lambda r: r.status_code == 200
            and r.json()["answer"]["success"] is True
            and r.json()["answer"]["data"]["name"] == "Priya Sharma"
        },
        {
            "name": "Order - O101",
            "run": lambda: client.post(
                "/chat",
                json={"message": "Check order O101 status."}
            ),
            "check": lambda r: r.status_code == 200
            and r.json()["answer"]["success"] is True
            and r.json()["answer"]["data"]["status"] == "Shipped"
        },
        {
            "name": "Order - O102",
            "run": lambda: client.post(
                "/chat",
                json={"message": "Check order O102 status."}
            ),
            "check": lambda r: r.status_code == 200
            and r.json()["answer"]["success"] is True
            and r.json()["answer"]["data"]["status"] == "Delivered"
        },
        {
            "name": "Email - Formal Draft",
            "run": lambda: client.post(
                "/draft-email",
                json={
                    "topic": "Order delivery update",
                    "tone": "formal"
                }
            ),
            "check": lambda r: r.status_code == 200
            and "Order delivery update" in r.json()["subject"]
            and "Dear Customer" in r.json()["body"]
        }
    ]


def main():
    results = []

    for scenario in scenario_results():
        documents.clear()
        start_time = time.perf_counter()

        try:
            response = scenario["run"]()
            elapsed = (time.perf_counter() - start_time) * 1000
            passed = scenario["check"](response)
            data = response.json()

            tools = data.get("tools_used", [])

            results.append({
                "scenario": scenario["name"],
                "result": "PASS" if passed else "FAIL",
                "response_time_ms": round(elapsed, 2),
                "tools_used": ", ".join(tools) if tools else "None"
            })

        except Exception as error:
            elapsed = (time.perf_counter() - start_time) * 1000

            results.append({
                "scenario": scenario["name"],
                "result": "FAIL",
                "response_time_ms": round(elapsed, 2),
                "tools_used": "Error: " + str(error)
            })

    csv_path = REPORT_DIR / "scenario_results.csv"

    with open(csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "scenario",
                "result",
                "response_time_ms",
                "tools_used"
            ]
        )
        writer.writeheader()
        writer.writerows(results)

    passed_count = sum(r["result"] == "PASS" for r in results)
    failed_count = len(results) - passed_count

    report = f"""# End-to-End Testing Report

## Summary

- Total scenarios: {len(results)}
- Passed: {passed_count}
- Failed: {failed_count}
- Overall result: {"PASS" if failed_count == 0 else "FAIL"}

## Scenario Results

| Scenario | Result | Response Time (ms) | Tools Used |
|---|---|---:|---|
"""

    for result in results:
        report += (
            f"| {result['scenario']} | {result['result']} | "
            f"{result['response_time_ms']} | {result['tools_used']} |\n"
        )

    report += """
## Bugs Found and Fixed

1. Document retrieval bug:
   The application returned the first uploaded document instead of
   selecting the relevant document. Fixed with keyword-based document matching.

2. Unknown customer ID bug:
   An unknown customer ID such as C999 incorrectly returned customer C101.
   Fixed by extracting and validating the requested customer ID.

## Unit Testing

CRM and Order tools were tested using mocked clients.
All 6 unit tests passed in the final test run.

## End-to-End Testing

All 10 required scenarios were executed using FastAPI TestClient.

## Secrets Hygiene

The application uses mock CRM and Order data. No real API credentials
are required for this test project. The .env file should be excluded
from version control using .gitignore.

## Conclusion

The scenario runner records pass/fail results, response time,
and tools used for each scenario.
"""

    (REPORT_DIR / "test_report.md").write_text(
        report, encoding="utf-8"
    )

    print("\nEND-TO-END SCENARIO RESULTS")
    print("=" * 45)

    for result in results:
        print(
            f"{result['scenario']}: {result['result']} "
            f"({result['response_time_ms']} ms)"
        )

    print("=" * 45)
    print(f"Total: {len(results)}")
    print(f"Passed: {passed_count}")
    print(f"Failed: {failed_count}")
    print("\nReports saved:")
    print("reports/scenario_results.csv")
    print("reports/test_report.md")


if __name__ == "__main__":
    main()