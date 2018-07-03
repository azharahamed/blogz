from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from config import username, password, host, port, database
from datetime import datetime

app = Flask(__name__)
app.config['DEBUG'] = False
app.config['ENV'] = 'development'
app.config['SQLALCHEMY_ECHO'] = True

connection_string = f'mysql+pymysql://{username}:{password}@{host}:{port}/{database}'
app.config['SQLALCHEMY_DATABASE_URI'] = connection_string
db = SQLAlchemy(app)
db_session = db.session

class Blog(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(140))
  content = db.Column(db.Text)
  created_at = db.Column(db.DateTime, default=datetime.now())

  @classmethod
  def all(cls, order_by=None):
    q = cls.query
    print("q = ",q)
    print("order by", order_by)
    if order_by:
      q = q.order_by(order_by)      
    return q.all()
  
  @classmethod
  def get(cls,id):
    return cls.query.get(id)

@app.route("/")
def index():
  if(request.args):
    _id = request.args['id']
    blog = Blog.get(_id)
    return render_template("blogdetails.html",blog=blog)
  else:
    return redirect("/blog")

@app.route("/blog")
def blog():
  blogposts = Blog.all(order_by='created_at desc')
  return render_template("index.html", blogposts=blogposts)

@app.route("/newpost")
def newblog():
  return render_template("add-a-blog.html")

@app.route("/editpost", methods=['POST','GET'])
def editpost():
  if request.method == 'GET':
    _id = request.args['id']
    blog = Blog.get(_id)
    return render_template("editpost.html",blog=blog)
  elif request.method == 'POST':
    _id = request.form.get('id')    
    blog = Blog.get(_id)
    blog.title = request.form['title']
    blog.content = request.form['content']
    db_session.commit()
    return redirect(f"/?id={_id}")

@app.route("/addblog", methods=['POST'])
def addconfirmation():
  blog = Blog()
  for item, value in request.form.items():
    print(f'{item} = {value}')
  blog.title = request.form['title']
  blog.content = request.form['content'] 
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