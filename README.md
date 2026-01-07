📊 ServiceNow MTTR CalculatorA streamlined web dashboard built with Python and Streamlit to calculate Mean Time to Resolution (MTTR) from ServiceNow Excel exports.This tool applies a custom 8-hour logic (rounding up any resolution time over 8 hours to a full day) to match specific business reporting requirements.🚀 Version HistoryV2.0 (Latest Release)Executive HTML Reporting: Added "Download Executive Report" feature which generates a professional, auto-aligned HTML report with performance badges and trend visualizations.Smart Volume Thresholds: "Best Performers" now requires a minimum of 3 tickets handled to ensure statistical significance (prevents "1-hit wonders").Interactive Investigative Maps: Upgraded static charts to Plotly Interactive Trendlines with KPI target legends and detailed hover-data (Ticket ID/Group).Enhanced UI/UX: Added "Back to Selection" navigation and rounded performance metrics for cleaner dashboard viewing.Deployment Hardening: Standardized Docker environment and streamlined column mapping for all 5 modules.V1.0 (Initial Release)8-Hour Logic: Core conversion of timestamps into business-aligned "Calculated Days."Multi-Module Support: Specific mapping for Incidents, Requests, Changes, Feedback, and Surveys.Secure Access: Built-in password protection gatekeeper via environment variables.Dockerized: Fully containerized for one-command deployment.🛠️ Deployment Guide1. Clone the repositoryBashgit clone https://github.com/beanp02/mttr-calculator.git
cd mttr-calculator
2. Create your Secret KeyCreate a hidden file to hold your password. This keeps it safe and private:Bashnano .env
Type the following inside the file, then save and exit (Ctrl+O, Enter, Ctrl+X):PlaintextAPP_PASSWORD=YourChosenPasswordHere
3. Launch the AppBashdocker compose up -d --build
📂 Required Excel ColumnsThe ServiceNow export should contain headers that the app can automatically map, though you can manually adjust them in the settings:ModuleStart ColumnEnd ColumnIncidentCreatedResolved atRequestCreatedClosedChangeActual start dateActual end dateFeedbackStartEndSurveyTaken onAction completed🔒 Security NoteThis app uses an .env file to manage access. Never commit your .env file to GitHub. It is already included in the .gitignore to prevent accidental leaks.Final GitHub Push SequenceSince you've already confirmed testing is successful, run these commands to finalize the V2.0 release on your repository:Bash# 1. Update the local files
nano README.md  # (Paste the content above)

# 2. Add and Commit
git add README.md app.py requirements.txt
git commit -m "Release V2.0.0: Added Executive HTML Reporting and Plotly Analytics"

# 3. Create Release Tag
git tag -a v2.0.0 -m "V2.0 Production Build"

# 4. Push to GitHub
git push origin main
git push origin v2.0.0
