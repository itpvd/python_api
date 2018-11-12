from flask import Flask, render_template,url_for,flash,redirect,request,json
from app import app,db
from app.models.post import Post
from flask_login import login_user,logout_user,current_user
from functools import wraps
import datetime

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

#List post page
@app.route("/showListPost")
@login_required_admin
def showListPost():
    return render_template('admin/admin_post_list.html')

#Add post page
@app.route("/formAddPost")
@login_required_admin
def formAddPost():
    return render_template('admin/admin_post_add.html')

#View post page
@app.route("/viewPostPage")
@login_required_admin
def viewPostPage():
    return render_template('user/post_list.html')

#Detail post page
@app.route("/detailPostPage")
@login_required_admin
def detailPostPage():
    return render_template('user/post_detail.html')

#Show list post
@app.route("/listPost")
@login_required_admin
def listPost():
    allRecord = Post.listAllPost()
    page = request.args.get('page', 1, type=int)
    listPost = Post.numberPostPerPage(page,10)
    dic={}
    for i in allRecord:
        dic[str(allRecord.index(i))]={'id': i.id,'title': i.title,'date_posted': i.date_posted,'content':i.content}
    dic['len']=len(allRecord)
    dic['status']="200"
    return json.dumps(dic);

#Create new post
@app.route("/addPost", methods=['POST'])
@login_required_admin
def addPost():
    input = request.form
    post = Post(input['title'],input['content'])
    post.createPost()
    return json.dumps({'status':'200'})
   
#Delete post  
@app.route("/deletePost/<id>", methods=['DELETE'])
@login_required_admin
def deletePost(id=None):
      Post.deletePost(id)
      return json.dumps({'status':'200'});

#Show form edit post
@app.route("/formEditPost/<id>",methods=['GET'])
@login_required_admin
def formEditPost(id=None):
    post = Post.findPostById(id)
    return json.dumps({'post':{'id': post.id,'title': post.title,'date_posted': post.date_posted,'content':post.content},"status":"200"})

#Update post 
@app.route("/updatePost",methods=['PUT'])
@login_required_admin
def updatePost():
    input = request.form
    id = input['id']
    post = Post(input['title'],input['content'])
    post.updatePost(id)
    flash('Update post is successful')
    return json.dumps({'status':'200'})

#Show list all post on user screen
@app.route("/viewPost")
@login_required_user
def viewPost():
    allRecord = Post.listAllPost()
    dic={}
    for i in allRecord:
        dic[str(allRecord.index(i))]={'id': i.id,'title': i.title,'date_posted': i.date_posted,'content':i.content}
    dic['len']=len(allRecord)
    dic['status']="200"
    return json.dumps(dic); 
    
@app.route("/detailPosts/<id>")
@login_required_user
def detailPosts(id=None):
    post = Post.findPostById(id_detail)
    return json.dumps({'post':{'id': post.id,'title': post.title,'date_posted': post.date_posted,'content':post.content},"status":"200"})
    