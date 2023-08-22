from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Feedback
from forms import UserForm, LoginForm, DeleteForm, FeedbackForm

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///auth_exercise'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = 'secret'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)

toolbar = DebugToolbarExtension(app)


@app.route('/')
def home_page():
    return redirect('/register')

@app.route('/register', methods=['GET', 'POST'])
def register_user():
    form = UserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        user = User.register(username, password, email, first_name, last_name)

        db.session.add(user)
        db.session.commit()

        session['username'] = user.username

        return redirect(f'/users/{user.username}')
    
    return render_template('users/register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_user():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)
        if user:
            session['username'] = user.username
            return redirect(f'/users/{user.username}')
        else:
            form.username.errors = ['Invalid username/password.']
    
    return render_template('users/login.html', form=form)

@app.route('/logout')
def logout_user():
    session.pop('username')
    return redirect('/')
    
@app.route('/users/<username>')
def user_page(username):
    if 'username' not in session or username != session['username']:
        return redirect('/')
    user = User.query.get(username)
    return render_template('users/user.html', user=user)

@app.route('/users/<username>/delete', methods=['POST'])
def delete_user(username):
    if 'username' not in session or username != session['username']:
        return redirect('/users/<username>')
    user = User.query.filter_by(username=username).first()

    if user.username == session['username']:
        db.session.delete(user)
        db.session.commit()
        session.pop('username')
    return redirect('/')

@app.route('/users/<username>/feedback/add', methods=['GET', 'POST'])
def add_feedback(username):
    if 'username' not in session or username != session['username']:
        return redirect('/users/<username>')
    
    form = FeedbackForm()
    user = User.query.get(username)

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data

        feedback = Feedback(title=title, content=content, username=username)

        db.session.add(feedback)
        db.session.commit()

        return redirect(f'/users/{feedback.username}')
    
    else:
        return render_template('feedback/new.html', form=form, user=user)
    
@app.route('/feedback/<feedback_id>/update', methods=['GET', 'POST'])
def update_feedback(feedback_id):
    feedback = Feedback.query.get(feedback_id)

    if 'username' not in session or feedback.username != session['username']:
        return redirect('/users/<username>')
    
    form = FeedbackForm(obj=feedback)

    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data
    
        db.session.commit()

        return redirect(f'/users/{feedback.username}')

    else:
        return render_template('feedback/new.html', form=form, user=feedback.username)
    
@app.route('/feedback/<feedback_id>/delete', methods=['POST'])
def delete_feedback(feedback_id):
    feedback = Feedback.query.get(feedback_id)
    
    if 'username' not in session or feedback.username != session['username']:
        return redirect('/users/<username>')
    
    form = DeleteForm()

    if form.validate_on_submit():
        db.session.delete(feedback)
        db.session.commit()
    
    return redirect(f'/users/{feedback.username}')