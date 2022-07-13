import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

db_drop_and_create_all()

# ROUTES DEFINITION
@app.route('/drinks')
def get_drinks():

    drinks = [drink.short() for drink in Drink.query.all()]
    
    return jsonify({
    'success': True,
    'drinks': drinks
    }, 200)
    

@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail():
    
    drinks = [drink.long() for drink in Drink.query.all()]

    return jsonify({
    'success': True,
    'drinks': drinks
    }, 200)



@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink():
    req = request.get_json()

    if 'title' and 'recipe' not in req:
        abort(422)

    my_recipe = req['recipe']
    if isinstance(my_recipe, dict):
        my_recipe = [my_recipe]

    try:
        drink_title = req['title']
        drink_recipe = json.dumps(my_recipe)

        new_Drink = Drink(
            title=drink_title,
            recipe=drink_recipe
        )

        new_Drink.insert()

    except:
        abort(400)

    return jsonify({
        'success': True,
        'drinks': [new_Drink.long()]
    }, 201)


@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('delete:drinks')
def modify_drink(id):
    req = request.get_json()
    drink = Drink.query.filter(Drink.id == id).one_or_none()

    if drink is None:
        abort(404)

    if 'title' and 'recipe' not in req:
        abort(422)

    my_recipe = req['recipe']
    if isinstance(my_recipe, dict):
        my_recipe = [my_recipe]
    
    try:
        drink_title = req['title']
        drink_recipe = json.dumps(my_recipe)

        drink.title = drink_title
        drink.recipe = drink_recipe
    except:
        abort(400)

    return jsonify({
        'success': True,
        'drinks': [drink.long() for drink in Drink.query.all()]
        })


@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(id):

    try:
        drink = Drink.query.filter(Drink.id == id).one_or_none()

        if drink is None:
            abort(404)

        drink.delete()

    except:
        abort(422)

    return jsonify({
        'success': True,
        'delete': id
    }, 200)


# Error Handling

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
