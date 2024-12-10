# Quiz Application with Flask and PostgreSQL

A simple quiz web application that allows users to register, log in, and take quizzes. The application uses the Open Trivia API to fetch quiz questions dynamically and stores user data and responses in a PostgreSQL database.

---
A simple quiz web application that allows users to register, log in, and take quizzes. The application uses the Open Trivia API to fetch quiz questions dynamically and stores user data and responses in a PostgreSQL database.

---

## Features

- **User Registration and Login**: Secure authentication with hashed passwords using `bcrypt`.
- **Dynamic Quizzes**: Fetches quiz questions from the [Open Trivia API](https://opentdb.com/).
- **Answer Tracking**: Stores user answers and calculates results.
- **Leaderboard**: Tracks scores and provides user performance insights.
- **Responsive Design**: Frontend built with HTML and CSS.

---

## Technologies Used

- **Backend**: Flask (Python)
- **Database**: PostgreSQL
- **APIs**: Open Trivia API
- **Frontend**: HTML, CSS

---

## Installation

### Prerequisites

1. Python 3.8+
2. PostgreSQL database

### Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-username/quiz-app.git
   cd quiz-app
Create a Virtual Environment

bash
Copy code
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
Install Dependencies

bash
Copy code
pip install -r requirements.txt
Set Up Environment Variables

Create a .env file in the root directory:
env
Copy code
DATABASE_URL=postgresql://username:password@host:port/dbname
SECRET_KEY=your_secret_key
Replace username, password, host, port, and dbname with your PostgreSQL database credentials.
Initialize the Database

Open the PostgreSQL client and execute the SQL schema provided here.
Or use psql to execute:
bash
Copy code
psql -U username -d dbname -f schema.sql
Run the Application

bash
Copy code
python app.py
Access the Application

Open your browser and visit: http://localhost:5000
File Structure
bash
Copy code
quiz-app/
│
├── static/                  # Static files
│   ├── style.css            # CSS styles
│
├── templates/               # HTML templates
│   ├── home.html            # Home page
│   ├── login.html           # Login page
│   ├── register.html        # Register page
│   ├── quiz.html            # Quiz page
│
├── app.py                   # Main application logic
├── db.py                    # Database connection helper
├── requirements.txt         # Python dependencies
├── schema.sql               # Database schema
├── .env                     # Environment variables (not included in the repo)
└── README.md                # Project documentation
API Integration
Open Trivia API
The application fetches questions from the Open Trivia API. You can adjust the number and type of questions in app.py:

python
Copy code
response = requests.get("https://opentdb.com/api.php?amount=5&type=multiple")
Deployment
Local Deployment: Use the above instructions to run the app locally.
Cloud Deployment: Deploy using platforms like:
Heroku
AWS
Render
Contribution Guidelines
Fork the repository.
Create a new branch for your feature or bugfix:
bash
Copy code
git checkout -b feature-name
Commit your changes and push to your fork:
bash
Copy code
git add .
git commit -m "Description of changes"
git push origin feature-name
Submit a Pull Request.
License
This project is licensed under the MIT License. See the LICENSE file for details.

Acknowledgments
Open Trivia API for providing the quiz questions.
Flask for the backend framework.
PostgreSQL for the database.
yaml
Copy code

---

### **How to Use It**

1. Replace `your-username` in the clone command with your GitHub username.
2. Update any specific details like additional features, live demo links, or custom instructio