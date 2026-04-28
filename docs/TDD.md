Technical Design Document: Q-Help

1. Project Purpose
Q-Help is a multi-source data intelligence tool designed to bridge the gap between IT Asset Management (ITAM), Service Desk operations, and Financial Planning. By correlating asset data from GLPI with ticket history from Spiceworks, the tool identifies hardware failure patterns, calculates depreciation, and generates a predictive replacement roadmap to support executive decision-making.

2. Technical Glossary
ETL (Extract, Transform, Load): The process of retrieving data from GLPI and Spiceworks, cleaning it via Python, and outputting a structured report.
Data Correlation: Linking two different databases (Inventory and Tickets) using a unique identifier (Serial Number or Hostname).
Data Sanitization: Automated identification and correction of "dirty data" (e.g., mismatched serial numbers or impossible dates).
Asset Depreciation: The systematic reduction in hardware value over time, used to trigger proactive budget alerts.
MTBF (Mean Time Between Failures): A KPI derived from Spiceworks data to identify underperforming hardware models.
Dockerization: Packaging Q-Help into a container for consistent execution across any environment.
Cloud Integration (Google Sheets API): Connecting the Python backend to Google Workspace for real-time stakeholder dashboards.

3. Project Roadmap (Phases of Execution)
Phase 1: Data Discovery & Multi-Source Mapping (Product & QA Focus)
Objective: Define the "Source of Truth" by merging two disconnected datasets.
Action: Create a mapping logic to correlate Spiceworks support requests (Created By(Email), Summary) with the GLPI hardware inventory (Usuário, Localização, Purchase Date), solving the lack of direct hardware identification in the ticketing system.
QA Constraint: Implement a "Cross-Reference Validation" layer to flag tickets that cannot be linked to any known asset in the official inventory.
Phase 2: The Q-Help Correlation Engine (Development Focus)
Objective: Build Python logic to calculate a "Hardware Reliability Score."
Core Logic:
$RemainingLife = ExpectedLifespan - (CurrentDate - PurchaseDate)$
Reliability Score: Weighted calculation based on Frequency of Tickets vs Asset Age.
Tech Stack: Python, Pandas (for merging and analyzing large datasets).
Phase 3: Business Intelligence & Graphical Insights (Product Focus)
Objective: Translate technical correlations into visual executive insights.
Output: Graphical reports highlighting "Maintenance Cost vs. Age" and "Top Failure-Prone Models."
Value: Provides evidence-based justification for hardware procurement, showing exactly which brands are costing more in support hours.
Phase 4: Deployment & CI/CD (DevOps Focus)
Objective: Ensure the tool is portable, reliable, and production-ready.
Action: Create a Dockerfile and docker-compose setup.
Automation: Use GitHub Actions to run automated tests (Pytest) to ensure the correlation logic remains accurate after code changes.
Phase 5: Cloud Integration & Live Dashboarding (Project Focus)
Objective: Automate delivery to non-technical stakeholders.
Action: Use Google Sheets API to push the analyzed data into the Director's existing reporting spreadsheets.
Impact: Replaces manual CSV manipulation with an automated, graphical, and live data stream.