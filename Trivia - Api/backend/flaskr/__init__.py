import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def split_into_pages(request, questions, number_questions):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * number_questions
    end = start + number_questions

    questions = [question.format() for question in questions]
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app, resources={'/': {'origins': '*'}})
    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization, true")
        response.headers.add("Access-Control-Allow-Methods", "GET, PUT, POST, DELETE, OPTIONS")
        return response
    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories')
    def get_categories():

        all_categories = {}
        categories = Category.query.all()
        for category in categories:
            all_categories[category.id] = category.type

        if len(all_categories) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'categories': all_categories
        }),200

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """

    @app.route('/questions')
    def get_questions():

        
        questions = Question.query.order_by(Question.id).all()
        total_questions = len(questions)
        categories = Category.query.order_by(Category.id).all()

        
        current_questions = split_into_pages(
            request, questions,
            QUESTIONS_PER_PAGE)

        if(len(current_questions) == 0):
            abort(404)

        all_categories = {}
        for category in categories:
            all_categories[category.id] = category.type

        return jsonify({
            'success': True,
            'total_questions': total_questions,
            'categories': all_categories,
            'questions': current_questions
        })

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:id>', methods=['DELETE'])

    def delete_question(id):
  
        question = Question.query.filter(Question.id == id).one_or_none()
        if question is None:
            abort(422)

        try:
            question.delete()
            questions = Question.query.order_by(Question.id).all()
            total_questions = len(questions)
            current_questions = split_into_pages(request, questions, QUESTIONS_PER_PAGE)

            categories = Category.query.order_by(Category.id).all()
            all_categories = {}
            for category in categories:
                all_categories[category.id] = category.type

            return jsonify({
                'success': True,
                'deleted': question.id,
                'total_questions': total_questions,
                'categories': all_categories,
                'questions': current_questions,
            })
        except:
            abort(422)

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/questions', methods=['POST'])
    def add_question():
        body = request.get_json()
        question = body.get('question')
        answer = body.get('answer')
        category = body.get('category')
        difficulty = body.get('difficulty')
       
        if ((question is None) or (answer is None) or (difficulty is None) or (category is None)):
            abort(422)
        try:
            question = Question(question=question, answer=answer, difficulty=difficulty, category=category)
            question.insert()

            all_questions = Question.query.order_by(Question.id).all()
            current_questions = split_into_pages(request, all_questions, QUESTIONS_PER_PAGE)

            return jsonify({
            'success': True,
            'created': question.id,
            'questions': current_questions,
            'total_questions': len(Question.query.all())
            })
        except:
            abort(422)   

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        body = request.get_json()
        search_term = body.get('searchTerm')

        if (search_term):
              questions = Question.query.filter(Question.question.ilike(f'%{search_term}%'))
              current_questions = split_into_pages(request, questions, QUESTIONS_PER_PAGE)

              return jsonify({
                  'success': True,
                  'questions': current_questions,
                  'total_questions': len(questions)
                })

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:id>/questions')
    def get_questions_by_categories(id):
      
        try:
            categories = Category.query.order_by(Category.id).all()
            all_categories = {}
            for category in categories:
                all_categories[category.id] = category.type
        except:
            abort(422)

        if all_categories.get(id) is None:
            abort(404)

        try:
         
            questions = Question.query.filter(Question.category == id).order_by(Question.id).all()
            total_questions = len(questions)
            current_questions = split_into_pages(request, questions, QUESTIONS_PER_PAGE)


            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': total_questions,
                'categories': all_categories,
                'current_category': id
            })
        except:
            abort(422)

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

    @app.route('/quizzes', methods=['POST'])
    def get_quiz_question():

        try:
            body = request.get_json()
            question_category =  body.get('quiz_category') 
            previous_questions = body.get('previous_questions')
          
            if ((previous_questions is None) or (question_category is None)):
                abort(400)

            if (question_category['id'] == 0):
                questions = Question.query.all()
            else:
                questions = Question.query.filter_by(category=question_category['id']).all()

            if len(questions) != 0:

                random_question = random.choice(questions)
                
                return jsonify({
                'success': True,
                'question': random_question.format()
                })

            else:
                return jsonify({
                'success': True,
                'question': None
                })

        except:
            abort(400)


    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def not_found(error):
      return jsonify({
          "success": False,
          "error": 404,
          "message": "Resource not found"
      }), 404

    @app.errorhandler(422)
    def unprocessable(error):
      return jsonify({
          "success": False,
          "error": 422,
          "message": "Unprocessable"
      }), 422

    @app.errorhandler(400)
    def bad_request(error):
      return jsonify({
          "success": False,
          "error": 400,
          "message": "Bad Request"
      }), 400


    return app

