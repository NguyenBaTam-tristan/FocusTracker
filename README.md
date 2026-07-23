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

FocusTracker/
│── main.py          # Entry point
│── tracker.py       # Core tracking logic
│── database.py      # Database handling
│── report.py        # Report generation
│── config.py        # App configuration (DO NOT expose secrets)
└── focus_data.db    # Local database (SQLite)

---

## ⚙️ Setup & Installation

### 1. Clone the Repository

git clone https://github.com/NguyenBaTam-tristan/FocusTracker.git
cd FocusTracker

### 2. Create a Virtual Environment (Optional but Recommended)

Windows:
python -m venv env
env\Scripts\activate

macOS / Linux:
python3 -m venv env
source env/bin/activate

### 3. Install Dependencies

pip install -r requirements.txt

---

## ▶️ Running the App

Execute the main entry point to start tracking:

python main.py

---

## 🔐 Configuration & Security Notes

All application settings are managed in `config.py`.

> ⚠️ **Important Security Reminders:**
> - Do **NOT** push real API keys or sensitive variables to GitHub.
> - Keep personal credentials private.
> - If a secret key is accidentally leaked, **revoke it immediately**.

---

## 📊 How It Works

1. Start the application (`python main.py`).
2. Begin a focus session.
3. Session data is automatically saved into the local SQLite database (`focus_data.db`).
4. Generate reports to analyze your work habits and performance.

---

## 🚧 Roadmap

Planned features and improvements:

- [ ] 🖥️ GUI Interface
- [ ] 📈 Advanced analytics & Data visualization
- [ ] ☁️ Optional Cloud sync
- [ ] 🤖 AI-based productivity insights

---

## 🤝 Contributing

Contributions are always welcome! Feel free to fork this project, make improvements, and submit a pull request.

---

## 📄 License

This project is created for educational and personal use.

---

## 👤 Author

**Nguyen Ba Tam**
- GitHub: [@NguyenBaTam-tristan](https://github.com/NguyenBaTam-tristan)
