# FitBug – Fitness Tracker & Data Visualization Web App  
_CITS5505 Group 14 – The University of Western Australia_

---

##  Group Members

| Name                    | UWA Student ID | GitHub Username |
|-------------------------|----------------|------------------|
| Tharuki Dunyasha Silva  | 24327701       | TharuSilva       |
| John Koh                | 23845086       | jksy1414         |
| Maryam Saeed            | 23121354       | Mars-Martiny     |
| Qidi Cai                | 24053566       | Stitchy-QIDI     |

---

##  Project Overview

**FitBug** is a fitness data analysis platform developed using Flask for the CITS5505 Web Programming unit. Users can upload personal fitness data (e.g., from smartwatches or mobile apps), generate customizable visual reports, and manage personal statistics securely.

###  Key Features
- User registration, login, and profile management
- CSV file upload with dynamic column selection
- Editable headers before visualization
- Chart options: Line, Bar, Pie, Radar (via Chart.js)
- Statistical summaries: min, max, average
- Sharing: Private, Friends-only, or Public
- Analysis history and activity log per user
- Friend system: invite, accept, reject

---

##  Application Flow

| Step | Page / Tab                  | Functionality                                       |
|------|----------------------------|----------------------------------------------------|
| 1️⃣   | Home / Welcome             | Intro to FitBug                                    |
| 2️⃣   | Login / Register           | Secure access                                      |
| 3️⃣   | Data Upload                | Upload fitness CSVs                                |
| 4️⃣   | Column Selection + Rename  | Choose and rename headers for graphs               |
| 5️⃣   | Analysis & Visualization   | View interactive graphs and summary statistics     |
| 6️⃣   | Output Sharing             | Share results: private, friends, public, download  |
| 7️⃣   | Account Page               | Profile, history, goal tracker, friend system      |
| 8️⃣   | Explore Page               | view all shared graphs(public, private, friends)   |
---

##  Getting Started

###  Prerequisites
- Python 3.8+
- pip
- Git

###  Setup Instructions

```bash
# 1. Clone repository
git clone https://github.com/jksy1414/CITS5505_Group14_GroupProject.git
cd CITS5505_Group14_GroupProject

# 2. Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
touch .env  # or use any text editor
```

#### Example `.env` file:

```env
SECRET_KEY=your-secret-key
FLASK_APP=app.py
FLASK_ENV=development
MAIL_SERVER=smtp.example.com
MAIL_PORT=587
MAIL_USERNAME=your-email@example.com
MAIL_PASSWORD=your-email-password
```

###  Database Initialization

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

###  Launch the App

```bash
flask run
```

Visit: [http://127.0.0.1:5000](http://127.0.0.1:5000)

---
### Email Configuration for Password Reset
To enable the password reset feature, you need to configure your own email credentials in the environment file (.env or named.env). This feature uses Flask-Mail to send verification codes.

```bash
Example (Gmail):
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
MAIL_DEFAULT_SENDER=your_email@gmail.com
```
If you use Gmail, you must generate an App Password and use that instead of your real password.

---

##  Testing Instructions

###  Unit Tests

```bash
pytest tests/unit_tests
```

###  Selenium System Tests

1. Ensure the Flask app is running (`flask run`)
2. In a separate terminal:


```bash
pytest tests/selenium/
```

_If needed:_

```bash
pip install selenium chromedriver_autoinstaller
```


**📝Note:** Before running any Selenium tests that involve login, make sure to first run:

```bash
python tests/selenium/test_register_success.py
```
This script generates a test account and saves the credentials in a file named last_test_account.txt
```bash
located at tests/selenium/test_files/last_test_account.txt.
```
Any Selenium test that requires login (such as test_login_success.py, test_chart.py, etc.) depends on the credentials stored in this file.


---

##  UI Design

Figma-based prototype is available at:  
 [FitBug Figma Design](https://www.figma.com/file/EXAMPLELINK/fitbug-design)  
(_Replace with actual Figma URL_)

---

##  Project Structure

```plaintext
CITS5505_Group14_GroupProject/
├── app.py
├── models.py
├── auth_routes.py
├── templates/               # All HTML templates
├── static/                  # CSS, JS, images
├── tests/                   # Unit + Selenium test scripts
├── migrations/              # Database schema history
├── requirements.txt
├── README.md
├── .env                     # Your environment variables (not committed)
├── extension.py
├── forms.py  
```
##  Testing File

```plaintext
test.csv is the file for testing the function in the web
```

##  .env File

```plaintext
the .env file is include to show the example how the create the .env file would be, there is no secret key in it. 
```

---

## 📸 Media Credits

### Home Page:
- [Fitness Icons - Dribbble](https://dribbble.com/shots/7884095-Fitness-Icons)
- [Cornifer](https://hollowknight.fandom.com/wiki/Npc_mapper.png)
- [Nailsmith](https://hollowknight.fandom.com/wiki/Nailsmith?file=Nailsmith+2.png)

### Input Page:
- [Cornifer Input](https://hollowknight.fandom.com/wiki/Cornifer?file=Cornifer.png)

### Output Page:
- [Sheo Art](https://hollowknight.fandom.com/wiki/Sheo?file=NailmasterSheo.png)

### Default Profile:
- "Artful Anticks" by Oliver Herford (1894)

---

##  AI Acknowledgement

Documentation, instructions, and project structure were partially assisted by OpenAI’s ChatGPT and Copilot for drafting, formatting, and validation. All generated content was reviewed by the development team before use.

---

##  Contact

For course-related questions:  
**John Koh** – jksy1414@students.uwa.edu.au

---
