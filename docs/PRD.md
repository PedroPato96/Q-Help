Product Requirements Document (PRD): Q-Help

1. Executive Summary & Problem Statement
Currently, IT support operations and IT asset management exist in data silos. The Service Desk (Spiceworks) tracks agent performance and ticket resolution times, while the Asset Inventory (GLPI) tracks hardware age and specifications. Management reporting is currently limited to static, operational PDFs focusing primarily on agent metrics rather than asset health.
This disconnect prevents the IT Board from identifying which specific hardware models are causing the highest maintenance overhead. Q-Help solves this by correlating support requests with inventory data, creating a predictive intelligence tool that shifts the department's strategy from reactive troubleshooting to proactive lifecycle management.

2. Product Vision & Goals
Vision: To provide the IT Directorate with an automated, evidence-based dashboard that predicts hardware failures before they impact school operations.
Business Goal 1: Reduce overall support hours spent on legacy hardware by identifying the exact "Technical Debt" threshold (the point where maintaining an asset costs more than replacing it).
Business Goal 2: Replace the legacy monthly PDF reporting system with a dynamic, automated Cloud Dashboard (Google Sheets) updated in near real-time.

3. Target Audience (Stakeholders)
IT Director / Board: Primary consumers of the final dashboard. They need financial justification (ROI and Cost of Ownership) to approve hardware procurement budgets.
IT Support Team: Contributors and secondary consumers. They need to know if a machine assigned to a ticket has a historical pattern of failure to decide between repairing or replacing it.

4. User Stories
US01: As an IT Director, I want to view a ranked list of hardware models that generate the most support tickets, so that I can avoid purchasing unreliable brands in the next fiscal cycle.
US02: As an IT Director, I want to see the total hours spent fixing machines older than 4 years, so that I can calculate the hidden cost of delayed hardware replacement.
US03: As an IT Support Analyst, I want the monthly reporting process to be fully automated, so that the team saves hours of manual data extraction and PDF generation.

5. Success Metrics (KPIs)
Reporting Automation Rate: 100% elimination of manual CSV exports and PDF compiling for monthly infrastructure meetings.
Cost Avoidance: Identifiable reduction in MTTR (Mean Time To Resolution) by phasing out the top 10% most problematic assets flagged by Q-Help.

6. Out of Scope (For MVP)
Q-Help will not automatically create purchase orders.
Q-Help will not alter or delete any data within the GLPI or Spiceworks databases (Read-only extraction).
