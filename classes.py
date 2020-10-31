#数据库类：连接、关闭数据库，查询、插入数据
#业务逻辑处理类：Booksystem，BookAdmin
import pymysql,re
class DB:   #数据库连接
    name='数据库连接'
    def __init__(self,name,pwd,host,db,port=3306,charset='utf8'):
        # 初始化数据库连接参数
        try:  # 创建数据库连接
            self.con = pymysql.connect(user=name,password=pwd,host=host,
                                       port=port,db=db,charset=charset)
        except Exception:
            print('数据库连接错误')
            return None
        else:
            self.cur = self.con.cursor()  # 创建游标
            print('数据库连接成功')
    def close(self):
        self.cur.close()  # 关闭游标
        self.con.close()  # 关闭数据库连接
    def query_customer(self,cus):   #查找会员信息
        sql='select * from customer where customer="%s";'
        self.cur.execute(sql % cus)
        return self.cur.fetchone()
    def insert_customer(self,customer,pwd,phone,address):   #插入注册会员的数据
        sql='insert into customer(customer,pwd,phone,address) values ("%s","%s","%s","%s");'
        self.cur.execute(sql %(customer,pwd,phone,address))
        self.con.commit()
    def query_admin(self,admin):   #查找会员信息
        sql='select * from users where `user`="%s";'
        self.cur.execute(sql % admin)
        return self.cur.fetchone()
    def update_pwd(self,cus,pwd):  #更新密码
        sql='update customer set pwd="%s" where customer="%s";'
        self.cur.execute(sql %(pwd,cus))
        self.con.commit()
    def update_address(self,cus,address):  #更新地址
        sql='update customer set address="%s" where customer="%s";'
        self.cur.execute(sql %(address,cus))
        self.con.commit()
    def query_isbn(self,isbn):     #根据isbn查找书的信息
        sql='select * from bookinfo where isbn="%s";'
        self.cur.execute(sql % isbn)
        return self.cur.fetchone()
    def insert_bookinfo(self,name,isbn,writer,price,publish,quantity):
        #上架后，书籍详情插入bookinfo，库存插入inventory，默认插入销量为0的相关记录至sales
        sql_1='insert into bookinfo(`name`,isbn,writer,price,publish)values("%s","%s","%s","%f","%s");'
        self.cur.execute(sql_1 %(name,isbn,writer,float(price),publish))
        self.con.commit()
        #查找刚才插入到bookinfo记录的id，与库存表中的外键bookinfoid关联
        sql_2='select id from bookinfo where isbn="%s";'
        self.cur.execute(sql_2 %isbn)
        bookinfoid=self.cur.fetchone()[0]
        #插入数据到库存表中
        sql_3='insert into inventory(bookinfoid,quantity) values("%s","%s");'
        self.cur.execute(sql_3 %(bookinfoid,quantity))
        self.con.commit()
        #默认销量表中插入一条数据，销量\销售额为0
        sql_4='insert into sales(bookinfoid,quantity,totalprice) values("%s",0,0);'
        self.cur.execute(sql_4 % bookinfoid)
    def update_quantity(self,quantity,isbn):
        #查找bookinfo表中isbn记录的id，与库存表中的外键bookinfoid关联
        sql_1='select quantity from inventory where bookinfoid=(select id from bookinfo where isbn="%s");'
        self.cur.execute(sql_1 %isbn)  #拿到原来的库存,加上新上架的库存
        qua=self.cur.fetchone()[0]+int(quantity)       #拿到原来的库存,加上新上架的库存
        sql_2='update inventory set quantity="%s" where bookinfoid=(select id from bookinfo where isbn="%s");'
        self.cur.execute(sql_2 %(qua,isbn))
        self.con.commit()
    def query_bookinfos(self,field,param):   #模糊匹配bookinfo表中的记录
        #模糊匹配，结果显示书的名字，ISBN，作者，价格，出版社，销量，当前库存,默认以价格升序进行排序
        sql='''SELECT b.`name`,b.isbn,b.writer,b.price,b.publish,s.quantity,i.quantity
                FROM bookinfo b,inventory i ,sales s
                WHERE b.id=i.bookinfoid AND b.id=s.bookinfoid AND %s LIKE '%s'
                ORDER BY b.price
        '''
        params='%'+param+'%'
        self.cur.execute(sql %(field,params))
        return self.cur.fetchall()
    def bookinfos_desc(self,field,param):
        #模糊匹配查询结果，按照销量降序排列
        sql = '''SELECT b.`name`,b.isbn,b.writer,b.price,b.publish,s.quantity,i.quantity
                        FROM bookinfo b,inventory i ,sales s
                        WHERE b.id=i.bookinfoid AND b.id=s.bookinfoid AND %s LIKE '%s'
                        ORDER BY s.quantity DESC
                '''
        params = '%' + param + '%'
        self.cur.execute(sql % (field,params))
        return self.cur.fetchall()
    def query_price(self,field,l,r):
        #搜索价格区间的书籍信息
        sql='''SELECT b.`name`,b.isbn,b.writer,b.price,b.publish,s.quantity,i.quantity
                FROM bookinfo b,inventory i ,sales s
                WHERE b.id=i.bookinfoid AND b.id=s.bookinfoid AND %s BETWEEN %s AND %s
                ORDER BY b.price
        '''
        self.cur.execute(sql %(field,l,r))
        return self.cur.fetchall()
    def price_desc(self,field,l,r):
        #价格区间搜索的结果，按照销量降序排列
        sql='''SELECT b.`name`,b.isbn,b.writer,b.price,b.publish,s.quantity,i.quantity
                FROM bookinfo b,inventory i ,sales s
                WHERE b.id=i.bookinfoid AND b.id=s.bookinfoid AND %s BETWEEN %s AND %s
                ORDER BY s.quantity DESC
        '''
        self.cur.execute(sql % (field,l, r))
        return self.cur.fetchall()
    def insert_shopping(self,bookinfoid,customerid,quantity):   #往购物车表中出入数据
        sql='INSERT INTO shopping(bookinfoid,customerid,quantity) VALUES(%d,%d,%d)'
        self.cur.execute(sql %(bookinfoid,customerid,quantity))
        self.con.commit()
    def query_inventory(self,isbn):
        #根据书的isbn查库存
        sql='SELECT * FROM inventory WHERE bookinfoid=(SELECT id FROM bookinfo WHERE isbn="%s");'
        self.cur.execute(sql % isbn)
        return self.cur.fetchone()
    def query_shopping(self,customerid):
        '''
        购物车中，某一用户的全部书籍信息
        :param customerid:用户id
        :return:书名、isbn、作者、出版社、价格、购买数量
        '''
        sql='''SELECT b.`name`,b.isbn,b.writer,b.publish,b.price,s.quantity
                FROM shopping s,bookinfo b WHERE s.bookinfoid=b.id AND customerid=%s;
        '''
        self.cur.execute(sql %customerid)
        return self.cur.fetchall()
    def query_shopping_one(self,customerid,isbn):
        '''
        购物车中，某个用户的某本书（isbn）信息
        :param customerid:会员id
        :param isbn: 书籍信息
        :return: 书名、isbn、作者、出版社、价格、购买数量
        '''
        sql='''SELECT b.`name`,b.isbn,b.writer,b.publish,b.price,s.quantity
                FROM shopping s,bookinfo b WHERE s.bookinfoid=b.id AND customerid=%s AND b.isbn="%s"        
        '''
        self.cur.execute(sql % (customerid,isbn))
        return self.cur.fetchone()
    def delete_shopping_one(self,cusid,isbn):
        #删除购物车记录
        sql='''DELETE FROM shopping WHERE customerid=%s AND bookinfoid=
                (SELECT id FROM bookinfo WHERE isbn="%s");
        '''
        self.cur.execute(sql %(cusid,isbn))
        self.con.commit()
    def update_shopping_quantity(self,isbn,quantity):
        #更新购物车中的数量
        sql='UPDATE shopping SET quantity=%s WHERE bookinfoid=(SELECT id FROM bookinfo WHERE isbn="%s");'
        self.cur.execute(sql %(quantity,isbn))
        self.con.commit()
    def insert_orders(self,cusid,total):
        '''
        插入订单总表，并返回插入数据的id
        :param cusid: 当前用户的id
        :param total: 下单的总价
        :return: 返回订单的id
        '''
        sql="INSERT INTO orders(customerid,totalprice,`status`)VALUES(%s,%s,'未确认');"
        self.cur.execute(sql %(cusid,total))
        self.con.commit()
        #orders的id设置为的自增，新插入的此条数据是最后一条
        sql = 'SELECT id FROM orders ORDER BY id DESC LIMIT 1;'
        self.cur.execute(sql)
        return self.cur.fetchone()
    def query_for_ordersinfo(self,cusid):
        #查询要插入到ordersinfo中的bookinfoid，对应购买数量，总金额
        sql='''
        SELECT bookinfoid,s.quantity,s.quantity*b.price ,isbn
        FROM shopping s,bookinfo b 
        WHERE s.bookinfoid=b.id AND customerid=%s
        '''
        self.cur.execute(sql %cusid)
        return self.cur.fetchall()
    def insert_ordersinfo(self,ordersid,bookinfoid,quantity,price):
        #新增订单
        sql='INSERT INTO ordersinfo(ordersid,bookinfoid,quantity,price)VALUES(%s,%s,%s,%s);'
        self.cur.execute(sql %(ordersid,bookinfoid,quantity,price))
        self.con.commit()
    def update_inventory(self,bookinfoid,qua):
        #用户支付订单后，更新库存表中的书籍数量
        sql='UPDATE inventory SET quantity=%s WHERE bookinfoid=%s;'
        self.cur.execute(sql %(qua,bookinfoid))
        self.con.commit()
    def empty_shopping(self,cusid):
        #清空购物车
        sql='DELETE FROM shopping WHERE customerid=%s;'
        self.cur.execute(sql % cusid)
        self.con.commit()
    def query_orders(self,cusid):
        '''
        某个会员的订单查询
        :param cusid: 会员id
        :return:订单id,会员id,订单总价，状态
        '''
        sql='SELECT * FROM orders WHERE customerid=%s;'
        self.cur.execute(sql %cusid)
        return self.cur.fetchall()
    def update_orders(self,ordersid):
        #修改订单表的状态
        sql="UPDATE orders SET `status`='已收货' WHERE id=%s;"
        self.cur.execute(sql %ordersid)
        self.con.commit()
    def update_sales(self,ordersid):
        #更新销售表
        #1、查询订单中的书籍销售信息
        sql='''SELECT i.bookinfoid AS 书籍id,i.quantity AS 购买数量,i.price AS 销售额
                FROM orders o,ordersinfo i
                WHERE o.id=i.ordersid AND o.id="%s";
        '''
        self.cur.execute(sql %ordersid)
        r=self.cur.fetchall()    #r的每一元素为元组，（书籍id，购买数量，销售额）
        #2、更新销售表里的销售数量和销售额
        for i in r:
            sql='SELECT * FROM sales WHERE bookinfoid=%s'
            self.cur.execute(sql %i[0])
            olds=self.cur.fetchone()   #old为销售表里的原有销售情况，（id,书籍id，购买数量，销售额）
            new_qua=olds[2]+i[1]
            new_price=olds[3]+i[2]
            sql='UPDATE sales SET quantity=%s,totalprice=%s WHERE bookinfoid=%s;'
            self.cur.execute(sql %(new_qua,new_price,i[0]))
        self.con.commit()
    def query_sales(self):
        #查询销售统计,返回（书名，isbn,当前库存，销售量，销售额）
        sql='''SELECT b.`name`,b.isbn,i.quantity,s.quantity,s.totalprice
                FROM sales s
                LEFT JOIN bookinfo b
                ON s.bookinfoid=b.id
                LEFT JOIN inventory i
                ON i.bookinfoid=b.id
        '''
        self.cur.execute(sql)
        return self.cur.fetchall()
