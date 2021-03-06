# -*- encoding: utf-8 -*-
import logging
import os, sys
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from pymongo import MongoClient
from gridfs import GridFS
import base64
import bcrypt
salt = bcrypt.gensalt()

client = MongoClient()
client = MongoClient('localhost', 27017)
client = MongoClient('mongodb://localhost:27017')
db = client.webserver
authen = db.authen
product = db.product
# from logging.config import dictConfig

UPLOAD_FOLDER = './static/uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

authenNowMemory = []
authenMemory = []
postMemory = []

tempSecurityLogin = []
roundLogin = []


# dictConfig({
#     'version': 1,
#     'formatters': {'default': {
#         'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
#     }},
#     'handlers': {'wsgi': {
#         'class': 'logging.StreamHandler',
#         'stream': 'ext://flask.logging.wsgi_errors_stream',
#         'formatter': 'default'
#     }},
#     'root': {
#         'level': 'INFO',
#         'handlers': ['wsgi']
#     }
# })

registerFailPage = '''<!DOCTYPE html>
<html lang="en">
<head>
     <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css" integrity="sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO" crossorigin="anonymous">
    <meta charset="UTF-8">
    <title>Register</title>
</head>
<body style="text-align:center;font-family:Frostbite Boss Fight;background-image: url('../static/image/windowBack.jpg')">
<div class="jumbotron jumbotron-fluid" style="text-align:center;background-color:black;color:white"">
  <div class="container">
    <h1 class="display-1">Register</h1>
  </div>
</div>
<div style="text-align:center;color:white">
    <div class="alert alert-warning" role="alert">
      {}
    </div>
    <form method="POST" action="http://localhost:9000/register">
    <p><h1>Register</h1></p>
        <label class="lead">Username : <input type="text" name="username" class="form-control"></label>
    <br>
        <label class="lead">Password : <input type="password" name="password" class="form-control"></label>
    <br>
        <label class="lead">Confirm Password : <input type="password" name="confirmPassword" class="form-control"></label>
    <br>
        <label class="lead">Name : <input type="text" name="name" class="form-control"></label>
    <br>
        <label class="lead">Address : <input type="text" name="address" class="form-control"></label>
    <br>
    <button type="submit" class="btn btn-secondary">Register</button>
    </form>
    <br>
    <form method="GET" action="http://localhost:9000/login">
    <button type="submit" class="btn btn-secondary">Back</button>
    </form>
</div>
</body>
</html>'''
loginFailPage = '''<!DOCTYPE html>
<html lang="en">
<head>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css" integrity="sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO" crossorigin="anonymous">

    <meta charset="UTF-8">
    <title>OhmShop</title>
</head>
<body style="background-image: url('../static/image/windowBack.jpg')">
<div class="jumbotron jumbotron-fluid" style="text-align:center;background-color:black">
  <div class="container" style="color:white;font-family:Frostbite Boss Fight">
    <h1 class="display-1">Authentication</h1>
    <p class="lead">Welcome</p>
  </div>
</div>
<div class="alert alert-warning" role="alert">
  {}
</div>
        <form method="POST" action="http://localhost:9000/index">
            <div class="form-group" style="text-align:center;font-family:Frostbite Boss Fight;color:white">
                <label class="lead">username : <input type="text" name="username" class="form-control"></label>
                <br>
                <label class="lead">password : <input type="password" name="password" class="form-control"></label>
                <br>
                <button type="submit" class="btn btn-secondary" ><h5 class="display-5">Login</h5></button>
            </div>
        </form>

<div style="text-align:center;">
    <form method="GET" action="http://localhost:9000/register">
        <button type="submit" class="btn btn-secondary"><h5 class="display-5">Register</h5></button>
    </form>
</div>
</body>
</html>
'''
_initIndexPostPage = '''<!DOCTYPE html>
<html lang="en">
<head>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css" integrity="sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO" crossorigin="anonymous">
    <meta charset="UTF-8">
    <title>OhmShop</title>
</head>
<body>
  <div class="jumbotron jumbotron-fluid" style="text-align:center;">
    <div class="container">
      <h1 class="display-1">Ohm shop</h1>
      <p class="lead">Welcome to ohm shop</p>
    </div>
  </div>
  <div class="row" style="text-align:center;">
    <div class="col-2">
      <p class="lead">Welcome Ohm</p>
        <form method="GET" action="http://localhost:9000/">
            <button type="submit">Log out</button>
        </form>
    </div>
    <div class="col-10">
        {}{}
        <form method=post enctype=multipart/form-data action="http://localhost:9000/postImage">
          <p>
              <input type=file name=file>
              <input type=submit value=Upload>
          </p>
        </form>
        ข้อความประกาศขาย
        <form method="POST" action="http://localhost:9000/postText">
            <textarea name="message"></textarea>
            <br>
            <label>
                เบอร์โทรติดต่อ : <input type=text name=telephone class="form-control">
            </label>
            <br>
            <label>
                อีเมล : <input type=text name=email class="form-control">
            </label>
            <br>
            <button type="submit">POST</button>
        </form>
    </div>
  </div>
</body>
</html>
'''
initIndexPostPage = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>OhmShop</title>
    <!-- Bootstrap core CSS-->
    <link href="./static/vendor/bootstrap/css/bootstrap.min.css" rel="stylesheet">

    <!-- Custom fonts for this template-->
    <link href="./static/vendor/fontawesome-free/css/all.min.css" rel="stylesheet">

    <!-- Page level plugin CSS-->
    <link href="./static/vendor/datatables/dataTables.bootstrap4.css" rel="stylesheet">

    <!-- Custom styles for this template-->
    <link href="./static/css/sb-admin.css" rel="stylesheet">

    <!-- <link rel=stylesheet type=text/css href="static/css/bootstrap.min.css">
     <link rel=stylesheet type=text/css href="static/css/sb-admin.css">-->
