from flask import Flask, request, render_template
from flask.ext.restful import Api, Resource, reqparse, abort
from twilio import twiml
import plyvel
import json
import uuid

app = Flask(__name__)

# Wire up Flask Restful
api = Api(app)

# Intialize leveldb
db = plyvel.DB('./db', create_if_missing=True)

# load and return the todo, or abort if it doesn't exist
def load_todo_or_abort(todo_id):
    todo = db.get(str(todo_id))
    if todo is None:
        abort(404, message="Todo {} doesn't exist".format(todo_id))
    else:
        return json.loads(todo)

# Todo - get, delete or modify a single todo
class Todo(Resource):
    def get(self, todo_id):
        todo = load_todo_or_abort(todo_id)
        return todo

    def delete(self, todo_id):
        load_todo_or_abort(todo_id)
        db.delete(str(todo_id))
        return '', 204

    def put(self, todo_id):
        todo = load_todo_or_abort(todo_id)
        args = parser.parse_args()
        todo['todo'] = args['todo']
        db.put(str(todo_id), json.dumps(todo))
        return todo, 201

# TodoList - get a list of all todos or add a new todo
class TodoList(Resource):
    def get(self):
        todos = []
        for k, v in db.iterator():
            todos.append(json.loads(v))
        return todos

    def post(self):
        args = parser.parse_args()
        todo_id = uuid.uuid1()
        todo = {'id': str(todo_id), 'todo': args['todo']}
        db.put(str(todo_id), json.dumps(todo))
        return todo, 201

# request parsing for Flask Restful
parser = reqparse.RequestParser()
parser.add_argument('todo', type=str)

# Setup the Api resource routing 
api.add_resource(TodoList, '/todos')
api.add_resource(Todo, '/todos/<string:todo_id>')



@app.route('/', methods=['GET'])
def list():
    todos = []
    for k, v in db.iterator():
        todos.append(json.loads(v))
    return render_template('list.html', todos=todos)

# Define the Twilio webhook for adding todos
@app.route('/sms', methods=['POST'])
def sms():
    todo_id = uuid.uuid1()
    todo = {
        'id': str(todo_id), 
        'todo': request.form['Body']}
    db.put(str(todo_id), json.dumps(todo))
    response = twiml.Response()
    response.message('Thanks!')
    return str(response)

# Initialize and start the web application
if __name__ == "__main__":
    app.run()
