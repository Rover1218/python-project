from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from db import get_db_connection
import bcrypt
import requests
import os
from dotenv import load_dotenv
from functools import wraps
from datetime import datetime

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")  # Fetch the secret key from the environment variables

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please login to access this page!", "error")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Route: Home
@app.route('/')
def home():
    # Check if there's a logout message stored in session
    logout_message = session.pop('logout_message', None)
    if logout_message:
        flash(logout_message, "success")
    
    user_info = None
    if 'user_id' in session:
        conn = get_db_connection()
        if conn:
            cur = conn.cursor()
            try:
                # Fetch user's latest quiz results
                cur.execute(
                    """
                    SELECT quiz_score, submitted_at, total_questions, correct_answers
                    FROM Results 
                    WHERE user_id = %s 
                    ORDER BY submitted_at DESC LIMIT 1
                    """, 
                    (session['user_id'],)
                )
                result = cur.fetchone()
                
                # Fetch total quizzes taken
                cur.execute(
                    """
                    SELECT COUNT(DISTINCT result_id) 
                    FROM Results 
                    WHERE user_id = %s
                    """, 
                    (session['user_id'],)
                )
                total_quizzes = cur.fetchone()[0]
                
                # Fetch average score
                cur.execute(
                    """
                    SELECT AVG(quiz_score) 
                    FROM Results 
                    WHERE user_id = %s
                    """, 
                    (session['user_id'],)
                )
                avg_score = cur.fetchone()[0]
                
                user_info = {
                    'username': session.get('username'),
                    'latest_score': result[0] if result else None,
                    'latest_date': result[1].strftime("%B %d, %Y at %I:%M %p") if result else None,
                    'total_quizzes': total_quizzes,
                    'average_score': round(avg_score, 2) if avg_score else 0
                }
            except Exception as e:
                flash(f"Error fetching user information: {str(e)}", "error")
            finally:
                cur.close()
                conn.close()
    
    return render_template('home.html', logged_in='user_id' in session, user_info=user_info)

# Route: Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        if conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM Users WHERE username = %s", (username,))
            user = cur.fetchone()
            if user and bcrypt.checkpw(password.encode('utf-8'), user[3].encode('utf-8')):
                session['user_id'] = user[0]
                session['username'] = user[1]  # Store username in session
                flash("Welcome back! 👋", "success")
                cur.close()
                conn.close()
                return redirect(url_for('home'))  # Redirect to home instead of quiz
            else:
                flash("Invalid username or password! 😕", "error")
            cur.close()
            conn.close()
    else:
        # Check if there's a logout message stored in session
        logout_message = session.pop('logout_message', None)
        if logout_message:
            flash(logout_message, "success")
    return render_template('login.html')


# Route: Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        conn = get_db_connection()
        if conn:
            cur = conn.cursor()
            try:
                cur.execute(
                    'INSERT INTO Users (username, email, password_hash) VALUES (%s, %s, %s) RETURNING user_id',
                    (username, email, hashed_password.decode('utf-8'))
                )
                user_id = cur.fetchone()[0]
                conn.commit()
                session['user_id'] = user_id
                session['username'] = username
                flash("Registration successful! Welcome to Quiz Master! 🎉", "success")
                return redirect(url_for('home'))
            except Exception as e:
                conn.rollback()
                flash(f"Registration failed: {str(e)}", "error")
            finally:
                cur.close()
                conn.close()
    return render_template('register.html')

