# 📊 ServiceNow MTTR Calculator

A streamlined web dashboard built with Python and Streamlit to calculate Mean Time to Resolution (MTTR) from ServiceNow Excel exports.

This tool applies a custom **8-hour logic** (rounding up any resolution time over 8 hours to a full day) to match specific business reporting requirements.

## 🚀 Features
* **Multi-Module Support**: Specific mapping for Incidents, Requests, Changes, Feedback, and Surveys.
* **Automated Logic**: Converts ServiceNow timestamps into business-aligned "Calculated Days."
* **Visual Analytics**: Interactive trendlines showing resolution speed over time.
* **Secure Access**: Built-in password protection gatekeeper via environment variables.
* **Dockerized**: Fully containerized for one-command deployment.

---

## 🛠️ Deployment Guide

### 1. Clone the repository
```bash
git clone [https://github.com/beanp02/mttr-calculator.git](https://github.com/beanp02/mttr-calculator.git)
cd mttr-calculator
2. Create your Secret KeyCreate a hidden file to hold your password. This keeps it safe and private:Bashnano .env
Type the following inside the file, then save and exit (Ctrl+O, Enter, Ctrl+X):PlaintextAPP_PASSWORD=YourChosenPasswordHere
3. Launch the AppBashdocker compose up -d --build
📂 Required Excel ColumnsThe ServiceNow export must contain these specific headers:ModuleStart ColumnEnd ColumnIncidentCreatedResolved atRequestCreatedClosedChangeActual start dateActual end dateFeedbackStartEndSurveyTaken onAction completed🔒 Security NoteThis app uses an .env file to manage access. Never commit your .env file to GitHub. It is already included in the .gitignore to prevent accidental leaks.
