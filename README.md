<div style="text-align: center;">
    <h1>NJMU自动打卡</h1>
    <img src="https://github.com/TimeonFly/NJMU-Report/blob/main/images/logo.png"  alt="Logo"/>
</div>

# 😶严正声明
<font color='red'>学校的健康打卡制度是国家疫情防控的重要一环,违反疫情防控有关规定需承担刑事责任.此项目仅供学习交流,不可用于违法违规用途.使用本项目造成的任何后果使用者自行承担.</font>
# ⚙️快速使用

本项目通过腾讯云函数部署，可以实现每日健康日报的自动打卡，防止您因繁忙的工作或学习，亦或是睡懒觉而忘记了健康日报的填写
# 🧩环境依赖

由于腾讯云函数目前仅支持python3.6及3.7版本，且3.7版本缺乏必要的依赖库，因此本项目使用python3.6开发，您可以使用[Anaconda](https://www.anaconda.com)创建虚拟环境，并进行虚拟环境下依赖库管理。

项目依赖的库如下：

# 🛠️打卡配置
在ID.yaml文件中按备注填写网上办事大厅的用户名、密码；邮件，邮件授权码，接受邮件的邮箱地址，以及邮箱服务器等信息

# ☁️云函数部署
使用[腾讯云函数](https://cloud.tencent.com/product/scf '腾讯云函数')实现自动打卡

# 📧消息提醒
