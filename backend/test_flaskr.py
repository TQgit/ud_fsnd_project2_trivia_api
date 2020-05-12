import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://postgres:demo@{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after each test"""
        pass

    def test_qet_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['categories'])

    def test_qet_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertTrue(data['categories'])

    def test_delete_question(self):
        new_q = Question(question='why?', answer='because', difficulty=5, category=1)
        new_q.insert()
        q_id = Question.query.filter_by(question='why?', answer='because').first().id

        res = self.client().delete(f'/questions/{q_id}')
        data = json.loads(res.data)

        question = Question.query.filter_by(id=q_id).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(question, None)
        self.assertTrue(data['success'])

    def test_add_question(self):
        questions_to_delete = Question.query.filter_by(question='when?', answer='now').all()
        if len(questions_to_delete) > 0:
            [question.delete() for question in questions_to_delete]

        new_q = Question(question='when?', answer='now', difficulty=5, category=1)

        res = self.client().post(f'/questions', json=new_q.format())
        data = json.loads(res.data)

        question = Question.query.filter_by(question='when?', answer='now').one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(question.id)
        self.assertTrue(data['success'])

    def test_search_questions(self):
        res = self.client().post('/questions/title')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertTrue(data['success'])

    def test_get_category_questions(self):
        cat_id = 1
        res = self.client().get(f'/categories/{cat_id}/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['current_category'], cat_id)
        self.assertTrue(data['questions'])
        self.assertTrue(data['success'])

    def test_post_quizzes(self):
        res = self.client().post('/quizzes', json={
            'previous_questions': [21, 22],
            'quiz_category': {'type': "Science", 'id': 1}
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['question']['category'], 1)
        self.assertTrue(data['question'])
        self.assertTrue(data['success'])

    def test_400_bad_add_question(self):
        res = self.client().post('/questions', json={'question': 'Is this enough?'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['error'], 400)
        self.assertTrue(data['message'])
        self.assertFalse(data['success'])

    def test_404_search_question_not_found(self):
        res = self.client().post('/questions/quarantine2020')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['error'], 404)
        self.assertTrue(data['message'])
        self.assertFalse(data['success'])

    def test_405_get_search(self):
        res = self.client().get('/questions/title')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['error'], 405)
        self.assertTrue(data['message'])
        self.assertFalse(data['success'])

    def test_422_category_larger_than_two_digits(self):
        res = self.client().get('/categories/777/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['error'], 422)
        self.assertTrue(data['message'])
        self.assertFalse(data['success'])


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
