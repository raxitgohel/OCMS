from flask import *
from flask_login import LoginManager, login_user, logout_user, UserMixin, current_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_
from flask_migrate import Migrate
import os
import datetime


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['UPLOAD_FOLDER'] = 'saved_items'
app.secret_key = 'maisanskida'

# Initialize the Flask-Login extension
login_manager = LoginManager()
login_manager.init_app(app)

# initiallize database
db = SQLAlchemy(app)
migrate = Migrate(app, db)
# Create model
class User(db.Model, UserMixin):
    # id = db.Column(db.Integer, primary_key = True)
    uname = db.Column(db.String(30), primary_key=True)
    fname = db.Column(db.String(50), nullable = False)
    lname = db.Column(db.String(50), nullable = True)
    email = db.Column(db.String(50), nullable = False, unique = True)
    password = db.Column(db.String(50), nullable = False)
    designation = db.Column(db.String(10), nullable = False)

    # Create a function which returns a string when data was inserted
    def __repr__(self):
        return '<Hello, %r>' % self.uname
    
    def is_active(self):
        return True
    
    def get_id(self):
        return self.uname

class Course(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    cname = db.Column(db.String(50), nullable = False)
    cdesc = db.Column(db.String(200), nullable = False)
    teacher_uname = db.Column(db.String(30), nullable = False) 

    def __repr__(self):
        return 'Course %r created' % self.cname

class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cid = db.Column(db.Integer, nullable=False)
    student_uname = db.Column(db.String(30), nullable = False)
    
    def __repr__(self):
        return 'Student %r joined %r course' % (self.student_uname, self.cid)

class Upload(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    owner = db.Column(db.String(30), nullable=False)
    cid = db.Column(db.Integer, nullable=False)
    item_name = db.Column(db.String(200), nullable=False)
    item_path = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return 'Item %r saved at %r ' % (self.item_name, self.item_path)

# class Chat(db.Model):
#     chat_id = db.Column(db.Integer, primary_key =True, autoincrement=True)
#     creation_time = db.Column(db.DateTime, nullable=False)
#     updation_time = db.Column(db.DateTime, nullable=True)

class MessegeStore(db.Model):
    messege_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_id = db.Column(db.Integer, nullable=False)
    messege_content = db.Column(db.String(1500), nullable=False)
    sender_name = db.Column(db.String(30), nullable=False)

@login_manager.user_loader
def load_user(uname):
    return User.query.filter_by(uname=uname).first()

@app.route('/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        # msg = current_user.uname
        return redirect(url_for('home'))
    else:
        if request.method == 'POST':
            uname = request.form['uname']
            password  = request.form['password']
            user = User.query.filter_by(uname=uname).first()
            if user is not None and user.password == password:
                login_user(user)
                # session['logged_in'] = True
                # session['username'] = uname
                return redirect(url_for('home'))
            else:
                err = 'Invalid Username or Password'
                return render_template('login.html', err = err)
        return render_template('login.html')


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/home')
def home():
    if current_user.is_authenticated:
        if current_user.designation == 'teacher':
            crses = Course.query.filter_by(teacher_uname = current_user.uname).all()    
            msg = current_user.uname
            desg = current_user.designation
            return render_template('home.html', msg=msg, crses=crses, desg=desg)
        else:
            crses = Course.query.all()
            msg = current_user.uname
            desg = current_user.designation
            enr = Enrollment.query.filter_by(student_uname=msg).all()            
            enr_course_ids = [enrollment.cid for enrollment in enr]
            rem_available_courses = [course for course in crses if course.id not in enr_course_ids]
            enrolled_courses = [course for course in crses if course.id in enr_course_ids]
            return render_template('home.html', msg=msg, rem_crses=rem_available_courses, desg=desg, enr_crses=enrolled_courses)
        
    return render_template('login.html')

@app.route('/create_courses', methods = ['POST', 'GET'])
def create_courses():
    if current_user.is_authenticated:
        if request.method == 'POST':
            cname = request.form['cname']
            cdesc = request.form['cdesc']
            teacher_uname = current_user.uname
            course = Course(cname=cname, cdesc=cdesc, teacher_uname=teacher_uname)
            # Get the current date and time
            # current_datetime = datetime.datetime.now()
            # Format the date and time as a string
            # formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
            # chat = Chat(creation_time = current_datetime)
            db.session.add(course)
            # db.session.add(chat)
            db.session.commit()
            return redirect(url_for('home'))
        return render_template('create_course.html')

@app.route('/enroll', methods=['POST', 'GET'])
def enroll():
    if current_user.is_authenticated:
        cid = request.args.get('course_id')
        crs = Course.query.filter_by(id = cid).first()
        print(cid)
        if request.method=='POST':
            student_uname = current_user.uname
            enr = Enrollment.query.filter_by(cid=cid, student_uname=student_uname).first()
            if enr is None:
                enrlmnt = Enrollment(cid=cid, student_uname=student_uname)
                db.session.add(enrlmnt)
                db.session.commit()
                return render_template('enrollment_conform.html', student_uname=student_uname, cname = crs.cname)
            else:
                return 'Already enrolled!'

        return render_template('course_details.html', crs = crs)



@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        uname = request.form['uname']
        fname = request.form['fname']
        lname = request.form['lname']
        email = request.form['email']
        password = request.form['password']
        designation = request.form['desg']

        user = User(uname=uname, fname=fname, lname=lname, email=email, password=password, designation=designation)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/upload', methods=['GET','POST'])
def upload():
    if current_user.is_authenticated:
        t_uname = current_user.uname
        cid = request.args.get('course_id')
        crs = Course.query.filter_by(id=cid).first()
        enr = Enrollment.query.filter_by(cid = cid).all()
        stds=[]
        for e in enr:
            s = User.query.filter_by(uname=e.student_uname).first()
            if s:
                stds.append(s)

        items = Upload.query.filter_by(owner = t_uname, cid=cid).all()
        messeges = MessegeStore.query.filter_by(course_id = cid).all()
        if request.method=='POST':
            if 'file' in request.files:
                file = request.files['file']
                file_name = str(file.filename)
                print(file_name)
                
                if os.path.isdir(file_name):
                    folder_path = os.path.join(app.config['UPLOAD_FOLDER', file_name])
                    os.makedirs(folder_path, exist_ok=True)
                    for file in request.files.getlist('file'):
                        file_path = os.path.join(folder_path, file.filename)
                        file.save(file_path)
                    upload = Upload(owner=t_uname, cid=cid, item_name=file_name, item_path=folder_path)
                    db.session.add(upload)
                    db.session.commit()
                    return redirect(url_for('upload', course_id = crs.id))
                else:
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
                    print(file_path)
                    file.save(file_path)
                    upload = Upload(owner=t_uname, cid=cid, item_name=file_name, item_path=file_path)
                    db.session.add(upload)
                    db.session.commit()
                    return redirect(url_for('upload', course_id = crs.id))

        return render_template('course_page_for_teacher.html', t_uname=t_uname, crs=crs, items=items, enr=enr,stds=stds, messeges = messeges)

@app.route('/viewcontents')
def viewcontents():
    if current_user.is_authenticated:
        s_uname = current_user.uname
        cid = request.args.get('course_id')
        crs = Course.query.filter_by(id=cid).first()
        items = Upload.query.filter_by(owner = crs.teacher_uname, cid=cid).all()
        messeges = MessegeStore.query.filter_by(course_id = cid).all()
        return render_template('course_page_for_students.html', t_uname=crs.teacher_uname, s_uname=s_uname, crs=crs, items=items, messeges = messeges)

@app.route('/download/<filename>')
def download(filename):
    if current_user.is_authenticated:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/remove_student/<int:cid>/<string:uname>')
def remove_student(cid,uname):
    db.session.query(Enrollment).filter_by(cid=cid, student_uname=uname).delete()
    db.session.commit()
    return redirect(url_for('upload', course_id=cid))

@app.route('/send/<int:cid>/<string:uname>', methods=['POST','GET'])
def sendMsg(cid, uname):
    if request.method=='POST':
        content = request.form['msgcontent']
        msg = MessegeStore(course_id=cid, messege_content = content, sender_name=uname)
        db.session.add(msg)
        db.session.commit()
        desg = current_user.designation
        if desg=='student':
            return redirect(url_for('viewcontents', course_id=cid))
        else:
            return redirect(url_for('upload', course_id=cid))

# added later
if __name__== "__main__":
    with app.app_context():
        db.create_all()
    
    app.run(debug=True)