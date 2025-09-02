# 💳 BankStatementAnalyzer

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)  
[![Streamlit](https://img.shields.io/badge/Streamlit-Framework-red)](https://streamlit.io/)  
[![Pandas](https://img.shields.io/badge/Pandas-Data--Analysis-yellow)](https://pandas.pydata.org/)  
[![Matplotlib](https://img.shields.io/badge/Matplotlib-Visualization-green)](https://matplotlib.org/)  
[![License: MIT](https://img.shields.io/badge/License-MIT-black.svg)](LICENSE)  
[![Build](https://img.shields.io/badge/Build-Passing-brightgreen)](#)  
[![Made with PyCharm](https://img.shields.io/badge/Made%20with-PyCharm-lightgrey?logo=pycharm)](https://www.jetbrains.com/pycharm/)  
[![GitHub Stars](https://img.shields.io/github/stars/Tshepo206/BankStatementAnalyzer?style=social)](https://github.com/Tshepo206/BankStatementAnalyzer/stargazers)  
[![Last Commit](https://img.shields.io/github/last-commit/Tshepo206/BankStatementAnalyzer)](https://github.com/Tshepo206/BankStatementAnalyzer/commits/main)  

---

A **Streamlit-based web application** to **clean, normalize, and analyze bank statements**.  
Designed to simplify financial data review for accountants, analysts, and business owners.

---

## 🚀 Features
- 📂 Upload **bank statements** in CSV, XLSX, or XLS formats.
- 🧹 Normalize and clean raw transaction data.
- 🏷️ Rule-based transaction categorization (editable in `src/cleaner.py`).
- 📊 Visual insights:  
  - Top spending categories  
  - Debits vs Credits summary  
  - Interactive charts using Matplotlib
- 💾 Download cleaned data as **CSV** or **Excel**.
- ⚡ Lightweight and fully interactive via Streamlit.

---

## 🛠️ Tech Stack

**Programming Language**
- [Python 3.12](https://www.python.org/)

**Frameworks & Libraries**
- [Streamlit](https://streamlit.io/) → Interactive web app UI  
- [Pandas](https://pandas.pydata.org/) → Data cleaning & analysis  
- [Matplotlib](https://matplotlib.org/) → Data visualization  
- [scikit-learn](https://scikit-learn.org/) (optional) → Advanced analytics  
- [pytest](https://docs.pytest.org/) → Testing framework  
- [black](https://black.readthedocs.io/) + [isort](https://pycqa.github.io/isort/) → Code formatting  
- [flake8](https://flake8.pycqa.org/) → Linting

**Tools**
- [Make](https://www.gnu.org/software/make/) → Automates tasks (install, test, lint, run)  
- [Git](https://git-scm.com/) + [GitHub](https://github.com/) → Version control & collaboration  
- [PyCharm](https://www.jetbrains.com/pycharm/) → Main IDE  

---

## 📂 Project Structure

BankStatementAnalyzer/
├── .streamlit/           # Streamlit configuration (port, theme, etc.)
│   └── config.toml
├── data/                 # Sample and raw data (ignored by Git)
│   └── raw/
├── src/                  # Core source code
│   ├── init.py
│   └── cleaner.py        # Cleaning & categorization logic
├── tests/                # Unit tests
│   └── test_cleaner.py
├── LICENSE               # MIT License
├── Makefile              # Helper commands
├── README.md             # Project documentation
├── requirements.txt      # Python dependencies
└── streamlit_app.py      # Main Streamlit entry point

## ⚙️ Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Tshepo206/BankStatementAnalyzer.git
   cd BankStatementAnalyzer

2. Create and activate a virtual environment:

  python -m venv .venv
source .venv/bin/activate   # macOS/Linux
.venv\Scripts\activate      # Windows

3. Install dependencies:

    pip install -r requirements.txt

    ▶️ Usage

▶️ Usage

Run the app:

streamlit run streamlit_app.py

By default, it launches on:
👉 http://localhost:8503

🧪 Testing

Run the test suite:

pytest -q

🛠 Development

Use the Makefile for common tasks:

make install   # Install dependencies
make run       # Run the app
make test      # Run tests
make fmt       # Format code (black, isort)
make lint      # Run lint checks

📜 License

This project is licensed under the MIT License.
See the LICENSE file for details.

⸻

✨ Author

Tshepo Khoza
📌 Chartered Accountant → Building expertise in AI, Software Development, and Data Engineering
🔗 GitHub: Tshepo206

