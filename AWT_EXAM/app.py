from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Session(db.Model):
    username = db.Column(db.Text, primary_key=True)

    def __repr__(self):
        return f'<Session : {self.username}>'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<{self.id} : {self.title}>'

def isAdmin() -> bool:
    session = Session.query.filter_by(username='admin').first()
    if (session):
        return True
    return False

@app.route('/')
def main():
    blogs = Blog.query.all()
    return render_template('home.html', blogs=blogs, isAdmin=isAdmin())

@app.route('/blog/<int:id>')
def blog(id):
    blog_details = Blog.query.filter_by(id=id).first()
    return render_template('blog.html', blog_details=blog_details, isAdmin=isAdmin())

@app.route('/blog/<int:id>/edit', methods=['GET', 'POST'])
def blog_edit(id):
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        blog = Blog.query.filter_by(id=id).first()
        blog.title = title
        blog.content = content
        db.session.add(blog)
        db.session.commit()
        return redirect('/')
    blog_details = Blog.query.filter_by(id=id).first()
    return render_template('blog_edit.html', blog_details=blog_details, isAdmin=isAdmin())

@app.route('/blog/<int:id>/delete')
def blog_delete(id):
    blog = Blog.query.filter_by(id=id).first()
    db.session.delete(blog)
    db.session.commit()
    return redirect('/admin')

@app.route('/post', methods=['GET', 'POST'])
def blog_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        new_blog = Blog(title=title, content=content)
        db.session.add(new_blog)
        db.session.commit()
        return redirect('/blog/' + str(new_blog.id))
    return render_template('blog_post.html', isAdmin=isAdmin())

@app.route('/admin')
def admin():
    blogs = Blog.query.all()
    return render_template('admin.html', blogs=blogs, isAdmin=isAdmin())

@app.route('/logout')
def logout():
    session = Session.query.filter_by(username='admin').first()
    db.session.delete(session)
    db.session.commit()
    return redirect('/')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if (username == 'admin' and password == 'admin'):
            db.session.add(Session(username='admin'))
            db.session.commit()
            return redirect('/post')
        else:
            return redirect('/login')

    return render_template('login.html')

if __name__ == "__main__":
    app.run(debug=True)
