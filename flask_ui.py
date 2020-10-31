from flask import  Flask,render_template,request
import classes

#创建web应用程序
app = Flask(__name__, template_folder='templates', static_url_path='/', static_folder='static')

#开始页面
#http://127.0.0.1:5000/
@app.route("/")
def index():
    return render_template("start_menu.html")
@app.route("/start/",methods=['POST'])
def start():
    #从页面获取是会员登录还是管理员登录
    userclass = request.form.get("userclass")
    if userclass == "1":   # 会员登录
        return render_template("login.html")
    elif userclass=="2":   # 管理员登录
        return render_template("admin_login.html")
    else:        #未选择时给出提示
        return render_template("start_menu.html",msg="请选择！")

#会员登录
@app.route("/login/",methods=['POST'])
def login():
    #从页面获取用户名、密码
    username=request.form.get("username")
    pwd=request.form.get("pwd")
    flag,msg=booksystem.login(username,pwd)
    if flag:   #用户名和密码正确，进入主页
        return render_template("cus_main_menu.html")
    else:
        return render_template("login.html",msg=msg)


#会员注册
@app.route("/reg/",methods=['GET','POST'])
def reg():
    if request.method == 'GET':
        return render_template("reg.html")
    else:
        customer = request.form.get("username")
        pwd = request.form.get("pwd")
        pwd_re = request.form.get("pwd_re")
        phone = request.form.get("phone")
        address = request.form.get("address")
        flag,msg=booksystem.reg(customer,pwd,pwd_re,phone,address)
        return render_template("reg.html",msg=msg)


#密码找回
@app.route("/find_pwd/",methods=['GET','POST'])
def find_pwd():
    if request.method == 'GET':
        return render_template("find_pwd.html")
    else:
        customer=request.form.get("username")
        phone = request.form.get("phone")
        code=request.form.get("code")
        flag,msg=booksystem.find_pwd(customer,phone,code)
        if flag :
            pwd=booksystem.db.query_customer(customer)[2]  #   密码
            booksystem.login(customer, pwd)  #调用登录函数，为booksystem类增加custmerinfo属性
            return render_template("cus_main_menu.html")
        else:
            return render_template("find_pwd.html",msg=msg)


#信息修改
@app.route("/cus_modifyinfo/",methods=['GET','POST'])
def cus_modifyinfo():
    if request.method == 'GET':
        return render_template("cus_modifyinfo.html")
    else:
        pwd=request.form.get("pwd")
        pwd_re = request.form.get("pwd_re")
        address = request.form.get("address")
        msg1,msg2,msg3='','',''
        print(1,type(pwd),address)
        if pwd !='':
            msg1=booksystem.modify_pwd(pwd,pwd_re)
        if address != '':
            msg2=booksystem.modify_address(address)
        if pwd =='' and address == '':
            msg3='请输入密码或地址！'
        return render_template("cus_modifyinfo.html",msg1=msg1,msg2=msg2,msg3=msg3)

#书籍搜索
books=[]   #全局变量存放查询书籍的结果
# 获取列表的第6个元素
def takeFifth(elem):
    return elem[5]
@app.route("/find_book_menu/",methods=['GET','POST'])
def find_book_menu():
    global books
    if request.method == 'GET':
        return render_template("cus_main_menu.html")
    else:
        submits=request.form.get("submits")     #区分提交按钮
        keywords=request.form.get("keywords")   #区分搜索关键字，是以书名、作者、价格、出版社哪个来搜索
        texts = request.form.get("texts")       #输入的搜索内容
        lprice = request.form.get("lprice")     #以价格来搜索时，输入的最低价格
        rprice = request.form.get("rprice")     #以价格来搜索时，输入的最低价格
        isbn=request.form.get("isbn")           #加入购物车的书籍isbn
        quantity=request.form.get("quantity")   #加入购物车的书籍数量
        msg1,msg2='',''   #提示信息
        if submits=='查询' and keywords=='1':    #根据书名搜索
            books=list(booksystem.finds('`name`',texts))
        elif submits=='查询' and keywords=='2':  #根据作者搜索
            books = list(booksystem.finds('writer', texts))
        elif submits == '查询' and keywords == '3':  #根据价格搜索
            books=list(booksystem.finds('price',lprice,rprice))
        elif submits == '查询' and keywords == '4':   #根据出版社搜索
            books =list( booksystem.finds('publish', texts) )
        elif submits == '查询' and keywords ==None:
            msg1='请选择关键字'
            books = []
        elif submits == '销量由高到低':    #排序
            books.sort(key=takeFifth,reverse=True)
        elif submits == '加入购物车':
            msg2=booksystem.chose_book(isbn,quantity)
        else:
            pass
        return render_template("cus_main_menu.html", books=books,msg1=msg1,msg2=msg2)


