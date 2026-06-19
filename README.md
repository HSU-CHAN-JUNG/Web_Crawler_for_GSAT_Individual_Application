# GSAT Individual Application - Standardized Percentile Scores (SPS) Crawler

This project is a Python-based web crawler designed to obtain the Standardized Percentile Scores (SPS) of the General Scholastic Ability Test (GSAT) for the individual application channel (個人申請). 

---

## 🛠️ Requirements & Dependencies

The required Python packages and their specific versions are listed in `requirements.txt`.  
To install them, run:
```bash
pip install -r requirements.txt
```
---

## 💡Information

The repository consists of three main crawler scripts, each utilizing different methods to fetch department data:

1. catching_by_selenium.py (Written in 2024)
    - Method: Uses the selenium package to automate browser behavior.

    - Feature: It specifically identifies whether Mathematics is included in the department's grading criteria.

    - Output: Saves data to an Excel file (typically named ---採計數學).

Note: Execution time is slower compared to the Requests-based approaches due to browser rendering, but it offers potential for expanding more complex interactive functions in the future.

2. catching_by_request.py
    - Method: Uses the requests package for fast HTTP requests (developed with the assistance of Gemini).

    - Feature: Identifies all GSAT subjects graded by the departments.

    - Output: Saves data to a CSV file (typically named Table.csv).

    - Note: Planned for future feature expansions.

3. catching_by_request_2.py
    - Method: Similar architecture to catching_by_request.py but uses a different logic to traverse department pages.

    - Output: Saves data to a CSV file (typically named Table_----.csv).

Technical Insights: catching_by_request vs catching_by_request_2
The key difference between the two Requests-based scripts lies in how they fetch the department list:

    - catching_by_request.py: Collects all explicit department codes beforehand.

    - catching_by_request_2.py: Leverages the serial number system of the departments. Since department codes follow a structured pattern (University Code + Ordinal Number), this script dynamically increments the numbers to fetch data.
---

## Release notes

```bash
git log
```
