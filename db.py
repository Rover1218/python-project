import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection settings
DATABASE_URL = os.getenv("DATABASE_URL")

# Database connection function
def get_db_connection():
    try:
        # Establish connection
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print("Error connecting to database:", e)
        return None

def init_db():
    conn = get_db_connection()
    if conn:
        cur = conn.cursor()
        try:
            # Create users table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS Users (
                    user_id SERIAL PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create categories table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS Categories (
                    category_id SERIAL PRIMARY KEY,
                    name VARCHAR(100) UNIQUE NOT NULL
                )
            """)

            # Create questions table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS Questions (
                    question_id SERIAL PRIMARY KEY,
                    category_id INTEGER NOT NULL,
                    question_text TEXT NOT NULL,
                    difficulty VARCHAR(10) CHECK (difficulty IN ('easy', 'medium', 'hard')),
                    question_type VARCHAR(10) CHECK (question_type IN ('multiple', 'boolean')),
                    api_question_id VARCHAR(255) UNIQUE NOT NULL,
                    FOREIGN KEY (category_id) REFERENCES Categories(category_id) ON DELETE CASCADE
                )
            """)

            # Create answers table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS Answers (
                    answer_id SERIAL PRIMARY KEY,
                    question_id INTEGER NOT NULL,
                    answer_text TEXT NOT NULL,
                    is_correct BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (question_id) REFERENCES Questions(question_id) ON DELETE CASCADE
                )
            """)

            # Create user_answers table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS User_Answers (
                    user_answer_id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    question_id INTEGER NOT NULL,
                    selected_answer_id INTEGER,
                    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
                    FOREIGN KEY (question_id) REFERENCES Questions(question_id) ON DELETE CASCADE,
                    FOREIGN KEY (selected_answer_id) REFERENCES Answers(answer_id) ON DELETE CASCADE
                )
            """)

            # Create results table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS Results (
                    result_id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    quiz_score DECIMAL(5,2) NOT NULL,
                    total_questions INTEGER NOT NULL,
                    correct_answers INTEGER NOT NULL,
                    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
                )
            """)

            conn.commit()
            print("Database tables created successfully!")
        except Exception as e:
            print("Error creating tables:", e)
            conn.rollback()
        finally:
            cur.close()
            conn.close()

# Call this function when the application starts
if __name__ == "__main__":
    init_db()
