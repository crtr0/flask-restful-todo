# Flask Restful & LevelDB ToDo app

## Setup

If you don't have virtualenv:

`pip install virtualenv`

1) Install LevelDB libraries on your system. Here is an example of using [Homebrew]() to install on Mac OSX:

`brew install leveldb`

2) Clone this repo

`git clone <this repo>`

3) Set-up virtualenv and install dependencies

`virtualenv venv`
`source venv/bin/activate`
`pip install -r requirements.txt --use-mirrors`

## Running

`python app.py`

Now that the server is running, test it out:

`curl http://localhost:5000/todos`

Will return an empty array: []

`curl -X POST http://localhost:5000/todos -d "task=do dishes"`

Will return a new task object that looks like:

{"task": "do dishes", "id": "xxxxx"}

`curl http://localhost:5000/todos`

Will return an array with the new task inside: 

[{"task": "do dishes", "id": "xxxxx"}]

`curl http://localhost:5000/todos/xxxxx`

Will return the task object with that id:

{"task": "do dishes", "id": "xxxxx"}

`curl http://localhost:5000/todos/xxxxx -X PUT -d 'task=wash the dishes'`

Will return the modified object:

{"task": "wash the dishes", "id": "xxxxx"}

`curl http://localhost:5000/todos/xxxxx -X DELETE`

Will delete the task from the DB, no return value.

`curl http://localhost:5000/todos`

Will once again return an empty list: []


