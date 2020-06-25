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
        self.database_path = "postgres://{}:{}@{}/{}".format('postgres','1234','localhost:5432', self.database_name)
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
        res =  self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertIsNotNone(data['categories'])


    def test_get_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertIsNotNone(data['questions'])

    def test_delete_questions(self):
        res = self.client().delete('/questions/21')
        data = json.loads(res.data)

        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 21)

    def test_failed_delete_questions(self):
        res = self.client().delete('/questions/23')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_add_question(self):

        num_before = len(Question.query.all())

        new_question = {
            'question': 'what is the sun color?',
            'answer': 'yellow',
            'difficulty': 1,
            'category': 5
        }

        res = self.client().post('/questions', json=new_question)
        data = json.loads(res.data)

        num_after = len(Question.query.all())


        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(num_before+1 , num_after)


    def test_failed_add_question(self):
        
        num_before = len(Question.query.all())

        res = self.client().post('/questions')
        data = json.loads(res.data)

        num_after = len(Question.query.all())


        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data['message'], 'uprocessable')
        self.assertEqual(num_before, num_after)


    def test_search_question(self):
        res = self.client().post('/questions/search', json={'searchTerm': "title"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertIsNotNone(data['questions'])
        self.assertIsNotNone(data['total_questions'])

    def test_failed_search_question(self):
        res = self.client().post('/questions/search')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')



    def test_get_category_based_questions(self):
        res = self.client().get('/categories/2/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertIsNotNone(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertEqual(data['current_category'], 'Art')

    def test_failed_get_category_based_questions(self):
        res = self.client().get('/categories/9/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    
    def test_random_quiz(self):


        res = self.client().post('/quizzes', json={
            "previous_questions": [], 
            "quiz_category": {
                "id": "2", "type": "Art"
            }
        })

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertIsNotNone(data['question'])



    def test_failed_random_quiz(self):

        res = self.client().post('/quizzes', json={
            "previous_questions": [], 
            "quiz_category": {
                "id": "8", "type": "Art"
            }
        })

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data['message'], 'uprocessable')





# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()