</head>
<body id="page-top" style="text-align:center;font-family:Frostbite Boss Fight;background-image: url('../static/image/background1.jpeg')">
<nav class="navbar navbar-expand-lg navbar-dark bg-dark fixed-top">
      <div class="container">
        <a class="navbar-brand" href="#">Center shop</a>
        <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarResponsive" aria-controls="navbarResponsive" aria-expanded="false" aria-label="Toggle navigation">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarResponsive">
          <ul class="navbar-nav ml-auto">
            <li class="nav-item active">
              <a class="nav-link" href="http://localhost:9000/index" methods="get">Home
                <span class="sr-only">(current)</span>
              </a>
            </li>
            <li class="nav-item">
              <a class="nav-link" href="http://localhost:9000/about" methods="get">About</a>
            </li>
            <li class="nav-item">
              <a class="nav-link" href="http://localhost:9000/contact" methods="get">Contact</a>
            </li>
          </ul>
        </div>
      </div>
    </nav>
<br>
<br>
<div id="wrapper">
 <!-- Sidebar -->
      <ul class="sidebar navbar-nav ">
        <li class="nav-item dropdown">
          <a class="nav-link dropdown-toggle" href="#" id="pagesDropdown" role="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
            <i class="fas fa-fw fa-table"></i>
            <span>Markets</span>
          </a>
          <div class="dropdown-menu" aria-labelledby="pagesDropdown">
            <h6 class="dropdown-header">Post item</h6>
            <a class="dropdown-item">
            <button type="button" class="btn btn-secondary" data-toggle="modal" data-target="#exampleModal" data-whatever="@mdo">Create post</button>


          <div class="dropdown-divider"></div>
              <h6 class="dropdown-header">sell record</h6>
            <a class="dropdown-item" href="404.html">
                <table class="table table-bordered">
                    <thead>
                      <tr>
                        <th>Item</th>
                      </tr>
                    </thead>
                    <tbody>
                      {}
                    </tbody>
                  </table>
            </a>
          </div>
        <li class="nav-item dropdown">
          <a class="nav-link dropdown-toggle" href="#" id="pagesDropdown1" role="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
            <i class="fas fa-fw fa-folder"></i>
            <span>My Profile</span>
          </a>
          <div class="dropdown-menu" aria-labelledby="pagesDropdown1">
             <p> Name : {}</p>
             <br>
                <p>Address : {}</p>
          </div>
      </li>
        <li class="nav-item">
          <a class="nav-link" href="http://localhost:9000/login" method="get">
            <i class="fas fa-fw fa-folder"></i>
            <span>Log out</span></a>
        </li>
      </ul>
    {}
</div>


<!-- Bootstrap core JavaScript-->

<!-- Bootstrap core JavaScript-->
<script src="./static/vendor/jquery/jquery.min.js"></script>
<script src="./static/vendor/bootstrap/js/bootstrap.bundle.min.js"></script>
<script src="./static/vendor/jquery-easing/jquery.easing.min.js"></script>
<script src="./static/vendor/datatables/jquery.dataTables.js"></script>
<script src="./static/vendor/datatables/dataTables.bootstrap4.js"></script>
<script src="./static/js/sb-admin.min.js'"></script>

<div class="modal fade" id="exampleModal" tabindex="-1" role="dialog" aria-labelledby="exampleModalLabel" aria-hidden="true">
  <div class="modal-dialog" role="document">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title" id="exampleModalLabel">Create product</h5>
        <button type="button" class="close" data-dismiss="modal" aria-label="Close">
          <span aria-hidden="true">&times;</span>
        </button>
      </div>
      <div class="modal-body">
        <form method=post enctype=multipart/form-data action="http://localhost:9000/postImage">
              <p><input type=file name=file>
                 <input type=submit value=Upload>
                 <br>
                 {}
            </form>
            <form method="POST" action="http://localhost:9000/postText">
            <label>
                ชื่อสินค้า : <input type=text name="name" class="form-control">
            </label>
             <br>
                 <label>
                ราคา : <input type=text name="cost" class="form-control">
            </label>
                <br>
                 ข้อความประกาศขาย
            <textarea name="message" class="form-control" rows="2"></textarea>
            <br>
            <label>
                เบอร์โทรติดต่อ : <input type=text name=telephone class="form-control">
            </label>
            <br>
            <label>
                อีเมล : <input type=text name=email class="form-control">
            </label>
            <br>
        </a>
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>
        <button type="submit" class="btn btn-secondary">Post</button>
      </div>
      </form>
    </div>
  </div>
</div>


