from flask import Flask, request, render_template
from flask.ext.restful import Resource, reqparse, abort, Api
from twilio import twiml
import plyvel
import json
import uuid

# Create the Flask web app
app = Flask(__name__, static_url_path='')

# Wire up Flask Restful
api = Api(app)

# Intialize leveldb
db = plyvel.DB('./db', create_if_missing=True)

# Define the Twilio webhook for adding tasks
@app.route('/sms', methods=['POST'])
def sms():
    todo_id = uuid.uuid1()
    todo = {'id': str(todo_id), 'task': request.form['Body']}
    db.put(str(todo_id), json.dumps(todo))
    response = twiml.Response()
    response.message("Todo added: "+ request.form['Body'])
    return str(response)

# Define 
@app.route('/', methods=['GET'])
def list():
    todos = []
    for k, v in db.iterator():
        todos.append(json.loads(v))
    return render_template('list.html', todos=todos)

# request parsing for Flask Restful
parser = reqparse.RequestParser()
parser.add_argument('task', type=str)

# load and return the task, or abort if it doesn't exist
def load_task_or_abort(todo_id):
    task = db.get(str(todo_id))
    if task is None:
      abort(404, message="Todo {} doesn't exist".format(todo_id))
    else:
      return json.loads(task)


# Todo - get, delete or modify a single task
class Todo(Resource):
    def get(self, todo_id):
        task = load_task_or_abort(todo_id)
        return task

    def delete(self, todo_id):
        load_task_or_abort(todo_id)
        db.delete(str(todo_id))
        return '', 204

    def put(self, todo_id):
        task = load_task_or_abort(todo_id)
        args = parser.parse_args()
        task['task'] = args['task']
        db.put(str(todo_id), json.dumps(task))
        return task, 201


# TodoList - get a list of all tasks or add a new task
class TodoList(Resource):
    def get(self):
        todos = []
        for k, v in db.iterator():
          todos.append(json.loads(v))
        return todos

    def post(self):
        args = parser.parse_args()
        todo_id = uuid.uuid1()
        todo = {'id': str(todo_id), 'task': args['task']}
        db.put(str(todo_id), json.dumps(todo))
        emit('new task', todo, broadcast=True)
        return todo, 201


# Setup the Api resource routing 
api.add_resource(TodoList, '/todos')
api.add_resource(Todo, '/todos/<string:todo_id>')

# Initialize and start the web application
if __name__ == "__main__":
    app.run()
