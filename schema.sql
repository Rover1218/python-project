-- Users table
CREATE TABLE IF NOT EXISTS Users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL
);

-- Categories table
CREATE TABLE IF NOT EXISTS Categories (
    category_id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);

-- Questions table
CREATE TABLE IF NOT EXISTS Questions (
    question_id SERIAL PRIMARY KEY,
    category_id INTEGER REFERENCES Categories(category_id),
    question_text TEXT NOT NULL,
    difficulty VARCHAR(20),
    question_type VARCHAR(20),
    api_question_id VARCHAR(255) UNIQUE
);

-- Answers table
CREATE TABLE IF NOT EXISTS Answers (
    answer_id SERIAL PRIMARY KEY,
    question_id INTEGER REFERENCES Questions(question_id),
    answer_text TEXT NOT NULL,
    is_correct BOOLEAN NOT NULL
);

-- Results table
CREATE TABLE IF NOT EXISTS Results (
    result_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES Users(user_id),
    quiz_score DECIMAL(5,2),
    total_questions INTEGER,
    correct_answers INTEGER,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE User_Answers (
    answer_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES Users(user_id),
    question_id INTEGER REFERENCES Questions(question_id),
    selected_answer_id INTEGER REFERENCES Answers(answer_id),
    result_id INTEGER REFERENCES Results(result_id),
    is_correct BOOLEAN DEFAULT FALSE,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);