#购物车
@app.route("/shopping_menu/",methods=['GET','POST'])
def shopping_menu():
    shoppings=booksystem.shopping()   #查询当前用户购物车里的物品
    if shoppings:
        msg=''
    else:
        msg='抱歉，购物车里还没有宝贝!'
    if request.method == 'GET':
        return render_template("shopping_menu.html",books=shoppings,msg=msg)
    else:
        isbn=request.form.get("isbn")
        if booksystem.show_delete_shopping(isbn): #校验输入的isbn是否合法
            booksystem.delete_shopping_one(isbn)
            msg1 = '删除成功！'
            shoppings = booksystem.shopping()   #更新页面购物车的展示
            if not(shoppings):
                msg = '抱歉，购物车里还没有宝贝!'
        else:
            msg1='此书不在购物车中！'
        return render_template("shopping_menu.html",books=shoppings,msg=msg,msg1=msg1)

#支付
@app.route("/pay_menu/",methods=['GET','POST'])
def pay_menu():
    flag, pays, msg = booksystem.show_pay()
    if request.method == 'GET':
        return render_template("pay_menu.html",pays=pays,msg=msg)
    else:
        if flag:  #有订单、购买数量合理就提交支付
            msg1=booksystem.pay()
            flag, pays, msg = booksystem.show_pay()
        else:
            msg1='暂时无法支付，原因：%s'%msg
        return render_template("pay_menu.html",pays=pays,msg=msg1)


#订单管理
@app.route("/order_menu/",methods=['GET','POST'])
def order_menu():
    orders=booksystem.select_order()  #获取订单信息
    if orders:    #校验订单是否为空
        msg=''
    else:
        msg='暂无订单'
    if request.method == 'GET':
        return render_template("order_menu.html",orders=orders,msg=msg)
    else:
        if msg=='暂无订单':
            return render_template("order_menu.html",orders=orders,msg=msg)
        else:  #post请求且订单不为空时才做处理
            orderid=request.form.get('orderid')
            print(orderid)
            flag,msg=booksystem.check_receipt(orderid)  #校验输入的订单编号
            print(flag,msg)
            if flag:  #订单编号校验成功，则进行确认
                msg=booksystem.receipt_ok(orderid)
                orders = booksystem.select_order()   #更新页面上的订单
                return render_template("order_menu.html", orders=orders,msg=msg)
            else:
                return render_template("order_menu.html", orders=orders,msg=msg)


#管理员登录
@app.route("/admin_login/",methods=['GET','POST'])
def admin_login():
    if  request.method == 'GET':
        return render_template("admin_login.html")
    else:
        admin_name=request.form.get("admin_name")
        admin_pwd=request.form.get("admin_pwd")
        flag,msg=bookadmin.login_admin(admin_name,admin_pwd)
        if flag: #登录成功进入管理员主界面
            return render_template("admin_main.html")
        else:
            return render_template("admin_login.html",msg=msg)

#会员主界面
@app.route("/admin_main/")
def admin_main():
    return render_template("admin_main.html")
#上架书籍
@app.route("/guard/",methods=['GET','POST'])
def guard():
    if request.method == 'GET':
        return render_template("admin_main.html")
    else:
        isbn=request.form.get("isbn")
        bookname=request.form.get("bookname")
        author=request.form.get("author")
        price=request.form.get("price")
        publish=request.form.get("publish")
        quantity=request.form.get("quantity")
        flag,msg=bookadmin.grouding_book(bookname,isbn,author,price,publish,quantity)
        return render_template("admin_main.html",msg=msg)
#销售统计
@app.route("/sales/")
def sale():
    sales=bookadmin.sales()
    print(sales)
    return render_template("sales.html",sales=sales)

if __name__=='__main__':
    db = classes.DB(name='root', pwd='', host='localhost', db='book')
    booksystem = classes.Booksystem(db)
    bookadmin = classes.BookAdmin(db)
    app.run(debug=True)  # 启动应用程序