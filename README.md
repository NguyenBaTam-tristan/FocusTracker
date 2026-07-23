🚀 FocusTracker 2.0

A lightweight Python-based productivity tracker that helps you monitor focus sessions, store activity data, and generate simple reports.

📌 Features
⏱ Track focus sessions
💾 Store session data using SQLite
📊 Generate reports from tracked data
🧠 Simple and minimal design for personal productivity
🛠 Tech Stack
Python 3
SQLite
Standard Python libraries
📂 Project Structure
FocusTracker/
│── main.py          # Entry point
│── tracker.py       # Focus tracking logic
│── database.py      # Database operations
│── report.py        # Reporting functionality
│── config.py        # Configuration (API keys, settings)
│── focus_data.db    # SQLite database
⚙️ Installation
git clone https://github.com/NguyenBaTam-tristan/FocusTracker.git
cd FocusTracker

(Optional) Create virtual environment:

python -m venv env
env\Scripts\activate   # Windows
▶️ Usage

Run the app:

python main.py
🔐 Configuration

Edit config.py to update your settings.

⚠️ Important:

Do NOT upload your real API keys to GitHub
If you accidentally exposed a key, revoke it immediately
📊 Example Workflow
Start a focus session
Data is stored in SQLite database
Generate report to analyze productivity
🚧 Future Improvements
GUI interface
Data visualization charts
Cloud sync
Better session analytics
🤝 Contributing

Pull requests are welcome. Feel free to fork and improve the project.

📄 License

This project is for learning and personal use.
