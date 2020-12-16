from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask import jsonify

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class ToDoItem(db.Model):
    __tablename__ = 'todo_items'
    id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    text = db.Column(db.Text)

    def as_dict(self):
        """
        Метод який дозволяє перетворити об'єкт типу ToDoItem в словник
        :return:
        """
        return {
            'id': self.id,
            'text': self.text
        }


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/todos', methods=['GET'])  # методом GET можна  отримати список усіх заміток (ToDoItems)
def todo_list():
    """
    Метод API який показує список ToDoItem у форматі json
    :return:
    """
    todos = ToDoItem.query.all()  # Вибираємо всі елементи з бази даних
    todos_to_dict = [todo.as_dict() for todo in todos]  # Поелементно перетворюємо їх в масив словників
    return jsonify(todos_to_dict)  # перетворюємо їх в json і видаємо на вихід


@app.route('/todos', methods=['POST'])
def create_todo():
    """
    Метод API який дозволяє створити одне ToDoItem
    :return:
    """
    request_body = request.json  # Отримуємо json на вході
    if request_body.get('text') is None:
        return jsonify({
            'error': {
                'text': "Обов'язкове поле"
            }
        }), 400 # Вертаємо додатково HTTP код 400 що означає що це невдалий запит. Детальніше (https://http.cat/400)

    # Cтворюємо замітку (ToDoItem) в базі даних
    todo = ToDoItem(text=str(request_body['text']))
    db.session.add(todo)
    db.session.commit()

    return jsonify(todo.as_dict())  # Виводимо результат з бази даних у відповідь на запит


@app.route('/todo/<int:id>', methods=['GET'])
def todo_detail(id: int):
    """
    Метод API який дозволяє подивитись інформацію про конкретне ToDoItem з id в базі даних
    :param id:
    :return:
    """
    todo = ToDoItem.query.filter_by(id=id).first()  # шукаємо в базі даних ToDoItem з id який заданий в рядку
    if todo is None:
        return jsonify({
            'error': f'Елемент з id {id} не знайдено в базі даних'
        }), 404  # Вертаємо крім опису помилки ще також код 404. Детальніше (https://http.cat/404)

    return jsonify(todo.as_dict())  # якщо елемент в базі є то просто його відображаємо у вигляді json.


@app.route('/todo/<int:id>', methods=['PUT'])
def todo_edit(id: int):
    """
     Метод API який дозволяє відредагувати текст конкретного ToDoItem з  вказаним id в базі даних
    :param id:
    :return:
    """
    todo = ToDoItem.query.filter_by(id=id).first()  # шукаємо в базі даних ToDoItem з id який заданий в рядку
    if todo is None:
        return jsonify({
            'error': f'Елемент з id {id} не знайдено в базі даних'
        }), 404  # Вертаємо крім опису помилки ще також код 404. Детальніше (https://http.cat/404)

    # Для редагування в методу доступне тільки поле text
    request_body = request.json
    if request_body.get('text') is None:
        return jsonify({
            'error': {
                'text': "Обов'язкове поле"
            }
        }), 400  # Вертаємо додатково HTTP код 400 що означає що це невдалий запит. Детальніше (https://http.cat/400)
    todo.text = request_body.get('text')
    db.session.commit()
    return jsonify(todo.as_dict())  # Після редагування відправляємо кінцевий результат


@app.route('/todo/<int:id>', methods=['DELETE'])
def todo_delete(id: int):
    """
    Метод API який дозволяє видалити  конкретний ToDoItem з  вказаним id з бази даних
    :param id:
    :return:
    """
    todo = ToDoItem.query.filter_by(id=id).first()  # шукаємо в базі даних ToDoItem з id який заданий в рядку
    if todo is None:
        return jsonify({
            'error': f'Елемент з id {id} не знайдено в базі даних'
        }), 404  # Вертаємо крім опису помилки ще також код 404. Детальніше (https://http.cat/404)

    ToDoItem.query.filter_by(id=id).delete()
    db.session.commit()
    return jsonify({}), 204  # відправляємо код 204 що означає No Content, а значить ми видалили з бази даних елемент. (https://http.cat/204)


if __name__ == '__main__':
    app.run()
