from flask import Flask, request, abort, jsonify
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    CORS(app, resources={r"/*": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,DELETE')
        return response

    @app.route('/categories')
    def get_categories():
        categories = {str(category.id): category.type for category in Category.query.order_by(Category.id).all()}

        if len(categories) == 0:
            abort(404)

        return jsonify({'success': True,
                        'categories': categories})

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

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
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

    @app.route('/questions/<string:search_term>', methods=['POST'])
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
                abort(422)

        return jsonify({'success': True,
                        'questions': questions,
                        'total_questions': total_q,
                        'current_category': current_cat
                        })

    @app.route('/categories/<int:category_id>/questions')
    def get_questions_by_category(category_id):
        not_found = False
        try:
            if category_id > 99:
                raise Exception(f'{category_id} must be below 100')
            questions = Question.query.filter_by(category=category_id).all()
            total_q = len(questions)
            if total_q == 0:
                not_found = True
                raise Exception(f'Questions for category with id {category_id} not found')

            questions = [question.format() for question in questions]

        except Exception:
            if not_found:
                abort(404)
            else:
                abort(422)

        return jsonify({'success': True,
                        'questions': questions,
                        'total_questions': total_q,
                        'current_category': category_id
                        })

    @app.route('/quizzes', methods=['POST'])
    def get_quiz_questions():
        data = request.get_json()

        prev_qs_ids = data.get('previous_questions', None)
        quiz_cat = data.get('quiz_category', None)

        if prev_qs_ids is None or quiz_cat is None:
            abort(400)

        try:
            cat_id = quiz_cat['id']
            if cat_id == 0:
                questions = [question.format() for question in Question.query.all() if question.id not in prev_qs_ids]
            else:
                questions = [question.format() for question in Question.query.filter_by(category=cat_id).all()
                             if question.id not in prev_qs_ids]

            if len(questions) == 0:
                return jsonify({'success': True})

            question = random.choice(questions)

        except:
            abort(422)

        return jsonify({'success': True,
                        'question': question
                        })

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'success': False,
                        'error': 400,
                        'message': 'Bad request'}), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'success': False,
                        'error': 404,
                        'message': 'Not found'}), 404

    @app.errorhandler(405)
    def not_allowed(error):
        return jsonify({'success': False,
                        'error': 405,
                        'message': 'Method not allowed'}), 405

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({'success': False,
                        'error': 422,
                        'message': 'Unprocessable entity'}), 422

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({'success': False,
                        'error': 500,
                        'message': 'Internal server error'}), 500

    return app
