# CITS5505_Group14_GroupProject - FitBug - Fitness Tracker & Data Visualization Web App

## Group Members

| Name                    | UWA Student ID | GitHub Username |
|-------------------------|----------------|------------------|
| Tharuki Dunyasha Silva  | 24327701       | TharuSilva       |
| John Koh                | 23845086       | jksy1414          |
| Maryam Saeed            | 23121354       | Mars-Martiny      |
| Qidi Cai                | 24053566       | QidiC             |

---

## Purpose of the Application

FitBug is a web-based fitness data analysis platform developed as part of the CITS5505 Web Programming course at The University of Western Australia.

The goal of FitBug is to provide a user-friendly system where individuals can upload their personal fitness data (e.g., from smartwatches or health apps), analyze it for patterns and progress, and visualize the results using customizable charts. FitBug is designed with a focus on usability, privacy, and social sharing.

Key features include:

- User registration and login with secure authentication.
- Upload of fitness tracking data in CSV format.
- Column selection and header renaming for flexibility in analysis.
- Statistical summaries (average, minimum, maximum) per metric.
- Interactive visualizations (line, bar, pie, radar, etc.) using Chart.js.
- Sharing options: private, friends-only, or public.
- History tracking of past analyses per user account.
- Friend system for inviting and accepting other users.

---

## Website Outline

**FitBug** allows users to upload fitness data and receive personalized statistics about their physical activity. These stats can optionally be shared with other users either publicly or with friends/followers only. The visuals can also be downloaded for external sharing. The user retains complete control over what is shared. Personal history is saved in the user’s account and remains private unless shared.

- **Input** – Fitness tracker data (CSV from smartwatch or app)
- **Output** – Graphical statistics and summary
- **Sharing (Output)** – Internal (public or friend-only); External (download)
- **Account** – Username, Password, Profile, History (Output records)

### Main Pages

1. Home / Welcome page
2. Login / Registration
3. Data Upload and Selection
4. Analysis and Output Visualization
5. Account Page (history and profile features)

---

## How to Launch the Application

### Prerequisites

- Python 3.8 or later
- pip
- Git

### Setup Instructions

1. **Clone the repository**

```bash
git clone https://github.com/jksy1414/CITS5505_Group14_GroupProject.git
cd CITS5505_Group14_GroupProject
```

2. **Create and activate a virtual environment (optional)**

```bash
python -m venv venv
source venv/bin/activate       # On macOS/Linux
venv\Scripts\activate        # On Windows
```

3. **Install required packages**

```bash
pip install -r requirements.txt
```

4. **Configure environment variables**

Create a `.env` file with the following:

```
SECRET_KEY=your-secret-key
FLASK_APP=app.py
FLASK_ENV=development
MAIL_SERVER=smtp.example.com
MAIL_PORT=587
MAIL_USERNAME=your-email@example.com
MAIL_PASSWORD=your-email-password
```

5. **Initialize the database**

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

6. **Run the application**

```bash
flask run
```

Then open your browser and go to `http://127.0.0.1:5000`

---

## How to Run the Tests

### Unit Tests

```bash
pytest tests/
```

### Selenium System Tests

1. Make sure the app is running.
2. In a new terminal:

```bash
pytest tests/selenium/
```

If needed:

```bash
pip install selenium chromedriver_autoinstaller
```

---

## Figma UI Designs

We also designed a mockup UI in Figma to help guide development and styling.  
[View Figma Prototype](https://www.figma.com/file/EXAMPLELINK/fitbug-design)  
(*replace with your actual link*)

---

## Folder Structure

```plaintext
CITS5505_Group14_GroupProject/
├── app.py
├── models.py
├── auth_routes.py
├── templates/
├── static/
├── migrations/
├── tests/
├── requirements.txt
├── .env
├── README.md
```

---

## References

### Home Page Visuals:
- https://dribbble.com/shots/7884095-Fitness-Icons
- https://hollowknight.fandom.com/wiki/Hollow_Knight_Kickstarter?file=Kickstarter_voice.png
- https://hollowknight.fandom.com/wiki/Cornifer?file=Npc_mapper.png
- https://hollowknight.fandom.com/wiki/Nailsmith?file=Nailsmith+2.png

### Data Input Page:
- https://hollowknight.fandom.com/wiki/Cornifer?file=Cornifer.png

### Data Output Page:
- https://hollowknight.fandom.com/wiki/Sheo?file=NailmasterSheo.png

### Default Profile Picture:
- "Artful Anticks" by Oliver Herford, 1894

---

## AI Usage

This README and various planning materials (folder structure, setup steps) were drafted and refined using OpenAI’s ChatGPT and Copilot, which assisted in formatting and generating structured documentation. No generated code or content was used directly in the core application without review.

---

## Contact

For academic-related questions, please reach out to:  
John Koh – jksy1414@students.uwa.edu.au