class Booksystem:
    name='会员系统处理'
    def __init__(self,db):   #db为数据库连接（DB类）的对象
        self.db=db
    def reg(self,cus,pwd,pwd_re,phone,address):  #会员注册
        #用户名、密码、确认密码、手机号非空
        if cus!='' and pwd!='' and pwd_re!='' and phone!=None:
            #用户名不存在
            if self.db.query_customer(cus)==None:
                # 密码与确认密码一致
                if pwd_re == pwd:
                    # 手机号校验：11位的数字
                    if phone.isdecimal()  and  len(phone) == 11:
                        self.db.insert_customer(cus,pwd,phone,address)
                        return 1,"注册成功！可返回登录页面进行登录"
                    else:
                        return 0,"手机号不合法！"
                else:
                    return 0,"确认密码不一致！"
            else:
                return 0,"用户名已存在！"
        else:
            return 0,"用户名/密码/确认密码/手机号不允许为空！"
    def login(self,cus,pwd):
        self.customerinfo=self.db.query_customer(cus)
        #customerinfo为元组，（id,用户名，密码，电话，地址）
        if self.customerinfo!=None:   #用户名校验
            if self.customerinfo[2]==pwd:   #密码校验
                return 1,1
            else:
                return 0,'密码错误！'
        else:
            return 0, '用户名不正确！'
    def find_pwd(self,cus,phone,code):   #会员找回密码:用户名，手机号码，短信验证码（0000）
        customerinfo = self.db.query_customer(cus)
        if customerinfo != None and customerinfo[3]==phone:  # 用户名校验
            if code=='0000':
                 return 1,1
            else:
                return 0, '验证码不正确！'
        else:
            return 0,'用户名或手机号码不正确！'
    def modify_pwd(self,pwd,pwd_re):  #信息修改：修改密码
        if pwd==pwd_re:
            self.customerinfo=list(self.customerinfo)
            self.customerinfo[2]=pwd   #修改实例属性
            self.db.update_pwd(self.customerinfo[1],pwd) #更新到数据库
            return '修改密码成功！'
        else:
            return '确认密码不一致！'
    def modify_address(self,address):  #信息修改：收货地址
        self.customerinfo = list(self.customerinfo)
        self.customerinfo[4] = address  # 修改实例属性
        self.db.update_address(self.customerinfo[1], address)  # 更新到数据库
        return '修改地址成功！'
    def finds(self,field,*param):   #通过字段名，字段值进行模糊搜索
        if len(param)==1:  #当搜索书名、作者、出版社时，可变参数只传入一位
            books=self.db.query_bookinfos(field,param[0]) #数据库中返回的查询结果
        else:  #当搜索价格区间时。可变参数传入两位
            books=self.db.query_price(field,param[0],param[1])
        return books
    def chose_book(self,isbn,quantity):
        #选择书和数量，加入购物车
        # 对isbn进行校验：
        # 1、是否存在于当前的书籍信息表中；books为bookinfo中的一条记录,(id,书名，isbn,作者，价格，出版社)
        books=self.db.query_isbn(isbn)
        #2、是否存已经存在与购物车中，shopping_one为shopping表中书籍详情的一条记录,
        # shopping_one（'书名', 'ISBN', '作者',  '出版社', '单价', '购买数量'）
        shopping_one=self.db.query_shopping_one(self.customerinfo[0],isbn)
        #如果isbn存在于当前书籍信息表（bookinfo）中，并且还未加入购物车，则向购物车里超如一条新的记录
        if books and shopping_one==None:
            qua=self.db.query_inventory(isbn)  #qua为库存表中isbn书籍对应的记录，（id,bookinfoid,数量）
            #购买数量是整数并且小于当前库存
            if quantity.isdecimal() and qua[2]>=int(quantity):
                #加入购物车，更新shopping表
                # books[0]为bookinfoid,self.customerinfo[0]为customerid
                self.db.insert_shopping(books[0],self.customerinfo[0],int(quantity))
                return '加入购物车成功！您还可以选择其他书籍~'
            else:
                return  '库存不足或输入数量有误！'
        # 如果isbn已经存在于购物车中，则直接更新对应的购买数量
        elif shopping_one:
            if quantity.isdecimal():   #购买数量为整数
                ##更新购买数量,shopping_one[5]为购物车里原来的数量
                qua=int(quantity)+int(shopping_one[5])
                self.db.update_shopping_quantity(isbn,qua)
                return  '加入购物车成功！您还可以选择其他书籍~'
            else:
                return '输入的购买数量不是整数！'
        else:
            return  'isbn不存在，请检查！'
    def shopping(self):
        #购物车,shoppings为('书名', 'ISBN', '作者', '出版社', '单价', '购买数量')
        return self.db.query_shopping(self.customerinfo[0])  #self.customerinfo[0]为customerid
    def show_delete_shopping(self,isbn):
        '''
        删除购物车里的东西，输入isbn后，校验isbn
        :param isbn: 待删除书籍的isbn
        :return: True或Fales
        '''
        #shoppings为购物车中，当前登录用户的所有书籍信息，self.customerinfo[0]为customerid
        shoppings = self.db.query_shopping(self.customerinfo[0])
        isbns = []  # 声明空列表，存放购物车里书籍的isbn
        for i in shoppings:  # shoppings为查询购物车表返回的数据，（'书名', 'ISBN', '作者',  '出版社', '单价', '购买数量'）
            isbns.append(i[1])  #将所有isbn放到列表中
        if isbn in isbns:
            return True
    def delete_shopping_one(self,isbn):            #删除购物车里某本书籍的记录
        self.db.delete_shopping_one(self.customerinfo[0],isbn)
    def show_pay(self):  #订单支付确认前的展示和校验
        #1、校验购物车中是否有书，--无书则提
        #2、校验购物车中的购买数量小等于当前库存--提示删除书籍才能支付订单
        #3、有书，小于当前库存，则展示：书籍isbn,单价，总价
        #shopping为查询购物车表返回的数据，元组的每个元素（'书名', 'ISBN', '作者', '出版社', '单价', '购买数量'）
        shoppings=self.db.query_shopping(self.customerinfo[0])
        pays=[]  #返回值
        if shoppings:
            self.total_prices=0 #计算购物车中所有书籍的总价
            for i in shoppings:
                pay = []
                #shoppings[i][1]为isbn
                qua=self.db.query_inventory(i[1])  #qua为库存表中isbn书籍对应的记录，（id,bookinfoid,数量）
                if i[5]<=qua[2]:
                    total_price=i[4]*i[5]   #购物车中某一书籍的总价
                    self.total_prices+=total_price
                    pay.append(i[0])
                    pay.append(i[1])
                    pay.append(i[4])
                    pay.append(total_price)
                    pays.append(pay)
                else:
                    msg='购物车中ISBN为%s的书籍当前库存为%s,您购买的数量超过上限，无法下单，可删除后重新选择数量！'%(i[1],qua[2])
                    return 0,pays,msg
            msg='您需要支付的总金额为：%.2f元'%self.total_prices
            return 1,pays,msg
        else:
            return 0, pays, '购物车里没有宝贝!'
    def pay(self):
        #用户确认订单支付后，更新数据库
        #1、插入数据到订单总表orders,self.customerinfo[0]为customerid,self.total_prices为订单总价
        ordersid=self.db.insert_orders(self.customerinfo[0],self.total_prices)[0]
        #info为元组，每一个元素也是元组（bookinfoid,购买数量,销售额，isbn）
        info=self.db.query_for_ordersinfo(self.customerinfo[0])
        for i in info:
            # 2、将数据插入到订单详细表（ordersinfo）中
            self.db.insert_ordersinfo(ordersid,i[0],i[1],i[2])
            #3、更新库存:先查询原有库存，减去购买数量后，更新到库存表中
            old_quantity=self.db.query_inventory(i[3])[2]
            qua=old_quantity-i[1]
            self.db.update_inventory(i[0],qua)
        #4、清空当前用户的购物车里的数据
        self.db.empty_shopping(self.customerinfo[0])
        return '支付成功！'
    def select_order(self):
        #订单查询
        #cus_orders的每一个元素为元组（订单id,会员id,订单总价，状态）
        return self.db.query_orders(self.customerinfo[0])
    def check_receipt(self,ordersid):
        #确认收货的订单校验
        # cus_orders的每一个元素为元组（订单id,会员id,订单总价，状态）
        cus_orders = self.db.query_orders(self.customerinfo[0])
        if ordersid.isdecimal():     #1、订单编号是否为数字
            ordersid = int(ordersid)
            for i in cus_orders:   #2、订单编号是否存在
                if ordersid == i[0]:
                    if i[3]=='未确认':
                        return 1,''
                    else:
                        return 0, '此订单已确认收货，无需再确认！'
            else:
                return 0, '订单编号不存在'
        else:
            return 0,'请注意，订单编号是一串数字！'
    def receipt_ok(self,ordersid):
        #确认收货
        # 1、修改订单状态
        self.db.update_orders(ordersid)
        #2、更新销售表
        self.db.update_sales(ordersid)
        return '收货成功，欢迎再次购买！'
