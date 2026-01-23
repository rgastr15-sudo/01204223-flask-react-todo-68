from flask import Flask, request, jsonify
from flask_cors import CORS

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

app = Flask(__name__)
CORS(app)

# ---------- SQLAlchemy setup ----------

class Base(DeclarativeBase):
    pass

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(model_class=Base)
db.init_app(app)

# ---------- Model ----------

class TodoItem(db.Model):
    __tablename__ = 'todos'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    done: Mapped[bool] = mapped_column(default=False)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "done": self.done
        }

# ---------- Create database & tables ----------

with app.app_context():
    db.create_all()

INITIAL_TODOS = [
    TodoItem(title='Learn Flask'),
    TodoItem(title='Build a Flask App'),
]

with app.app_context():
    if TodoItem.query.count() == 0:
        for item in INITIAL_TODOS:
            db.session.add(item)
        db.session.commit()


# ---------- Temporary in-memory list (legacy) ----------
# ใช้ชั่วคราวสำหรับ POST / PATCH / DELETE

todo_list = []

# ---------- Routes ----------

# READ (from database)
@app.route('/api/todos/', methods=['GET'])
def get_todos():
    todos = TodoItem.query.all()
    return jsonify([todo.to_dict() for todo in todos])

# helper function (legacy)
def new_todo(data):
    if len(todo_list) == 0:
        new_id = 1
    else:
        new_id = 1 + max([todo['id'] for todo in todo_list])

    if 'title' not in data:
        return None

    return {
        "id": new_id,
        "title": data['title'],
        "done": data.get('done', False),
    }

# CREATE (legacy – ยังไม่ใช้ DB)
@app.route('/api/todos/', methods=['POST'])
def add_todo():
    data = request.get_json()
    todo = new_todo(data)
    if todo:
        todo_list.append(todo)
        return jsonify(todo)
    else:
        return jsonify({'error': 'Invalid todo data'}), 400

# UPDATE (legacy)
@app.route('/api/todos/<int:id>/toggle/', methods=['PATCH'])
def toggle_todo(id):
    todos = [todo for todo in todo_list if todo['id'] == id]
    if not todos:
        return jsonify({'error': 'Todo not found'}), 404

    todo = todos[0]
    todo['done'] = not todo['done']
    return jsonify(todo)

# DELETE (legacy)
@app.route('/api/todos/<int:id>/', methods=['DELETE'])
def delete_todo(id):
    global todo_list
    todos = [todo for todo in todo_list if todo['id'] == id]
    if not todos:
        return jsonify({'error': 'Todo not found'}), 404

    todo_list = [todo for todo in todo_list if todo['id'] != id]
    return jsonify({'message': 'Todo deleted successfully'})
