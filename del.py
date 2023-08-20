from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app import MessegeStore, Upload
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)



@app.route('/delete_all')
def delete_all():
    # db.session.query(MessegeStore).delete()
    # MessegeStore.__table__.drop(db.engine)
    # Upload.__table__.drop(db.engine)
    # db.session.commit()
    return 'All rows deleted from the table'

if __name__ == '__main__':
    app.run()
