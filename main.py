from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy
from config import username, password, host, port, database, app_secret_key
from datetime import datetime
import hashlib

app = Flask(__name__)
app.config['DEBUG'] = False
app.config['ENV'] = 'development'
app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCEMY_TRACK_MODIFICATIONS'] = False

connection_string = f'mysql+pymysql://{username}:{password}@{host}:{port}/{database}'
app.config['SQLALCHEMY_DATABASE_URI'] = connection_string
db = SQLAlchemy(app)
db_session = db.session
app.secret_key = app_secret_key

class Blog(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(140))
  content = db.Column(db.Text)
  created_at = db.Column(db.DateTime, default=datetime.now())
  created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

  @classmethod
  def all(cls, order_by=None):
    q = cls.query
    if order_by:
      q = q.order_by(order_by)      
    return q.all()
  
  @classmethod
  def get(cls,id):
    return cls.query.get(id)

class Users(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(40))
  password = db.Column(db.String(40))

  blogs = db.relationship('Blog',backref='users')

  @classmethod
  def all(cls, order_by=None):
    q = cls.query
    if order_by:
      q = q.order_by(order_by)      
    return q.all()
  
  @classmethod
  def get(cls,id):
    return cls.query.get(id)

@app.before_request
def require_login():
  not_allowed_routes=['logout', 'newpost', 'editpost', 'addblog' ] 
  print("The current end point is ",request.endpoint)
  if request.endpoint in not_allowed_routes and ('username' not in session):
    return redirect('/login')

@app.route("/blog")
def blog():
  if(request.args.get('id')):
    _id = request.args['id']
    blog = Blog.get(_id)
    user = Users.get(blog.created_by)
    errormsg = request.args.get('error')
    return render_template("blogdetails.html",blog=blog,username=user.username,errormsg=errormsg)
  
  elif(request.args.get('user')):
    _user = request.args['user']
    user = Users.get(_user)
    if(user):
      blog = Blog.query.filter_by(created_by=_user)
      return render_template("userblogs.html",blog=blog,username=user.username)
  else:
    return redirect("/")

@app.route("/signup", methods = ['POST', 'GET'])
def signup():
  if request.method == 'POST':
    requested_username = request.form.get('username')
    requested_password = request.form.get('password')
    confirm_password = request.form.get('verifypassword')
    user = Users.query.filter_by(username=requested_username).first()
    if user:
      errormsg = "Username Already Exists - Please try with another username"
      return redirect(f"/signup?error={errormsg}")
    elif requested_username and requested_password:
      if (requested_password == confirm_password):
        newuser = Users()
        newuser.username = requested_username
        h = hashlib.new('md5')
        usr_psswd = bytes(request.form.get('password'),'utf-8')
        h.update(usr_psswd)
        encrypted_password = h.hexdigest()
        newuser.password = encrypted_password
        db_session.add(newuser)
        db_session.commit()
        session['username'] = requested_username
        return redirect("/newpost")
      else:
        errormsg = "You password should match with the Verify password"
        return redirect(f"/signup?error={errormsg}")
    else:
        errormsg = "Username and password are mandatory"
        return redirect(f"/signup?error={errormsg}")
  elif request.method == 'GET':
    errormsg = request.args.get('error')
    return render_template('signup.html', errormsg=errormsg)

@app.route('/logout')
def logout():
  del session['username']
  return redirect("/")

@app.route("/login", methods=['POST','GET'])
def login():
  if request.method == 'POST':
    usrName = request.form.get('username')
    hh = hashlib.new('md5')
    usr_psswd = bytes(request.form.get('password'),'utf-8')
    hh.update(usr_psswd)
    encrypted_password = hh.hexdigest()
    if usrName and password:
      user = Users.query.filter_by(username = usrName).first()
      if user:
        if user.password == encrypted_password:
          session['username'] = usrName
          return redirect("/")
        else:
          errormsg = "Username and password is not matching"
          return redirect(f"/login?error={errormsg}")
      else:
          errormsg = "Username doesn't exist please try login again or register new"
          return redirect(f"/login?error={errormsg}")
  else:
    errormsg = request.args.get('error')
    return render_template('login.html', errormsg=errormsg)

@app.route("/")
def index():
  users = Users.all(order_by='username desc')
  return render_template("index.html", users=users)

@app.route("/newpost", methods =['GET'])
def newpost():
  return render_template("add-a-blog.html")

@app.route("/editpost", methods=['POST','GET'])
def editpost():
  if request.method == 'GET':
    _id = request.args['id']
    blog = Blog.get(_id)
    createdby = blog.created_by
    user = Users.get(createdby)
    if user.username == session['username']:
      return render_template("editpost.html",blog=blog)
    else:
      errormsg = "You can edit only your posts and not others"
      return redirect(f"/blog?id={_id}&error={errormsg}")
  elif request.method == 'POST':
    _id = request.form.get('id')    
    blog = Blog.get(_id)
    createdby = blog.created_by
    user = Users.get(createdby)
    if user.username == session['username']:
      blog.title = request.form['title']
      blog.content = request.form['content']
      db_session.add(blog)
      db_session.commit()
      return redirect(f"/blog?id={_id}")
    else:
      errormsg = "You can edit only your posts and not others"
      return redirect(f"/blog?id={_id}&error={errormsg}")

@app.route("/addblog", methods=['POST'])
def addblog():
  blog = Blog()
  for item, value in request.form.items():
    print(f'{item} = {value}')
  blog.title = request.form['title']
  blog.content = request.form['content'] 
  loggeduser = session['username']
  user = Users.query.filter_by(username = loggeduser).first()
  blog.created_by = user.id
  db_session.add(blog)
  db_session.commit()
  blogposts = Blog.all()
  return redirect(f"/?id={blogposts[-1].id}")

def main():
  from sqlalchemy import create_engine, inspect
  from sqlalchemy.exc import OperationalError
    
  try:
      ENGINE = create_engine(connection_string)
      INSPECTOR = inspect(ENGINE)  # used for checking if tables exist on startup
      # check if tables exist - create if they do not
      tables = INSPECTOR.get_table_names()
      if not tables:
          db.create_all()
  except OperationalError:
      print("Operational Error, Turn on MAMP")   

  app.run()

if __name__ == '__main__':
  main()