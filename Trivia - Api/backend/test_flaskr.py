import os
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
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories(self):
        res = self.client().get('/categories')
        body = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(body['success'], True)
        self.assertTrue(body['categories'])

    def test_get_questions(self):
        res = self.client().get('/questions')
        body = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(body['success'], True)
        self.assertTrue(body['total_questions'])
        self.assertTrue(body['categories'])
        self.assertTrue(body['questions'])

    def test_delete_question(self):
        res = self.client().delete('/questions/6')
        body = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(body['success'], True)
        self.assertTrue(body['deleted'])
        self.assertTrue(body['total_questions'])
        self.assertTrue(body['categories'])
        self.assertTrue(body['questions'])

    def test_422_delete_question(self):
        res = self.client().delete('/questions/9999')
        body = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(body['success'], False)
        self.assertEqual(body['message'], 'Unprocessable')

    def test_add_question(self):
        res = self.client().post('/questions', json=self.new_question)
        body = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(body['success'], True)
        self.assertTrue(body['created'])
        self.assertTrue(body['questions'])
        self.assertTrue(body['total_questions'])
        self.assertTrue(body['categories'])

    def test_422_add_question(self):
        self.app.config["SQLALCHEMY_DATABASE_URI"] = ""
        res = self.client().post('/questions', json=self.question)
        body = json.loads(res.data)
        self.app.config["SQLALCHEMY_DATABASE_URI"] = self.database_path

        self.assertEqual(res.status_code, 422)
        self.assertEqual(body['success'], False)
        self.assertEqual(body['message'], 'Unprocessable')

    def test_search_questions(self):
        res = self.client().post('/questions', json={'searchTerm': 'What'})
        body = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(body['success'], True)
        self.assertTrue(body['questions'])
        self.assertTrue(body['total_questions'])
 

    def test_404_search_questions(self):
        res = self.client().post('/questions', json={'searchTerm': 'Madagascar'})
        body = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(body['success'], False)
        self.assertEqual(body['message'], 'Resource not found')


    def test_get_questions_by_category(self):
        res = self.client().get('/categories/5/questions')
        body = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(body['success'], True)
        self.assertTrue(body['questions'])
        self.assertTrue(body['total_questions'])
        self.assertTrue(body['categories'])
        self.assertEqual(body['current_category'], 1)

    def test_404_get_questions_by_category(self):
        res = self.client().get('/categories/9999/questions')
        body = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(body['success'], False)
        self.assertEqual(body['message'], 'Resource not found')

    def test_422_get_questions_by_category(self):
        self.app.config["SQLALCHEMY_DATABASE_URI"] = ""
        res = self.client().get('/categories/6/questions')
        body = json.loads(res.data)
        self.app.config["SQLALCHEMY_DATABASE_URI"] = self.database_path
        self.assertEqual(res.status_code, 422)
        self.assertEqual(body['success'], False)
        self.assertEqual(body['message'], 'Unprocessable')

    def test_get_quiz_question(self):
        res = self.client().post('/quizzes', json={'previous_questions': [], 'quiz_category': {'id': 1}})
        body = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(body['success'], True)
        self.assertTrue(body['question'])

    def test_get_quiz_question_failed(self):
        res = self.client().post('/quizzes', json={'previous_questions': []})
        body = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(body['success'], False)
        self.assertEqual(body['message'], 'Unprocessable')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()