# Sprint 1 Retrospective

## Sprint Goal

Build the data foundation for the Nifty 100 Financial Intelligence Platform by loading all core and supporting datasets into SQLite, validating data quality, and preparing the project for KPI development.

---

## What Went Well

- Project structure and ETL pipeline were successfully established.
- All 12 datasets were loaded into SQLite.
- Data normalization for company IDs and year fields was implemented.
- Duplicate and orphan records were handled during loading.
- Load audit reporting was generated successfully.
- Data quality review was completed for five randomly selected companies.
- No critical data quality issues were identified.

---

## Challenges Encountered

- Initial loader audit statistics required debugging.
- Coverage differences between source datasets required investigation.
- One company (SBIN) showed missing balance sheet records, which was traced back to source data rather than a loader issue.

---

## Key Learnings

- Source data coverage can vary across financial statement datasets.
- Audit logging is useful for validating ETL results and identifying rejected records.
- Manual data quality reviews help verify that automated checks are working correctly.

---

## Sprint 1 Deliverables Completed

- SQLite database (nifty100.db)
- Database schema
- ETL loader
- Data quality validation
- Load audit report
- Data quality review notes
- Exploratory SQL queries

---

## Improvements for Sprint 2

- Expand automated validation checks where possible.
- Begin KPI computation with formula validation against source data.
- Increase test coverage for financial calculations.

---

## Sprint Status

Sprint 1 completed successfully and ready for Sprint 2.