# End-to-End Testing Report

## Summary

- Total scenarios: 10
- Passed: 10
- Failed: 0
- Overall result: PASS

## Scenario Results

| Scenario | Result | Response Time (ms) | Tools Used |
|---|---|---:|---|
| Document - Company Policy | PASS | 150.17 | DocumentSearch |
| Document - Annual Leave | PASS | 13.67 | DocumentSearch |
| Document - Sales Report | PASS | 14.55 | DocumentSearch |
| Unanswerable - Mars Weather | PASS | 8.44 | None |
| Unanswerable - CEO Favourite Colour | PASS | 7.14 | None |
| CRM - Customer C101 | PASS | 7.7 | CRMTool |
| CRM - Customer C102 | PASS | 8.2 | CRMTool |
| Order - O101 | PASS | 6.87 | OrderTool |
| Order - O102 | PASS | 8.97 | OrderTool |
| Email - Formal Draft | PASS | 7.57 | EmailDraft |

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
