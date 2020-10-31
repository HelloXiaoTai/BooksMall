from flask import  Flask,render_template,request


#创建web应用程序
app=Flask(__name__)

#写一个函数来处理浏览器发送过来的请求
#路由：通过浏览器访问过来的请求，到底交给谁来处理
#路由本质：add_url_rule（路径和函数做绑定）
#endpoint是别名
@app.route('/')   #当访问到127.0.0.1:5000/是会执行hello_world()函数
def hello_world():
    #这里来处理业务逻辑
    return 'tests.html'    #返回的数据--->响应

@app.route("/")
def index():
    return render_template("tests.html")   #此时会自动的找templates文件夹里面的tests.html文件

# 把一个变量发送到页面---从flask往页面上扔数据
@app.route("/")
def index():
    #字符串
    s="你好啊哈哈哈哈哈哈哈"
    #列表
    lis=["希澈","东海","银赫","神童","圭贤"]
    return render_template("tests.html",hello=s,lis=lis)   #此时会自动的找templates文件夹里面的tests.html文件


#通过一个案例来学习如何从页面接收数据
#登录
@app.route("/")
def index():
    return render_template("login.html")

#methods默认接收的请求为get请求
@app.route("/login",methods=['POST'])
def login():
    #接收用户名和密码
    #从页面发送过来的数据都在request中,request接收form表单的数据信息
    #{user:你写的内容，pwd:你写的内容}
    username=request.form.get("user")
    pwd=request.form.get("pwd")
    #url传参,即网页提交的是get请求
    # request.args.get()
    if username=="wangyi" and pwd=="123":
        return "登录成功"
    else:
        return render_template("login.html",msg="登录失败")

if __name__=='__main__':   #固定写法，程序的入口
    app.run(debug=True) #启动应用程序（启动一个flask项目）

#模板-->gtml
