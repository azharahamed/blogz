from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from config import username, password, host, port, database
from datetime import datetime

app = Flask(__name__)
app.config['DEBUG'] = True
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

@app.route("/")
def index():
  if(request.args):
    # print(f'Blog Id passed through url {request.args["id"]}')
    _id = request.args['id']
    blog = Blog.query.filter_by(id=_id).first()
    return render_template("blogdetails.html",blog=blog)
  else:
    return redirect("/blog")

@app.route("/blog")
def blog():
  blogposts = Blog.query.all()
  return render_template("index.html", blogposts=blogposts)

@app.route("/newpost")
def newblog():
  return render_template("add-a-blog.html")

@app.route("/addblog", methods=['POST'])
def addconfirmation():
  blog = Blog()
  for item, value in request.form.items():
    print(f'{item} = {value}')
  blog.title = request.form['title']
  blog.content = request.form['content'] 
  db.session.add(blog)
  db.session.commit()
  blogposts = Blog.query.all()
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

  blogposts = Blog.query.all()
  print(blogposts)      
  app.run()

if __name__ == '__main__':
  main()