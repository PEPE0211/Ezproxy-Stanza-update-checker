# EZproxy Stanza Monitor

An automated Python utility designed to track updates for EZproxy database stanzas from the official OCLC support site. It identifies updates for your specific subscribed databases and sends summary email notifications.

## 🛠 Problem Solved
Managing EZproxy requires keeping stanzas up-to-date to ensure persistent user access. Manually checking the OCLC "Most Recent" page for a large list of databases is tedious. This script:
* **Automates Monitoring:** Scrapes the OCLC "Most Recent Stanzas" page weekly.
* **Smart Matching:** Uses fuzzy logic to match your local list against OCLC names, ignoring case and minor typos (e.g., "ieee xplor" matches "IEEE Xplore").
* **Targeted Alerts:** Only notifies you if a database *you actually use* has been updated.

---

## 🚀 Setup Instructions

### 1. Prerequisites
This script requires Python 3.12+ and uses a virtual environment to avoid system conflicts.

```bash
# Create project directory
mkdir ezproxy-monitor && cd ezproxy-monitor

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install requests beautifulsoup4
```
### 2. Configuration
Edit the StanzaChecker.py file with your credentials:

EMAIL_USER: Your email address.

EMAIL_PASS: Your 16-character App Password(I used Google).

RECIPIENT_EMAIL: The address where alerts should be sent.

### 3. Initialization
Before the first run, ensure your stanzas.json exists in the same directory. The script uses 2026-02-05 as the baseline date for all your databases to ensure you only get notified about updates moving forward. Make sure all your stanza's are updated or you can setup stanzas.json to have the date you actually updated the stanza.

📅 Automation
You can set up a cron job or Windows Task Scheduler, depending on your OS, to run the script with whatever interval you require.

🔍 Features & Monitoring
Logging
All script activity is logged to stanza_checker.log. You can monitor it in real-time:

```Bash
tail -f stanza_checker.log
```
Data Structure (stanzas.json)
The script maintains a JSON tracker. It includes a metadata field to show you exactly when the last check occurred, even if no updates were found.

Fuzzy Matching Logic
The script employs difflib.get_close_matches with an 80% similarity threshold. This ensures that variations in naming conventions between your list and OCLC do not result in missed updates.
