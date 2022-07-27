<div style="text-align: center;">
    <h1>NJMU自动打卡</h1>
</div>

<div style="text-align: center;">
    <img alt="GitHub Pipenv locked Python version" src="https://img.shields.io/github/pipenv/locked/python-version/TimeonFly/NJMU-Report?style=flat-square">
    <img alt="GitHub" src="https://img.shields.io/github/license/TimeonFly/NJMU-Report?style=flat-square">
    <img alt="GitHub Repo stars" src="https://img.shields.io/github/stars/TimeonFly/NJMU-Report?style=flat-square">
</div>

# ⚠️严正声明
**学校的健康打卡制度是国家疫情防控的重要一环,违反疫情防控有关规定需承担刑事责任.此项目仅供学习交流,不可用于违法违规用途.使用本项目造成的任何后果使用者自行承担**

# ⚙️快速使用

本项目通过腾讯云函数部署，可以实现每日健康日报的自动打卡，防止您因繁忙的工作或学习，亦或是睡懒觉而忘记了健康日报的填写。使用步骤如下：
1. 下载Release中的`depency.zip`文件，此为云函数依赖文件
2. 下载Release中的`run.zip`文件，此为运行函数
3. **请注意run.zip中的文件版本较为落后，一些bug可能未及时修复，建议clone本项目到本地或是下载源码**<br>
使用以下命令clone本项目到本地<br>
````git clone https://github.com/TimeonFly/NJMU-Report.git````
4. 解压`run.zip`或clone本项目到本地后，[安装好依赖](#setup)，填写`ID.yaml`文件 ，填写后运行`getinfo.py`，此函数用于获取您昨天填写的信息，并自动去除几个由`index.py`文件自动生成的参数
5. 运行`getinfo.py`后，`疫情打卡提交信息.txt`文件已有内容后，压缩文件夹，待上传云函数
6. `run.zip`文件中的`index.py`等文件版本较为落后，建议您下载源文件，替换`run.zip`文件中的文件以保持最新版本

# 🧩环境依赖

由于腾讯云函数目前仅支持python3.6及3.7版本，且3.7版本缺乏必要的依赖库，因此本项目使用Python3.6开发。建议您使用[Anaconda](https://www.anaconda.com)创建虚拟环境，并进行虚拟环境下依赖库管理，建议使用Pycharm编辑并运行代码。

## Anaconda

解压`run.zip`后，在解压的文件夹目录下打开`cmd`运行此命令`conda install --yes --file requirements.txt`,<span id=setup>安装依赖</span>。关于将conda添加到环境变量，您可以访问[此网页](https://blog.csdn.net/Python_Smily/article/details/105993200) 。

## PIP
  
如果您使用的是pip安装指令，在解压的文件夹目录下打开`cmd`运行此命令`pip install -r requirements.txt`，以安装依赖，关于将pip添加到环境变量，您可以访问[此网页](https://blog.csdn.net/NY_YN/article/details/111462947) 。

## pipenv

在Pycharm中使用pipenv创建环境时，会自动根据`requirements.txt`文件安装所需依赖，如果下载依赖库速度慢，您可以科学上网或将`Pipfile`文件中的`[[source]]`下的`url`更改为`https://mirrors.aliyun.com/pypi/simple`，
有关pipenv环境的创建及激活，您可以参考[此链接](https://zhuanlan.zhihu.com/p/37581807 )或是自行搜索

## 项目依赖的库如下：
详见`requirements.txt`文件
  
**由于腾讯云函数的限制，此处的`pyyaml`库并不是最新版本，使用的是旧版本开发，如果使用最新版本可能出现报错的情况**

   ```
   requests==2.27.1
   pyyaml==3.12
   pydes==2.0.1
   pycryptodome==3.10.1
   ```
# 🛠️打卡配置
在`ID.yaml`文件中按备注填写网上办事大厅的用户名(username)、密码(password)；发送邮件的邮箱(sender)，邮件授权码(password)，接受邮件的邮箱地址(receivers)，以及邮箱smtp服务器(smtp_server)等信息。

# ☁️云函数部署
**目前腾讯云函数已开始进行收费，新用户前6个月免费，建议通过学生身份购买学生优惠的套餐**

使用[腾讯云函数](https://cloud.tencent.com/product/scf '腾讯云函数')实现自动打卡,部署步骤如下：（如果您无法看到图片，您可以参考[此链接](https://zhuanlan.zhihu.com/p/139219691 '')修改hosts文件，或是采用科学上网）
<details>
<summary>展开查看</summary>

1. 点击上方腾讯云函数超链接，注册认证后，进入控制台，点击左边的层。

    ![step1](https://github.com/TimeonFly/NJMU-Report/blob/master/images/1.png)

2. 点击新建，名称随意，然后点击上传zip，选择release中的dependency.zip上传，然后选择运行环境python3.6，然后点击确定。

    ![step2](https://github.com/TimeonFly/NJMU-Report/blob/master/images/2.png)
3. 点击左边的函数服务，新建云函数，名称随意，运行环境选择python3.6，创建方式选择空白函数，按如下步骤后，点击完成。

    ![step3](https://github.com/TimeonFly/NJMU-Report/blob/master/images/3.png)
4. 点击层管理，点击绑定，选中刚刚创建的层，点击确定。

    ![step4](https://github.com/TimeonFly/NJMU-Report/blob/master/images/4.png)
5. 左边点击触发管理，创建触发器，名称随意，触发周期选择自定义，然后配置cron表达式，下面的表达式表示每天早上8点05分执行，如果需要自定义，请在`index.py`中同步修改`create_info`函数中的参数，默认是8点05分。
   
   `0 5 8 * * * *`
   
    ![step5](https://github.com/TimeonFly/NJMU-Report/blob/master/images/5.png)
6. 然后就可以测试云函数了，绿色代表云函数执行成功，红色代表云函数执行失败（失败的原因大部分是由于依赖造成的）。返回结果是success.，代表自动提交成功，如遇到问题，请仔细查看日志。

</details>

# 📰消息提醒
本项目使用邮件提醒您自动打卡是否成功，可能日后会有微信提醒。请按打卡配置配置好`ID.yaml`文件，邮件授权码以163邮箱为例。

   ![step6](https://github.com/TimeonFly/NJMU-Report/blob/master/images/6.png)

# 🖥️开发者

如果你也懂得一些`python`知识，欢迎`fork`...定制属于你自己的脚本

学校的健康日报打卡有多个入口：

- 今日校园
- 微门户
- 网上办事大厅

由于安卓抓包较为繁琐，所以本项目是基于网上办事大厅这个入口开发的，如果代码运行有问题，你可以通过网上办事大厅进入健康日报打卡，按下F12打开开发者工具，进行抓包分析。此外，**苏康码的截图需要浏览器渲染**，受制于腾讯云函数的限制，很难在云函数中实现，如果你有好的解决方法，欢迎提交commit

目前截图的问题，考虑到截图还需要保存到本地，云函数也无法提供文件保存这一功能（或许可以保存为二进制文件于内存中），所以目前较好的解决方法是本地使用`selenium`进行截图，但这个方法需要电脑每天定时开机，云端的话使用云服务器较好，但有一定的费用，鉴于学校已经很久没有收集截图了，所以暂时搁置，如果你需要提交截图的话，可以采用本地的方法
# 🎯目标

- [ ] 是否需要截图验证
- [ ] **苏康码截图**
- [ ] 行程码截图
- [ ] 微信打卡提醒
- [ ] 时间参数匹配
# ❤️致谢
此项目参考了[@ZimoLoveShuang](https://github.com/ZimoLoveShuang 'ZimoLoveShuang')大佬的 [auto-submit](https://github.com/ZimoLoveShuang/auto-submit 'auto-submit')项目，尤其是本项目的`encrypt.py`文件，非常感谢。

感谢JetBrains提供的 PyCharm 教育版软件

# 📨  联系我
如果您有建议或者bug提交，您可以通过Issues提交或是通过此邮箱timeomfly@gmail.com联系我