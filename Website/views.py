import os #, cv2
from flask import Flask,send_from_directory
import flask
import sqlite3
from flask.helpers import make_response
from sqlalchemy import desc
from werkzeug import Request, exceptions
from flask_login import login_required, current_user, logout_user
from flask import Blueprint, app, render_template, request, flash, redirect, url_for,Response
from sqlalchemy.sql.sqltypes import INTEGER, STRINGTYPE, String
from werkzeug.utils import secure_filename, secure_filename
from . import db,UPLOAD_FOLDER
from datetime import datetime
from .models import User,Produto,Img
from PIL import Image
from datetime import datetime, timedelta,time
from werkzeug.security import generate_password_hash, check_password_hash
from operator import attrgetter
from collections import OrderedDict
from random import randint

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.instance_path=UPLOAD_FOLDER
uploads_dir = os.path.join(app.instance_path, 'uploads')
#os.makedirs(uploads_dir)

views = Blueprint('views', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif','tiff','webp','bmp'}

FILE='file[]'
MESSAGE="File successfully uploaded"
INDEX='views.index'
MESSAGE_IMG='The image format is not correct! Check it!'
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def filetype_ok(mimetype):
    for element in ALLOWED_EXTENSIONS:
        if  element in mimetype:
            return True
    return False

def commiting():
    try:
        db.session.commit()
    except AssertionError as err:
        db.session.rollback()
        flask.abort(409, err) 
    except (exceptions.IntegrityError, sqlite3.IntegrityError) as err:
        db.session.rollback()
        print("There isn't no element or already or other possible mistake exists")
        flask.abort(409, err.orig) 
    except Exception as err:
        db.session.rollback()
        flask.abort(500, err) 
    #/finally: 
        #/db.session.close()

def remove_product(id):
    remove_product_from_favorites(id)
    product=Produto.query.get(id)
    delete_imgs(product)        
    db.session.delete(product)
    commiting()





def save_pic(file,img_function,id,width,height):
    print(file.filename)
    if file and allowed_file(file.filename):
        mimetype=file.mimetype            
        if filetype_ok(mimetype):

            image=Image.open(file)
            print(image.size) 
            width=image.size[0]
            height=image.size[1]
            aux=str(randint(1,999999))+file.filename
            filename = secure_filename(aux)                
            f = Image.open(file)
            f = f.resize((width,height)) 
            image.save(os.path.join(uploads_dir, filename), optimize=True,quality=65)            

            if img_function=='image':
                #/f.save(os.path.join(uploads_dir, filename))
                #print(uploads_dir)                  
                #/img =Img(img=f.read(), name=filename,mimetype=mimetype,produtoid= produto.id)
                img =Img(name=filename,mimetype=mimetype,produtoid= id,width=width,height=height)         
                db.session.add(img)
                commiting()
            elif img_function =='foto_name':
                if current_user.foto_name != 'guest_user.jpg':
                    os.remove(os.path.join(uploads_dir, current_user.foto_name))
                current_user.foto_name=filename
                commiting()
                
            elif img_function =='logo_user':
                if current_user.logo_user:
                    os.remove(os.path.join(uploads_dir, current_user.logo_user))
                current_user.logo_user=filename
                commiting()
            return 'success'
        return MESSAGE_IMG
    return 'error'

def filter_db(types,categoria,pricemin,pricemax,search,concat):      
    keywordsearch=search.split(' ') 
    for key in keywordsearch:
        if concat==11100:   
                lista =Produto.query.filter((Produto.money >=pricemin) &( Produto.money <=pricemax) &(Produto.name.contains(key) | Produto.description.contains(key))).order_by(Produto.id.desc()).all()
        elif concat==11101:
                lista =Produto.query.filter((Produto.type== types) & (Produto.money >=pricemin)  & (Produto.money <=pricemax )& (Produto.name.contains(key) | Produto.description.contains(key))).order_by(Produto.id.desc()).all()
        elif concat==11110:
                lista =Produto.query.filter((Produto.category== categoria) & (Produto.money >=pricemin)  & (Produto.money <=pricemax) & (Produto.name.contains(key) | Produto.description.contains(key))).order_by(Produto.id.desc()).all()
        elif concat==11111:
                lista =Produto.query.filter((Produto.type == types) & (Produto.category== categoria) & (Produto.money >=pricemin ) &(Produto.money <=pricemax)&(Produto.name.contains(key) | Produto.description.contains(key))).order_by(Produto.id.desc()).all()
        else:
            lista=Produto.query.order_by(Produto.id.desc()).all()
            print("Produtos error in selected produtos!!")
    return lista
    
   
def chunks(listprodutos, n_products):
    if len(listprodutos)>n_products:
        return [listprodutos[i:i + n_products] for i in range(0, len(listprodutos),n_products)]
    else:
        return listprodutos


@views.route('/index/', methods=['GET', 'POST'])
@views.route('/index/?method=<method>&page=<page>',methods=['GET', 'POST'])
@views.route('/index/?method=<method>&page=<page>&types=<types>&categoria=<categoria>&pricemax=<pricemax>&pricemin=<pricemin>&search=<search>',methods=['GET', 'POST'])
def index(*args):
    n_products=1
    page='index.html'
    option=0
    peso=[10000,1000,100,0,0]
    concat=0
    method=request.args.get('method',type=str)
    print(request.url)
    print(request.path)
    print(method)
    print(request.args.get('types'))
    print(request.args.get('categoria'))
    print(request.args.get('search'))
    print(request.args.get('page'))
    if request.args.get('page')!=None:
        pag=int(request.args.get('page'))
    else:
        pag=1
    print("url request       "+request.url)
    print(request.path)

    if(request.args.get('search') !=None)and (method=='POST') and (request.args.get('search')!=''):
        option=2
        print("option 2")
        types=request.args.get('types',default='Types',type=str)
        categoria=request.args.get('categoria',default='Categories',type=str)
        pricemax=request.args.get('pricemax',type=float)
        pricemin=request.args.get('pricemin',type=float)
        search=(request.args.get('search',default='',type=str)).replace('%20',' ')
        print(str(types)+ str(categoria)+ str(pricemin)+str(pricemax)+str(search))           

    elif request.form.get('search')!=None or request.method=='POST':#nao mexer
        option=1
        print(request.form.get('search')+"   option1   "+ request.method)
        print(str(request.form.get('search'))+ "e este é a option before that"+ str(option))        
        print("option 1")            
        types=request.form.get('types')#5
        categoria=request.form.get('productTypes')#4
        pricemax=request.form.get('pricemax',type=float) #3
        pricemin=request.form.get('pricemin',type=float)#2
        search=request.form.get('search')#1
        print(str(types)+ str(categoria)+ str(pricemin)+str(pricemax)+str(search))  

    elif option ==0:#no parameters
        listprodutos= Produto.query.order_by(Produto.id.desc()).all()
        print("concat está a "+str(concat))
                  
  
    if option !=0:
        peso[3]=10 if categoria != None and not 'Categories' in categoria else 0
        peso[4]=1 if types!= None and not 'Types' in types else 0
        concat=peso[0]+peso[1]+peso[2]+peso[3]+peso[4]
        listprodutos= filter_db(types,categoria,pricemin,pricemax,search,concat)
        print(str(types)+ str(categoria)+ str(pricemin)+str(pricemax)+str(search))

    print("este é o concat" + str(concat))   
    n_pages= round((len(listprodutos)/n_products) + 0.49)
    
    print(str(n_pages)+ "este é o n de paginas")
    print(str(pag) +" esta é a pagina")
    if ( pag<=n_pages) and (pag>=1): 
        n=(pag-1)
    else:
        n=0

    print(str(n) + " id que chegou no backend")  
    print(str(n_pages) + "  numero de paginas")            
    
    print(listprodutos)
    print(str(n) +" id usado no get")

    splited=chunks(listprodutos,n_products)
    print(splited)
    print("| produtos mostrados") 
    if  (method == 'POST' or request.method == 'POST') and n_pages>1:  
        return render_template(
        page,
        user=current_user,
        produtos=splited[n],    
        n_pages=n_pages,
        current_page=n+1,
        method=method,
        types=types,
        categoria=categoria,
        pricemax=pricemax,
        pricemin=pricemin,
        search=search)
    elif n_pages>1 and(request.method == 'GET'):
        return render_template(
        page,
        user=current_user,
        produtos=splited[n],     
        n_pages=n_pages,
        current_page=n+1,
        method=method)
    else:
        return render_template(
        page,
        user=current_user,
        produtos=listprodutos,    
        n_pages=n_pages,
        current_page=n+1,
        method=method)
        

def remove_product_from_favorites(id):
    product_delimitated=";"+str(id)+";"
    product= Produto.query.get(id)
    users= product.user_likedIt
    if users:
        users=users.replace(";",'',1) 
        users=users[:len(users)-1]  
        print(users)          
        x=users.split(";;") 
        if x:     
            print(x)       
            favoritos=list(map(int,x))
            print(str(favoritos))           
            for id_ in favoritos:                    
                print(str(id_)+"   this is the value saved")        
                user=User.query.get(id_)
                user.market_products=user.market_products.replace(product_delimitated,'')
                commiting()


def delete_imgs(product):
    for item in product.picture:
        os.remove(os.path.join(uploads_dir, item.name))
        product.picture.remove(item)
        db.session.delete(item)
    commiting()

def delete_allproducts_user(user):
    listproducts= Produto.query.filter(Produto.userOwnersid==user.id).all()    
    for product in listproducts:
        remove_product_from_favorites(product.id)
        delete_imgs(product)
        db.session.delete(product)
    commiting()
    

@login_required
@views.route('/profile/<int:id>',methods=['GET','POST'])
def profile(**kwargs):
    if current_user.is_authenticated:
        listprodutos=Produto.query.filter(Produto.userOwnersid==current_user.id).order_by(Produto.id.desc()).all()
        utilizador=current_user
        if kwargs.get('id'):
            id=int(kwargs.get('id'))
            print(str(id))
            utilizador=User.query.get(id)        
            if not User.query.get(id):
                return make_response(render_template('profile.html',id = current_user.id,user=current_user,utilizador=current_user,produtos=listprodutos), 200)
        else:
            id=current_user.id
        #/byte= request.form.get('del')
        listprodutos=Produto.query.filter(Produto.userOwnersid==id).order_by(Produto.id.desc()).all()
        if request.method == 'POST':
            #if byte==0:
                id_=request.form['id_delete']
                remove_product(id_)        
                flash('Product deleted with sucssess',category='success')
                return redirect(url_for('views.profile', id=current_user.id))
            #/else:
                #user=current_user  
                #print(str(user.id))  
                #logout_user()
                #delete_allproducts_user(user)    
                #db.session.delete(user)    
                #commiting()
                #return redirect(url_for('views.index', user=None))
        return render_template('profile.html',user=current_user,utilizador=utilizador,produtos=listprodutos)
    return render_template('forbiden.html',user=None)


@views.route('/about')
def about():
    count= User.query.count()
    n=Produto.query.count()
    return render_template('about.html',user=current_user,count=count,products_number= n)

@views.route('/uploads/<name>')
def download_file(name):
    return send_from_directory(UPLOAD_FOLDER, name)

@views.route('/sell', methods=['GET', 'POST'])
def sell():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')             
        date=datetime.now()    
        selected= request.form.get('productTypes')
        file = request.files.getlist(FILE)
        price=request.form.get('price')

        produto = Produto(name=name,description=description,date=date,category=selected,money=price,userOwners=current_user.name,userOwnersid=current_user.id, type='For sale')
        
        db.session.add(produto)      
        commiting()
        
        #print(produto.id)
        flask.current_app.logger.info('Committing changes to db...')        
        for f in file:               
            if save_pic(f,'image',produto.id,216,156)=='success': 
                #/print(str(f)+"\n"+str(img)+"\n"+ "name"+ str(filename)+"tipo"+str(mimetype) +"produtoid"+ str(produto.id));
                flash(MESSAGE,category="success")
            else:
                remove_product(produto.id)
                flash(MESSAGE_IMG,category="error")
                return render_template('sell.html',user=current_user)                                       
        return redirect(url_for(INDEX))            
    return render_template('sell.html',user=current_user)


@views.route('/<int:id>')
def get_img(id):
    img = Img.query.filter_by(id=id).first()
    if not img:
        return 'Img Not Found!', 404
    return Response(img.img, mimetype=img.mimetype)


@views.route('/buy', methods=['GET', 'POST'])
def buy():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')             
        date=datetime.now()    
        selected= request.form.get('productTypes')
        file = request.files.getlist(FILE)
        price=request.form.get('price')

        produto = Produto(name=name,description=description,date=date,category=selected,money=price,userOwners=current_user.name,userOwnersid=current_user.id, type='Wanted')
               
        db.session.add(produto)      
        commiting()
        
        #print(produto.id)
        flask.current_app.logger.info('Committing changes to db...')        
        for f in file:               
            if save_pic(f,'image',produto.id,420,310)=='success': 
                #/print(str(f)+"\n"+str(img)+"\n"+ "name"+ str(filename)+"tipo"+str(mimetype) +"produtoid"+ str(produto.id));
                flash(MESSAGE,category="success")
            else:
                remove_product(produto.id)
                flash(MESSAGE_IMG,category="error")
                return render_template('buy.html',user=current_user)                                       
        return redirect(url_for(INDEX))            
    return render_template('buy.html',user=current_user)


@views.route('/auctions', methods=['GET', 'POST'])
def auctions():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')             
        date=datetime.now()    
        selected= request.form.get('productTypes')
        file = request.files.getlist(FILE)
        price=request.form.get('price')
        limitdate=request.form.get('auctiondate').replace('T',' ')
        #print(str(limitdate))
        
        timespan= datetime.strptime(limitdate,'%Y-%m-%d %H:%M')  

        produto = Produto(name=name,description=description,date=date,category=selected,money=price,userOwners=current_user.name,userOwnersid=current_user.id, type='Auctions',auctiondate=timespan)
        #print(timespan)

        db.session.add(produto)      
        commiting()
        
        #print(produto.id)
        flask.current_app.logger.info('Committing changes to db...')        
        for f in file:               
            if save_pic(f,'image',produto.id,420,310)=='success': 
                #/print(str(f)+"\n"+str(img)+"\n"+ "name"+ str(filename)+"tipo"+str(mimetype) +"produtoid"+ str(produto.id));
                flash(MESSAGE,category="success")
            else:
                remove_product(produto.id)
                flash(MESSAGE_IMG,category="error")
                return render_template('auctions.html',user=current_user)                                       
        return redirect(url_for(INDEX))            
    return render_template('auctions.html',user=current_user)

@views.context_processor
def inject_today_date():
    return {'today_date': datetime.today()}

@views.context_processor
def inject_year_later():     
    d = datetime.today() + timedelta(days=365)
    return {'today_date_after_year': d }


def bit_decision_(id):
    bit=1
    container=";"+str(id)+";"
    if container in current_user.market_products:
        bit=0
    return bit
    
    

@views.route('/products/<int:id>',methods=['GET', 'POST'])
def products(id):
    exists  = True if Produto.query.get(id)!= None else False
    print(str(exists))
    produto=None
    if exists:
        produto=Produto.query.get(id)
        user=None     
        bit=0
        if current_user.is_authenticated and produto:
            user=current_user
            user_delimitated=';'+str(user.id)+';'
            print(str(id)+ " id")
            bit=bit_decision_(id)
            print(str(bit)+" este é o bit")         

            #print(str(produto.id) +"  "+ produto.name)            
            products_id_saved=';'+str(id)+';'

            if(request.method=='POST'):     
                if products_id_saved not in current_user.market_products and 'None' not in products_id_saved:            
                    current_user.market_products += products_id_saved 
                    produto.user_likedIt += user_delimitated 
                    print(str(produto.user_likedIt)+ "users love it")         
                    print(current_user.market_products+ "  colocou")           
                    db.session.commit()
                else:
                    current_user.market_products=current_user.market_products.replace(products_id_saved,'')
                    produto.user_likedIt=produto.user_likedIt.replace(user_delimitated,'')              
                    db.session.commit()               
                    print(current_user.market_products+ "  retirou")    
        return render_template('products.html',user=user,product=produto,bit_decision=bit)
    return redirect(url_for('views.index'))


@views.route('/favorites',methods=['GET', 'POST'])
@login_required
def favorites():
    listprodutos=[]   
    values= current_user.market_products
    if values:
        values=values.replace(";",'',1) 
        values=values[:len(values)-1]  
        #/print(values)          
        x=values.split(";;") 
        if x:     
            #/print(x)       
            favoritos=list(map(int,x))
            #/print(str(favoritos))           
            for id in favoritos:                    
                print(str(id)+"   this is the value saved")        
                listprodutos.insert(0,Produto.query.get(id))
            #/print(str(listprodutos[0].id) +str(listprodutos[0].name))
    return render_template('favorites.html',user=current_user,produtos=listprodutos)

def return_status(returned):
    if returned == 'success':
        print('success')
        flash("Changes saved!",category='success')
        return redirect(url_for('views.index', user=current_user))
    elif returned == 'error':
        print('error')
        flash("File corrupt!",category='error')
        return render_template('edit.html',user=current_user)
    else:
        flash(returned,category='error')
        print(returned)
        return render_template('edit.html',user=current_user)

@login_required
@views.route('/edit', methods=['GET','POST'])
def edit():
    user=User.query.get(current_user.id) 
    if request.method == 'POST':
        name = request.form.get('name')
        password_before=request.form.get('password1')
        password_new=request.form.get('password2')
        confimr_new_password=request.form.get('password3')
        email = request.form.get('email')        
        description = request.form.get('description')                         
        picProfile = request.files.get("picProfile")
        logoPic =request.files.get("logoPic")

        if password_before and password_new and confimr_new_password:
            if check_password_hash(user.password, password_before) and password_new == confimr_new_password:
                user.password=generate_password_hash(password_new, method='sha256')
                db.session.commit()
        if name:
            user.name=name
            db.session.commit()
        if email:
            user.email=email
            db.session.commit()
        if description:
            user.description=description
            db.session.commit()

        if  picProfile :              
            return_status(save_pic(picProfile,'foto_name',None,200,200))           
        if logoPic:            
            return_status(save_pic(logoPic,'logo_user',None,200,200))
        return redirect(url_for('views.profile',id=current_user.id))        
    return render_template('edit.html', user=current_user)


@login_required
@views.route('/delete_account', methods=['POST'])
def delete_account():
    user=current_user  
    print(str(user.id))  
    logout_user()
    delete_allproducts_user(user)    
    db.session.delete(user)    
    commiting()
    return redirect(url_for('views.index', user=None))
    
@login_required
@views.route('/edit_product/<int:id>', methods=['GET','POST'])
def edit_product(id):
    print(str(id))
    user=current_user  
    print(str(user.id))
    exists  = True if Produto.query.get(id) else False
    print(str(exists))
    produto=None
    if exists:
        produto=Produto.query.get(id)
    else:
        flash('Not allowed!!', category='error')
        return redirect(url_for('views.profile',id=user.id))
    print(produto)

    if request.method == 'POST':
        #/information to set 
        imagesdel=request.form.get('imagesdel_',type=str)
        print(imagesdel)
        imagesdel=imagesdel[:-1]
        imagesdel=imagesdel.split(';')
        print(imagesdel)
        if imagesdel and len(produto.picture)>len(imagesdel):
            for img in imagesdel:
                item=Img.query.get(int(img))
                produto.picture.remove(item)
                os.remove(os.path.join(uploads_dir, item.name))
                db.session.delete(item)
            commiting()
        else:
            flash('Can not delete all pictures!!', category='error')
            return render_template('edit_product.html',product=produto,id=user.id,user=user, utilizador=user)
       
        print(str(produto.auctiondate))
        name= request.form.get('nameproduct')
        if name!= produto.name and name!='' and name!=None:
            produto.name=name
            commiting()
        print("este é o nome do produto "+name)
        price= request.form.get('price',type=float)
        if price!= produto.money and price!=None:
            produto.money=price
            commiting()
        print(price)
       
        if produto.type=='Auctions':
            print( produto.auctiondate)
            print(request.form.get('auctiondate',type=str))
            auctiondate=request.form.get('auctiondate',type=str).replace('T',' ')
            auctiondate=datetime.strptime(auctiondate,'%Y-%m-%d %H:%M')
            if auctiondate>datetime.now() and auctiondate!=produto.auctiondate:
                print(True)
                if auctiondate!= produto.auctiondate and auctiondate!=None and produto.type=='Auctions':
                    produto.auctiondate=auctiondate
                    commiting()
            print(str(auctiondate))

        select= request.form.get('productTypes',type=str)
        if select!= produto.category and select!=None:
            produto.category=select
            commiting()
        print("este é a category do produto "+select)

        description=request.form.get('description',type=str)
        if description!= produto.description and description!='':
            produto.description=description
            commiting()
        print("este é a description do produto "+description)
        #change info of product

        file = request.files.getlist(FILE)
        if file:
            flask.current_app.logger.info('Committing changes to db...')        
            for f in file:               
                if save_pic(f,'image',produto.id,216,156)=='success': 
                    #/print(str(f)+"\n"+str(img)+"\n"+ "name"+ str(filename)+"tipo"+str(mimetype) +"produtoid"+ str(produto.id));
                    flash(MESSAGE,category="success")

        return redirect(url_for('views.products',id=id))

    return render_template('edit_product.html',product=produto,id=user.id,user=user, utilizador=user)
