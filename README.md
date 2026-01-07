# 📊 ServiceNow MTTR Calculator

A streamlined web dashboard built with Python and Streamlit to calculate **Mean Time to Resolution (MTTR)** from ServiceNow Excel exports.

This tool applies a custom **8-hour logic** (rounding up any resolution time over 8 hours to a full day) to match specific business reporting requirements.

---

## 🚀 Version History

### **V2.0 (Latest Release)**
* **Executive HTML Reporting:** Added "Download Executive Report" feature which generates a professional, auto-aligned HTML report with performance badges and trend visualizations.
* **Smart Volume Thresholds:** "Best Performers" now requires a minimum of **3 tickets** handled to ensure statistical significance (prevents "1-hit wonders").
* **Interactive Investigative Maps:** Upgraded static charts to Plotly Interactive Trendlines with KPI target legends and detailed hover-data (Ticket ID/Group).
* **Enhanced UI/UX:** Added "Back to Selection" navigation and rounded performance metrics for cleaner dashboard viewing.
* **Deployment Hardening:** Standardized Docker environment and streamlined column mapping for all 5 modules.

### **V1.0 (Initial Release)**
* **8-Hour Logic:** Core conversion of timestamps into business-aligned "Calculated Days."
* **Multi-Module Support:** Specific mapping for Incidents, Requests, Changes, Feedback, and Surveys.
* **Secure Access:** Built-in password protection gatekeeper via environment variables.
* **Dockerized:** Fully containerized for one-command deployment.

---

## 🛠️ Deployment Guide

### **1. Clone the repository**
git clone https://github.com/beanp02/mttr-calculator.git
cd mttr-calculator

### **2. Create your Secret Key**
Create a hidden file to hold your password. This keeps it safe and private:
nano .env

Type the following inside the file, then save and exit (Ctrl+O, Enter, Ctrl+X):
APP_PASSWORD=YourChosenPasswordHere

### **3. Launch the App**
docker compose up -d --build

---

## 📂 Required Excel Columns
The ServiceNow export should contain headers that the app can automatically map, though you can manually adjust them in the settings:

| Module | Start Column | End Column |
| :--- | :--- | :--- |
| **Incident** | Created | Resolved at |
| **Request** | Created | Closed |
| **Change** | Actual start date | Actual end date |
| **Feedback** | Start | End |
| **Survey** | Taken on | Action completed |

---

## 🔒 Security Notes
This app uses an .env file to manage access.

---
