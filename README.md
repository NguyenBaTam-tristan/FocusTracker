# 🚀 FocusTracker

> A simple yet powerful productivity tracker built with Python to monitor focus sessions and analyze work habits.

---

## 🧠 Overview

**FocusTracker** helps you stay disciplined by tracking your focus sessions, storing activity data, and generating reports to evaluate your productivity over time.

This project is designed to be:
- ⚡ **Lightweight**
- 🧩 **Easy to use**
- 🔒 **Fully local**

---

## ✨ Features

- ⏱ **Focus Session Tracking:** Track how long you stay focused during work sessions.
- 💾 **Local Data Storage:** Uses SQLite to store all session data securely on your machine.
- 📊 **Basic Reporting:** Generate reports to review your productivity over time.
- ⚙️ **Custom Configuration:** Easily modify settings via `config.py`.

---

## 🛠 Tech Stack

- **Language:** Python 3
- **Database:** SQLite
- **Libraries:** Standard Python libraries

---

## 📂 Project Structure

```text
FocusTracker/
│── main.py          # Entry point
│── tracker.py       # Core tracking logic
│── database.py      # Database handling
│── report.py        # Report generation
│── config.py        # App configuration (DO NOT expose secrets)
└── focus_data.db    # Local database (SQLite)