@app.route('/quiz', methods=['GET', 'POST'])
@login_required
def quiz():
    if request.method == 'GET':
        # Get quiz parameters from query string
        quiz_type = request.args.get('type')
        category = request.args.get('category')
        
        # If no parameters are provided, show the quiz settings form
        if not quiz_type and not category:
            return render_template("quiz.html", questions=None)
            
        difficulty = request.args.get('difficulty')
        amount = request.args.get('amount', '5')

        # Build API URL with parameters
        api_url = f"https://opentdb.com/api.php?amount={amount}&type={quiz_type}"
        if category:
            api_url += f"&category={category}"
        if difficulty:
            api_url += f"&difficulty={difficulty}"

        try:
            # Fetch questions based on type
            response = requests.get(api_url)
            data = response.json()
            
            if data['response_code'] != 0:
                flash("Error fetching questions. Please try again.", "error")
                return redirect(url_for('home'))
                
            api_questions = data.get('results', [])
            
            if not api_questions:
                flash("No questions available. Please try again.", "error")
                return redirect(url_for('home'))
            
            conn = get_db_connection()
            if conn:
                cur = conn.cursor()
                try:
                    questions = []
                    for q in api_questions:
                        # Store category
                        cur.execute("""
                            INSERT INTO Categories (name) VALUES (%s)
                            ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name
                            RETURNING category_id
                        """, (q['category'],))
                        category_id = cur.fetchone()[0]
                        
                        # Store question
                        cur.execute("""
                            INSERT INTO Questions (category_id, question_text, difficulty, question_type, api_question_id)
                            VALUES (%s, %s, %s, %s, %s)
                            ON CONFLICT (api_question_id) DO UPDATE SET question_text = EXCLUDED.question_text
                            RETURNING question_id
                        """, (category_id, q['question'], q['difficulty'], q['type'], 
                              f"{q['question']}_{q['category']}"))  # Create unique ID
                        question_id = cur.fetchone()[0]
                        
                        # Store answers based on question type
                        if quiz_type == 'boolean':
                            answers = [
                                {'text': 'True', 'is_correct': q['correct_answer'] == 'True'},
                                {'text': 'False', 'is_correct': q['correct_answer'] == 'False'}
                            ]
                        else:
                            answers = [{'text': q['correct_answer'], 'is_correct': True}]
                            for incorrect in q['incorrect_answers']:
                                answers.append({'text': incorrect, 'is_correct': False})
                        
                        for answer in answers:
                            cur.execute("""
                                INSERT INTO Answers (question_id, answer_text, is_correct)
                                VALUES (%s, %s, %s)
                                RETURNING answer_id
                            """, (question_id, answer['text'], answer['is_correct']))
                        
                        questions.append({
                            'id': question_id,
                            'question': q['question'],
                            'answers': answers
                        })
                    
                    conn.commit()
                    return render_template("quiz.html", questions=questions)
                except Exception as e:
                    conn.rollback()
                    flash(f"Error preparing quiz: {str(e)}", "error")
                finally:
                    cur.close()
                    conn.close()
        except Exception as e:
            print("Error:", str(e))  # Print any errors
            flash(f"Error fetching questions: {str(e)}", "error")
            return redirect(url_for('home'))
    
    if request.method == 'POST':
        try:
            data = request.get_json()
            print("Received data:", data)  # Debug log
            
            user_id = session['user_id']
            answers = data.get('answers', [])
            
            if not answers:
                return jsonify({'success': False, 'error': 'No answers provided'})
            
            total_questions = len(answers)
            correct_answers = sum(1 for ans in answers if ans['isCorrect'])
            quiz_score = (correct_answers / total_questions) * 100

            conn = get_db_connection()
            if conn:
                cur = conn.cursor()
                try:
                    # Create Results entry
                    cur.execute("""
                        INSERT INTO Results 
                        (user_id, quiz_score, total_questions, correct_answers, submitted_at)
                        VALUES (%s, %s, %s, %s, NOW())
                        RETURNING result_id
                    """, (user_id, quiz_score, total_questions, correct_answers))
                    
                    result_id = cur.fetchone()[0]
                    print(f"Created result_id: {result_id}")  # Debug log
                    
                    # Store each answer
                    for answer in answers:
                        print(f"Processing answer: {answer}")  # Debug log
                        cur.execute("""
                            INSERT INTO User_Answers 
                            (user_id, question_id, selected_answer_id, result_id, is_correct)
                            VALUES (%s, %s, %s, %s, %s)
                        """, (
                            user_id, 
                            answer['questionId'], 
                            answer['answerId'],
                            result_id,
                            answer['isCorrect']
                        ))
                    
                    conn.commit()
                    return jsonify({
                        'success': True,
                        'score': quiz_score,
                        'correct': correct_answers,
                        'total': total_questions,
                        'result_id': result_id
                    })
                except Exception as e:
                    conn.rollback()
                    print(f"Database error: {str(e)}")  # Debug log
                    return jsonify({'success': False, 'error': str(e)})
                finally:
                    cur.close()
                    conn.close()
        except Exception as e:
            print(f"Server error: {str(e)}")  # Debug log
            return jsonify({'success': False, 'error': str(e)})

    flash("Error loading quiz questions", "error")
    return redirect(url_for('home'))

@app.route('/results/<int:result_id>')
@login_required
def view_result(result_id):
    conn = get_db_connection()
    if conn:
        cur = conn.cursor()
        try:
            # Get quiz result
            cur.execute("""
                SELECT quiz_score, submitted_at, total_questions, correct_answers
                FROM Results 
                WHERE result_id = %s AND user_id = %s
            """, (result_id, session['user_id']))
            result = cur.fetchone()
            
            if result:
                # Get detailed answers
                cur.execute("""
                    SELECT q.question_text, ua.is_correct, 
                           ua.selected_answer_id, a.answer_text,
                           (SELECT answer_text FROM Answers WHERE question_id = q.question_id AND is_correct = true LIMIT 1) as correct_answer
                    FROM User_Answers ua
                    JOIN Questions q ON ua.question_id = q.question_id
                    JOIN Answers a ON ua.selected_answer_id = a.answer_id
                    WHERE ua.result_id = %s
                    ORDER BY ua.answer_id
                """, (result_id,))
                answers = cur.fetchall()
                
                return render_template("results.html", 
                                    result=result,
                                    answers=answers)
            
        except Exception as e:
            flash(f"Error retrieving results: {str(e)}", "error")
        finally:
            cur.close()
            conn.close()
    
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    if 'user_id' in session:
        username = session.get('username', 'User')  # Get username before clearing session
        session.clear()
        # Store the logout message in session
        session['logout_message'] = f"Goodbye {username}! You've been logged out successfully!"
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
