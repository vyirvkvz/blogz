from flask import Flask, request, redirect, render_template, flash, session
from flask_sqlalchemy import SQLAlchemy
import cgi

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:root@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'Its a secret'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(2000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    username = db.Column(db.String(120),unique=True)
    password = db.Column(db.String(120))
    blog_posts = db.relationship('Blog',backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = User.query.all()
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            session['username'] = username
            flash('Logged in')
            return redirect('/newpost')
        else:
            flash('User password incorrect, or user does not exist', 'error')
    
    return render_template('login.html')

@app.route('/signup', methods=['GET' , 'POST'])
def signupForm():
    if request.method == 'GET':
        return render_template('signup.html')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verifyPassword = request.form['verifyPassword']
        users = User.query.all()

        usernameError = ''
        passwordError = ''
        verifyError = ''

    # USERNAME REQUIREMENTS
        if len(username) <3 or len(username) > 10:
            usernameError = "Username must be 3 to 10 characters"
            username = ''
        elif ' ' in username or ' ' in username:
            usernameError = 'Username cannot contain spaces.'

        if not password:
            passwordError = 'Please enter a password.'
        elif len(password) <3 or len(password) >20:
            passwordError = 'Passwords must be between 3 and 20 characters in length.'
        elif ' ' in password or '   ' in password:
            passwordError = 'Passwords cannot contain spaces.'

    # PASSWORD ERROR - DO THE PASSWORDS MATCH
        if password != verifyPassword:
            passwordError = "Passwords do not match"
            password = ''
        else:
            password = password

    # PASSWORD VERIFICATION
        if verifyPassword != password:
            verifyError = "Passwords do not match"
            password = ''
            verifyPassword = ''
        else:
            password = password
            verifyPassword = verifyPassword

        existing_user = User.query.filter_by(username=username).first()
        if not usernameError and not passwordError and not verifyError:
            if request.method == 'POST':
                new_user = User(username , password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                return redirect('/newpost')
        else:
            return render_template('signup.html', 
            username = username,
            usernameError = usernameError,
            password = password,
            passwordError = passwordError,
            verifyPassword = verifyPassword,
            verifyError = verifyError,
            )
    
    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/login')

@app.before_request
def require_login():
    allowed_routes = ['signupForm' , 'login' , 'index', 'blog_list']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/', methods=['GET']) 
def index():
    users = User.query.all()
    return render_template('index.html' , users = users)

@app.route('/blog', methods=["POST", "GET"])
def blog_list():
    if request.method == 'GET':
        if 'id' in request.args:
            IDblog = request.args.get('id')
            blogging= Blog.query.get(IDblog)
            owner = blogging.owner
            return render_template('blogpost.html', blogging=blogging, owner=owner)
 
        if 'user' in request.args:
            username = request.args.get('user')
            owner = User.query.filter_by(username = username).first()
            user_post = Blog.query.filter_by(owner = owner).all()
            return render_template('singleUser.html', user_post=user_post, 
            owner = owner,) 

    entries = Blog.query.all()
    users = User.query.all()
    return render_template('blog.html', 
    entries = entries, 
    users=users,
    )

@app.route('/newpost', methods=['GET', 'POST'])
def nPost():
  
    if request.method == 'POST':
        blogTitle = request.form['blogTitle']
        blogBody = request.form['blogBody']

        titleError = ''
        bodyError = ''

        if blogTitle == '':
            titleError = 'Please fill in the title'

        if blogBody == '':
            bodyError = 'Please fill in the body'

        if not titleError and not bodyError:
            if request.method == 'POST':
                blogTitle = request.form['blogTitle']
                blogBody = request.form['blogBody']
                owner = User.query.filter_by(username =session['username']).first()
                newPost = Blog(blogTitle , blogBody, owner)
                db.session.add(newPost)
                db.session.commit()
            return render_template('blogview.html' , blogTitle = blogTitle , blogBody = blogBody, owner = owner)
        else:
            return render_template('newpost.html',
            bodyError = bodyError,
            titleError = titleError,
            blogTitle = blogTitle, 
            blogBody = blogBody)

    if request.method == 'GET':
        return render_template('newpost.html')

if __name__ == '__main__':
    app.run()