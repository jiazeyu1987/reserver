from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# 创建最小的Flask应用
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# 定义模型
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)

@app.route('/')
def index():
    return "Hello World!"

def create_tables():
    with app.app_context():
        print(f"db.metadata.tables: {db.metadata.tables}")
        db.create_all()
        print("表创建完成")
        
        # 检查表是否真的创建了
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"数据库中的表: {tables}")

if __name__ == '__main__':
    create_tables()
    app.run(debug=True)