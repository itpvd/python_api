from flask import Flask, render_template,url_for,flash,redirect,request,json
from app import app,db,mail
from app.models.user import User
from flask_login import login_user,logout_user,current_user
from random import *
from functools import wraps

#Function check authen admin
def login_required_admin(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if current_user.is_authenticated==False or current_user.role!='admin':
            return json.dumps({'status':'401'});
        else:
            try:
                return f(*args, **kwargs)
            except Exception as exception:
                return json.dumps({'error':type(exception).__name__});
    return wrap

#Function check authen user
def login_required_user(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if current_user.is_authenticated==False:
            return json.dumps({'status':'401'});
        else:
            try:
                return f(*args, **kwargs)
            except Exception as exception:
                return json.dumps({'error':type(exception).__name__});
    return wrap
                           
#list user page
@app.route("/showListUser")
@login_required_admin
def showListUser():
    return render_template('admin/admin_user_list.html')

#Add user page
@app.route("/formAddUser")
@login_required_admin
def formAddUser():
    return render_template('admin/admin_user_add.html')

#Change password page
@app.route("/formChangePassword", methods=['GET'])
@login_required_user
def formChangePassword():
    return render_template('user/change_password.html')

#Forget password page
@app.route("/formForgetPassword", methods=['GET'])
def formForgetPassword():
    return render_template('user/foget_password.html')

#Show list all user
@app.route("/listUser")
@login_required_admin
def listUser():
    allRecord = User.listAllUser()
    page = request.args.get('page', 1, type=int)
    listUser = User.numberUserPerPage(page,10)
    dic={}
    for i in allRecord:
        dic[str(allRecord.index(i))]={'id': i.id,'username': i.username,'password': i.password,'email':i.email,'gender':i.gender,'birthday':i.birthday,'phone':i.phone,'role':i.role}
    dic['len']=len(allRecord)
    dic['status']="200"
    return json.dumps(dic);

#Create new user
@app.route("/addUser", methods=['POST'])
@login_required_admin
def addUser():
    input = request.form
    if User.userExists(input['username'])==False  and User.checkLenPass(input['password']):
        user = User(input['username'],input['password'],input['email'],input['gender'],input['birthday'],input['phone'],input['role'])
        user.createUser()
        return json.dumps({'status':'200'})
    else: 
        return json.dumps({'status':'400',"alert":User.alertRegister(input['username'],input['password'],input['password'])})

#Delete user 
@app.route("/deleteUser/<id>", methods=['DELETE'])
@login_required_admin
def deleteUser(id=None):
    User.deleteUser(id)
    return json.dumps({"status":"200"})

#Show form edit user
@app.route("/formEditUser/<id>", methods=['GET'])
@login_required_admin
def formEditUser(id=None):
    user = User.findUserById(id)
    return json.dumps({'id': user.id,'username': user.username,'password': user.password,'email':user.email,'gender':user.gender,'birthday':user.birthday,'phone':user.phone,'role':user.role,"status":"200"})

#Update user
@app.route("/updateUser",methods=['PUT'])
@login_required_admin
def updateUser():
    input = request.form
    id = input['id']
    if User.checkLenPass(input['password']):
        user = User(input['username'],input['password'],input['email'],input['gender'],input['birthday'],input['phone'],input['role'])
        user.updateUser(id)
        return json.dumps({'status':'200'});    
    else:
        return json.dumps({'status':'400','alert':'Password of at least 8 characters, including char and numbers, at least 1 capital letter'}); 

#Change Password
@app.route("/changePassword",methods=['POST'])
@login_required_user
def changePassword():
    input = request.form
    if input['passwordold']==current_user.password and input['password'] == input['passwordcf'] and User.checkLenPass(input['password']):
        id = current_user.id
        user = User(current_user.username,input['password'],current_user.email,current_user.gender,current_user.birthday,current_user.phone,current_user.role)
        user.updateUser(id)
        flash('Change password successfull')
        return json.dumps({'status':'200'});
    else:
        flash(User.alertChangePassword(current_user.password,input['passwordold'],input['password'],input['passwordcf']))
        return json.dumps({'status':'400'});

#Show form change Profile
@app.route("/formChangeProfile", methods=['GET'])
@login_required_user
def formChangeProfile():
    id = current_user.id
    user = User.findUserById(id)
    return render_template('user/change_profile.html',user=user)

#Change profile
@app.route("/changeProfile",methods=['POST'])
@login_required_user
def changeProfile():
    input = request.form
    id = current_user.id
    user = User(current_user.username,current_user.password,input['email'],input['gender'],input['birthday'],input['phone'],current_user.role)
    user.updateUser(id)
    return json.dumps({'status':'200'})

#Send password to mail when forget password
@app.route("/sendEmail",methods=['POST'])
def senEmail():
    input = request.form
    user = User.findUserByName(input['username'])
    if user and user.email==input['email']:
        msg = Message(subject="Hello %s, Flask app reset password"%user.username,
                      sender=app.config.get("MAIL_USERNAME"),
                      recipients=["%s"%user.email],
                      body="hi %s, new password:%s,thank you."%(user.username,user.password))
        mail.send(msg)
        return json.dumps({'status':'200','alert':'The password has been sent to your email'})
    else:
        flash('User name or email wrong')
        return json.dumps({'status':'400'})
