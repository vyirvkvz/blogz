from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:root@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(2000))

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/', methods=['GET']) 
def index():
    return redirect('/blog')

@app.route('/blog')
def blog_list():

    id = request.args.get('id')
    if id:
        id = request.args.get('id')
        blog = Blog.query.filter_by(id=id).first()
        bBody = blog.body
        bTitle = blog.title
        return render_template('blogview.html', bBody=bBody, bTitle=bTitle)

    blog_posts = Blog.query.all()
    return render_template('blog.html', blog_posts=blog_posts)


@app.route('/newpost', methods=['GET', 'POST'])
def nPost():

    if request.method == 'POST':

        blogTitle = request.form['blogTitle']
        blogBody = request.form['blogBody']
        nPost = Blog(blogTitle, blogBody)

        titleError = ''
        bodyError = ''

        if blogTitle == '':
            titleError = 'Please fill in the title'

        if blogBody == '':
            bodyError = 'Please fill in the body'

        if not titleError and not bodyError:
            db.session.add(nPost)
            db.session.commit()
            id = str(nPost.id)
            return redirect('/blog?id={}'.format(id))
        else:
            return render_template('newpost.html',bodyError=bodyError,
            titleError=titleError,
            blogTitle=blogTitle, blogBody=blogBody)


    # retrieve all entries from database
    blog_posts = db.session.query(Blog)

    return render_template('newpost.html')

if __name__ == '__main__':
    app.run()