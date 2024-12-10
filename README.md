# Quiz Application with Flask and PostgreSQL

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
   ```

2. **Create a Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables**

   Create a `.env` file in the root directory:
   ```env
   DATABASE_URL=postgresql://username:password@host:port/dbname
   SECRET_KEY=your_secret_key
   ```
   Replace `username`, `password`, `host`, `port`, and `dbname` with your PostgreSQL database credentials.

5. **Initialize the Database**

   Open the PostgreSQL client and execute the SQL schema provided here. Or use `psql` to execute:
   ```bash
   psql -U username -d dbname -f schema.sql
   ```

6. **Run the Application**
   ```bash
   python app.py
   ```

7. **Access the Application**

   Open your browser and visit: `http://localhost:5000`

## API Integration

The application integrates with the [Open Trivia API](https://opentdb.com/) to fetch quiz questions dynamically. Below is a brief overview of how the integration works:

1. **Fetching Questions**: The application sends a GET request to the Open Trivia API endpoint to retrieve quiz questions based on the selected category and difficulty.
2. **Processing Responses**: The API response is parsed, and the questions are formatted to be displayed to the user.
3. **Handling Errors**: The application includes error handling to manage cases where the API request fails or returns no questions.

Example of an API request to fetch 10 questions of medium difficulty from the "General Knowledge" category: