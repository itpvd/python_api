from flask import Flask, render_template,url_for,flash,redirect,request,json
from app import app,db
from app.models.user import User
from flask_login import login_user,logout_user

#--LOGIN function--
#Login page
@app.route("/")
@app.route("/formLogin")
def formLogin():
    return render_template('user/login.html',title='login')

#register page
@app.route("/formRegister")
def formRegister():
    return render_template('user/register.html',title='register')

#error page
@app.route("/error")
def error():
    return render_template('error/error.html')

#Login
@app.route("/login", methods=['POST'])
def login():
    try:
        input = request.form
        user = User.findUserByName(input['username'])
        if user and user.password == input['password'] and user.role=='user':
            login_user(user)
            return json.dumps({'status':'200','role':'user'});
        elif user and user.password == input['password'] and user.role=='admin':
            login_user(user)
            return json.dumps({'status':'200','role':'admin'});
        else:
            flash('User name or password is incorrect')
            return json.dumps({'status':'401'});
    except Exception as exception:
        return json.dumps({'error':type(exception).__name__});

#Register
@app.route("/register", methods=['POST'])
def register():
    try:
        input = request.form
        user = User.findUserByName(input['username'])
        if not user  and input['password']== input['confirmpass'] and  User.checkLenPass(input['password']):
            user = User(input['username'],input['password'],input['email'],input['gender'],input['birthday'],input['phone'],'user')
            User.createUser(user)
            return json.dumps({'status':'200'});
        else:
            return json.dumps({'status':'400','alert':User.alertRegister(input['username'],input['password'],input['confirmpass'])});
    except Exception as exception:
        return json.dumps({'error':type(exception).__name__});
        
#Logout
@app.route("/logout")
def logout():
    logout_user()
    return redirect('formLogin')