class BookAdmin:
    name='管理员系统处理'
    def __init__(self,db):   #db为数据库连接（DB类）的对象
        self.db=db
    def login_admin(self,name,pwd):    #管理员登录
        self.admininfo = self.db.query_admin(name)
        print(self.admininfo)
        if self.admininfo != None:  # 用户名校验
            if self.admininfo[2] == pwd:  # 密码校验
                return 1,'登录成功!'
            else:
                return 0,'密码错误！'
        else:
            return 0,"用户名不正确！"
    def grouding_book(self,name,isbn,writer,price,publish,quantity):
        ## 上架书籍，要求输入：书籍名，ISBN，作者，单价，出版社，数量；
        #校验输入信息为非空
        if all([name!='',isbn!='',writer!='',price!='',publish!='',quantity!='']):
            # 校验输入的价格为0位或1位或2位小数
            s=re.findall(r'^(([1-9]{1}\d*)|(0{1}))(\.\d{0,2})?$',price)
            if s !=[]  and quantity.isdecimal():#价格符合要求，数量为整数
                if self.db.query_isbn(isbn):  # 检查isbn是否已经存在
                    self.db.update_quantity(quantity, isbn)   #isbn存在则只更新数量（inventory表）
                    # print('入库isbn存在，更新数量')
                else:   #isbn不存在则新增
                    self.db.insert_bookinfo(name, isbn, writer, price, publish, quantity)
                    # print('入库isbn不存在，插入新的数据')
                return 1,'入库成功！'
            else:
                return 0,'输入的单价或数量有误！'
        else:
            return 0,'注意：每一项信息都不能为空！'
    def sales(self):
        #查询销售统计
        #sales中的每一个元素为元组类型，（书名，isbn,当前库存，销售量，销售额）
        return self.db.query_sales()

if __name__=='__main__':
    db = DB(name='root', pwd='', host='localhost', db='book')
    db.update_sales(5)
    b=Booksystem(db)
    d=BookAdmin(db)
    # d.sales()
    # c.login()
    # c.select_orders()
    # tup=db.query_for_ordersinfo(2)
    # print(tup)
