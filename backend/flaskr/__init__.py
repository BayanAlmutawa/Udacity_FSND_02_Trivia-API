import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random


from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, questions):

  page = request.args.get('page', 1, type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE
  
  questions_list = [question.format() for question in questions]

  return questions_list[start:end]

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  #Allow '*' for origins
  CORS(app, resources={'/': {'origins': '*'}}) 

  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response


  # handle GET requests for all available categories.
  @app.route('/categories', methods=['GET'])
  def get_categories():
    
    try:

      categories_list = Category.query.order_by(Category.type).all()

      if len(categories_list) == 0:
        abort(404)

      return jsonify({
        'success': True,
        'categories': {category.id: category.type for category in categories_list}
      })

    except:
      abort(404)

  # handle GET requests for all questions, including pagination (every 10 questions). 
  
  @app.route('/questions', methods=['GET'])
  def get_questions():
    try:
      total_questions = Question.query.order_by(Question.id).all()
      questions_list = paginate_questions(request, total_questions)
      categories_results = Category.query.order_by(Category.type).all()

      categories = {category.id: category.type for category in categories_results}
      
      if len(questions_list) == 0:
        abort(404)

      return jsonify({
        'success': True,
        'questions': questions_list,
        'total_questions': len(total_questions),
        'current_category': None,
        'categories': categories
      })
    except:
      abort(404)


  # DELETE question using a question ID. 
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):

    question_obj = Question.query.filter_by(id=question_id).one_or_none()

    if not question_obj:
      abort(404)

    question_obj.delete()

    return jsonify({
      'success': True,
      'deleted': question_id
    })


  # POST a new question, 
  @app.route('/questions', methods=['POST'])
  def add_question():
    
    try:

      requested_data = request.get_json()

      question = requested_data.get('question')
      answer = requested_data.get('answer')
      difficulty = requested_data.get('difficulty')
      category = requested_data.get('category')

      new_question = Question(question=question, answer=answer, difficulty=difficulty, category=category)
      new_question.insert()

      return jsonify({
        'success': True,
        'created': new_question.id
      }) 

    except:
      abort(422)

    

  # get questions based on a specific search term. 
  @app.route('/questions/search', methods=['POST'])
  def search_question():

    try:
      search_term = request.get_json().get('searchTerm')

      if search_term:
        results = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()

        return jsonify({
          'success': True,
          'questions': [question.format() for question in results],
          'total_questions': len(results),
          'current_category': None
        })

    except:
      abort(404)



    
  # get questions based on a specific category. 
  @app.route('/categories/<int:category_id>/questions')
  def get_category_based_questions(category_id):

    try:
      questions_results = Question.query.order_by(Question.id).filter_by(category=category_id).all()

      if questions_results:
        category = [question.category for question in questions_results]

        return jsonify({
          "questions": [question.format() for question in questions_results],
          "total_questions": len(questions_results),
          "current_category": category
        })

    except:
      abort(404)





  # get random questions to play the quiz. 
  @app.route('/quizzes', methods=['POST'])
  def random_quiz():
    try:
      
      category = request.get_json().get('quiz_category')
      if not category:
        abort(404)
      
      pre_questions = request.get_json().get('previous_questions')

      if category['id'] == 0:
        questions = Question.query.all()
      else:
        questions = Question.query.filter_by(category=category['id']).all()
      
      questions_list =  [question.format() for question in questions if question.id not in pre_questions]

      random_question = random.choice(questions_list)
      return jsonify({
        'question': random_question
      })

    except:
      abort(422)


  # error handlers for all expected errors 
  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      "success": False,
      "error": 400,
      "message": "bad request"
    }), 400

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False,
      "error": 404,
      "message": "resource not found"
    }), 404

  @app.errorhandler(422)
  def uprocessable(error):
    return jsonify({
      "success": False,
      "error": 422,
      "message": "uprocessable"
    }), 422
  
  @app.errorhandler(500)
  def internal_error(error):
    return jsonify({
      "success": False,
      "error": 500,
      "message": "internal server error"
    }), 500
  
  return app


    