</body>
</html>
'''
indexPostPage = []

boxPostMem = []
boxPost = '''
<br>
<div class="container">

                <div class="card mt-4" style="text-align:center">
                        <img class="card-img-top img-fluid center" src="static/uploads/{}" alt="" style="width:50%;height:50%;">
                        <div class="card-body">
                            <h3 class="card-title">{}</h3>
                            <h4>{} บาท</h4>
                            <p class="card-text">{}</p>
                            <h4>เบอร์ติดต่อ : {}</h4>
                            <h4>email : {}</h4>
                            <h4>ชื่อผู้ขาย : {}</h4>
                        </div>
                </div>

    </div>
    <br>'''

sellMem = []
buyMem = []

imageMem = []

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/inde")
def inde():
    return redirect("http://localhost:9000/",302)

@app.route("/ind")
def ind():
    return redirect("http://localhost:9000/",302)

@app.route("/in")
def in_():
    return redirect("http://localhost:9000/",302)

@app.route("/i")
def i():
    return redirect("http://localhost:9000/",302)

@app.route("/")
def login():
    return render_template("login.html")

@app.route("/login")
def backLogin():
    return redirect("http://localhost:9000/",302)

@app.route("/index", methods=['POST', 'GET'])
def main():
    if (request.method == 'POST'):
        username = request.form['username']
        password = request.form['password']
        firstLogin = authen.find_one({'username': request.form['username']})
        print(firstLogin)
        if(firstLogin!=None):
            hashPass = bcrypt.hashpw(request.form['password'].encode(), salt)
            if(tempSecurityLogin!=[]):
                tempSecurityLogin.pop(0)
            # print(hashPass==firstLogin['password'],hashPass,'----',firstLogin['password'])
            if(bcrypt.checkpw(request.form['password'].encode(), firstLogin['password'])):
                if(authenNowMemory!=[]):
                    authenNowMemory.pop(0)
                    authenNowMemory.append(firstLogin)
                else:
                    authenNowMemory.append(firstLogin)
                if indexPostPage != []:
                    indexPostPage.pop(0)
                    indexPostPage.append(
                        initIndexPostPage.format("", firstLogin['name'], firstLogin['address'],
                                                 boxPostMem, "").replace("\\n", "").replace("['", "").replace("']", "").replace(
                            "', '", "<br>"))
                    app.logger.debug('%s logged in successfully', firstLogin['username'])
                    return  indexPostPage[0]
                else:
                    app.logger.debug('%s logged in successfully', firstLogin['username'])
                    return initIndexPostPage.format("", firstLogin['name'], firstLogin['address'],
                                                 boxPostMem, "").replace("\\n", "").replace("['", "").replace("']", "").replace(
                            "', '", "<br>")
                app.logger.debug('%s failed to log in', firstLogin['password'])
                return loginFailPage.format('wrong username or password')
            else:
                if(roundLogin==[]):
                    roundLogin.append(1)
                else:
                    roundLogin.append(roundLogin[0]+1)
                    roundLogin.pop(0)
                if(roundLogin[0]==3):
                    return 'sorry you cursious'
                if(tempSecurityLogin!=[]):
                    if(tempSecurityLogin[0]==request.form['username']):
                        roundLogin.append(roundLogin[0]+1)
                        roundLogin.pop(0)
                        app.logger.warning('%s warning enemy hacked username round : ',i)
                    else:
                        tempSecurityLogin.pop(0)
                        roundLogin.pop(0)
                else:
                    tempSecurityLogin.append(request.form['username'])
        else:
            if(username==''):
                app.logger.debug('%s failed to log in', username)
                return loginFailPage.format('username is missing')
            if(password==''):
                app.logger.debug('%s failed to log in', username)
                return loginFailPage.format('password is missing')
        app.logger.debug('%s failed to log in', username)
        return loginFailPage.format('failed login')
    else:
        if indexPostPage != []:
            app.logger.debug('%s failed to log in', firstLogin['username'])
            indexPostPage.pop(0)
            indexPostPage.append(
                initIndexPostPage.format("", firstLogin['name'], firstLogin['address'],
                                         boxPostMem, "").replace("\\n", "").replace("['", "").replace("']", "").replace(
                    "', '", "<br>"))

            return indexPostPage[0]
        else:
            app.logger.debug('%s failed to log in', firstLogin['username'])
            return initIndexPostPage.format("", firstLogin['name'], firstLogin['address'],
                                            "", "").replace("\\n", "").replace("['", "").replace("']", "").replace(
                "', '", "<br>")

    # if (request.method == 'POST'):
    #     username = request.form['username']
    #     password = request.form['password']
    #     if(username!=''
    #             and username!= None
    #             and password!=''
    #             and password!= None):
    #         for x in authenMemory:
    #             if(x.get('username')==username and x.get('password')==password):
    #                 authenNowMemory.append(x)
    #                 if indexPostPage != []:
    #                     indexPostPage.pop(0)
    #                     indexPostPage.append(
    #                         initIndexPostPage.format("", authenNowMemory[0]['name'], authenNowMemory[0]['address'],
    #                                                  boxPostMem, "").replace("\\n", "").replace("['", "").replace("']", "").replace(
    #                             "', '", "<br>"))
    #
    #                     app.logger.info('%s logged in successfully', username)
    #                     return  indexPostPage[0]
    #                 else:
    #                     app.logger.info('%s logged in successfully', username)
    #                     return initIndexPostPage.format("", authenNowMemory[0]['name'], authenNowMemory[0]['address'],
    #                                                  "", "").replace("\\n", "").replace("['", "").replace("']", "").replace(
    #                             "', '", "<br>")
    #         app.logger.info('%s failed to log in', username)
    #         return loginFailPage.format('wrong username or password')
    #     else:
    #         if(username==''):
    #             app.logger.info('%s failed to log in', username)
    #             return loginFailPage.format('username is missing')
    #         if(password==''):
    #             app.logger.info('%s failed to log in', username)
    #             return loginFailPage.format('password is missing')
    #         app.logger.info('%s failed to log in', username)
    #         return loginFailPage
    # else:
    #     if indexPostPage != []:
    #         indexPostPage.pop(0)
    #         indexPostPage.append(
    #             initIndexPostPage.format("", authenNowMemory[0]['name'], authenNowMemory[0]['address'],
    #                                      boxPostMem, "").replace("\\n", "").replace("['", "").replace("']", "").replace(
    #                 "', '", "<br>"))
    #
    #         return indexPostPage[0]
    #     else:
    #         return initIndexPostPage.format("", authenNowMemory[0]['name'], authenNowMemory[0]['address'],
    #                                         "", "").replace("\\n", "").replace("['", "").replace("']", "").replace(
    #             "', '", "<br>")

@app.route("/about", methods=['GET'])
def about():
    return render_template('about.html')

@app.route("/contact", methods=['GET'])
def contact():
    return render_template('contact.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if(request.method=='POST'):
        if(request.form['username']!=''):
            if(request.form['password']!=''):
                if(request.form['confirmPassword']!=''):
                    if(request.form['name']!=''):
                        if(request.form['address']!=''):
                            if(request.form['password']==request.form['confirmPassword']):
                                authenMemory.append({'username': request.form['username'],
                                               'password': request.form['password'],
                                                 'name': request.form['name'],
                                                 'address': request.form['address']})

                                hashedPass = bcrypt.hashpw(request.form['password'].encode(), salt)
                                postDb = {
                                    'username': request.form['username'],
                                    'password': hashedPass,
                                    'name': request.form['name'],
                                    'address': request.form['address']
                                }
                                app.logger.debug('%s register in successfully', postDb)
                                authen.insert_one(postDb)
                                return render_template("login.html")
                            else:
                                return registerFailPage.format("password don't match confirm password")
                        else:
                            return registerFailPage.format("address is missing")
                    else:
                        return registerFailPage.format("name is missing")
                else:
                    return registerFailPage.format("confirm password is missing")
            else:
                return registerFailPage.format("password is missing")
        else:
            return registerFailPage.format("username is missing")
    else:
        return render_template("register.html")

@app.route("/postText", methods=['POST'])
def postText():
    name = authenNowMemory[0]['name']
    nameProd = request.form['name']
    costProd = request.form['cost']
    telephoneProd = request.form['telephone']
    emailProd = request.form['email']
    dataProd = request.form['message']
    productDB = {
        'nameProd': nameProd,
        'costProd': costProd,
        'telephoneProd': telephoneProd,
        'emailProd': emailProd,
        'dataProd': dataProd,
        'imgProd': imageMem[0],
        'name': authenNowMemory[0]['name']
    }
    app.logger.debug('%s post product in successfully by :',authenNowMemory[0]['name'],'| resource : ', productDB)
    product.insert_one(productDB)

    boxPostMem.append(boxPost.format(imageMem[0], nameProd, costProd, dataProd, telephoneProd, emailProd, name))
    # for x in product.find_one({}):

    sellMem.append("<tr><td>"+nameProd+"</td></tr>")
    postMemory.append(dataProd)

    # 1.successUpload 2.user 3.boxPost
    if indexPostPage != []:
        indexPostPage.pop(0)
        indexPostPage.append(initIndexPostPage.format(sellMem, authenNowMemory[0]['name'], authenNowMemory[0]['address'], boxPostMem, "").replace("\\n", "").replace("['", "").replace("']", "").replace("', '", "<br>"))
    else:
        indexPostPage.append(initIndexPostPage.format(sellMem, authenNowMemory[0]['name'], authenNowMemory[0]['address'], boxPostMem, "").replace("\\n", "").replace("['", "").replace("']","").replace("', '", "<br>"))
    return indexPostPage[0]

@app.route("/postImage", methods=['POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            if indexPostPage != []:
                indexPostPage.pop(0)
                indexPostPage.append(
                    initIndexPostPage.format("", authenNowMemory[0]['name'], authenNowMemory[0]['address'], boxPostMem, "No file part").replace("\\n", "").replace("['",
                                                                                                            "").replace(
                        "']", "").replace("', '", "<br>"))
            else:
                indexPostPage.append(
                    initIndexPostPage.format("", authenNowMemory[0]['name'], authenNowMemory[0]['address'], boxPostMem, "No file part").replace("\\n", "").replace("['",
                                                                                                            "").replace(
                        "']", "").replace("', '", "<br>"))
            app.logger.error('%s upload image in failled by', authenNowMemory[0]['name'])
            return indexPostPage[0]
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filen ame
        if file.filename == '':
            if indexPostPage != []:
                indexPostPage.pop(0)
                indexPostPage.append(
                    initIndexPostPage.format("No selected file",authenNowMemory[0]['name'], authenNowMemory[0]['address'], boxPostMem, "").replace("\\n", "").replace("['",
                                                                                                            "").replace(
                        "']", "").replace("', '", "<br>"))
            else:
                indexPostPage.append(
                    initIndexPostPage.format("No selected file",authenNowMemory[0]['name'], authenNowMemory[0]['address'], boxPostMem, "").replace("\\n", "").replace("['",
                                                                                                            "").replace(
                        "']", "").replace("', '", "<br>"))
            app.logger.error('%s upload image in failled by', authenNowMemory[0]['name'])
            return indexPostPage[0]
        if file and allowed_file(file.filename):
            print('isPath')
            filename = secure_filename(file.filename)

            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            if imageMem != []:
                imageMem.pop(0)
                imageMem.append(filename)
            else:
                imageMem.append(filename)
            if indexPostPage != []:
                indexPostPage.pop(0)
                indexPostPage.append(
                    initIndexPostPage.format("", authenNowMemory[0]['name'], authenNowMemory[0]['address'], boxPostMem,"success",).replace("\\n", "").replace("['",
                                                                                                            "").replace(
                        "']", "").replace("', '", "<br>"))
            else:
                indexPostPage.append(
                    initIndexPostPage.format("", authenNowMemory[0]['name'], authenNowMemory[0]['address'], boxPostMem,"success").replace("\\n", "").replace("['",
                                                                                                            "").replace(
                        "']", "").replace("', '", "<br>"))
            app.logger.error('%s upload image in successfully by', authenNowMemory[0]['name'], ' | resource : ', imageMem[0])
            return indexPostPage[0]
    return ""



if __name__ == "__main__":
    files = os.listdir(UPLOAD_FOLDER)

    cclient = MongoClient()
    client = MongoClient('localhost', 27017)
    client = MongoClient('mongodb://localhost:27017')
    db = client.webserver
    authen = db.authen
    product = db.product
    # salt = bcrypt.gensalt()
    # hash = bcrypt.hashpw('1234'.encode(), salt)
    # print(hash == bcrypt.hashpw('1234'.encode(), salt))
    # print(bcrypt.checkpw('1234'.encode(),hash))
    logging.basicConfig(filename='log/log.log',level=logging.DEBUG)
    app.logger.info('%s database connected : mongodb://localhost:27017')
    for x in product.find({}):
        boxPostMem.append(boxPost.format(x['imgProd'], x['nameProd'], x['costProd'], x['dataProd'], x['telephoneProd'], x['emailProd'], x['name']))
    #---Clear mem---
    # for name in files:
    #     os.remove(UPLOAD_FOLDER+"/"+name)
    app.logger.info('%s inital query database success')
    app.run(debug=True, host="0.0.0.0", port=9000)
