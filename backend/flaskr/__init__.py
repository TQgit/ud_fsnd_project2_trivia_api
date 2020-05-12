import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    '''
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    '''
    CORS(app, resources={r"/*": {"origins": "*"}})

    '''
    @TODO: Use the after_request decorator to set Access-Control-Allow
    '''

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,DELETE')
        return response

    '''
    @TODO: 
    Create an endpoint to handle GET requests 
    for all available categories.
    '''

    @app.route('/categories')
    def get_categories():
        categories = {str(category.id): category.type for category in Category.query.order_by(Category.id).all()}

        if len(categories) == 0:
            abort(404)

        return jsonify({'success': True,
                        'categories': categories})

    '''
    @TODO: 
    Create an endpoint to handle GET requests for questions, 
    including pagination (every 10 questions). 
    This endpoint should return a list of questions, 
    number of total questions, current category, categories.
  
    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions. 
    '''

    @app.route('/questions')
    def get_questions():
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        questions = Question.query.order_by(Question.id).all()
        total_q = len(questions)

        questions = [question.format() for question in questions[start:end]]
        categories = {str(category.id): category.type for category in Category.query.order_by(Category.id).all()}

        if len(questions) == 0 or len(categories) == 0:
            abort(404)

        current_cat = questions[0]['category']

        return jsonify({'success': True,
                        'questions': questions,
                        'total_questions': total_q,
                        'categories': categories,
                        'current_category': current_cat})

    '''
    @TODO: 
    Create an endpoint to DELETE question using a question ID. 
  
    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page. 
    '''

    @app.route('/questions/<question_id>', methods=['DELETE'])
    def delete_question(question_id):
        not_found = False
        try:
            question = Question.query.filter_by(id=question_id).one_or_none()
            if question is None:
                not_found = True
                raise Exception(f'question {question_id} not found')

            question.delete()
        except Exception:
            if not_found:
                abort(404)
            else:
                abort(422)

        return jsonify({'success': True})

    '''
    @TODO: 
    Create an endpoint to POST a new question, 
    which will require the question and answer text, 
    category, and difficulty score.
  
    TEST: When you submit a question on the "Add" tab, 
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.  
    '''

    @app.route('/questions', methods=['POST'])
    def add_question():
        try:
            data = request.get_json()

            question = data['question']
            answer = data['answer']
            difficulty = data['difficulty']
            category = data['category']

            new_question = Question(question=question, answer=answer, difficulty=difficulty, category=category)
            new_question.insert()
        except:
            abort(400)

        return jsonify({'success': True})

    '''
    @TODO: 
    Create a POST endpoint to get questions based on a search term. 
    It should return any questions for whom the search term 
    is a substring of the question. 
  
    TEST: Search by any phrase. The questions list will update to include 
    only question that include that string within their question. 
    Try using the word "title" to start. 
    '''

    @app.route('/questions/<search_term>', methods=['POST'])
    def search_question(search_term):
        not_found = False
        try:
            questions = Question.query.filter(Question.question.ilike(f'%{search_term}%')).order_by(Question.id).all()
            total_q = len(questions)

            if total_q == 0:
                not_found = True
                raise Exception(f'no questions with search term: "{search_term}" found')

            questions = [question.format() for question in questions]
            current_cat = questions[0]['category']

        except Exception:
            if not_found:
                abort(404)
            else:
                abort(400)

        return jsonify({'success': True,
                        'questions': questions,
                        'total_questions': total_q,
                        'current_category': current_cat
                        })

    '''
    @TODO: 
    Create a GET endpoint to get questions based on category. 
  
    TEST: In the "List" tab / main screen, clicking on one of the 
    categories in the left column will cause only questions of that 
    category to be shown. 
    '''

    

    '''
    @TODO: 
    Create a POST endpoint to get questions to play the quiz. 
    This endpoint should take category and previous question parameters 
    and return a random questions within the given category, 
    if provided, and that is not one of the previous questions. 
  
    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not. 
    '''

    '''
    @TODO: 
    Create error handlers for all expected errors 
    including 404 and 422. 
    '''

    return app
