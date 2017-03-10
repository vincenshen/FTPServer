FTP Readme

作者：沈洪斌
博客：http://www.cnblogs.com/vincenshen/

程序介绍：
	实现登录md5加密认证
	实现dir查看文件列表 （只针对windows平台）
	实现get下载文件
	实现put上传文件
	断点续传（未实现）
	打印进度条
	文件一致性校验（未实现）
	磁盘配额（未实现）
	
程序目录结构：

	FTPServer #FTPserver程序主目录
	│
	├──bin
	│   ├── server.py  #FTPserver接口
	│ 	
  	├──core
	│   ├── ftpserver.py  #主逻辑功能程序
  	│
	├──db	#用户账户存储目录
	│
	├──conf
	│   ├── settings.py # 配置文件
	│
	├──ftproot # 用户FTP根目录


	FTPClient #FTPClient程序主目录
	│
	├──bin
	│   ├── client.py  #FTPclient接口
	│ 	
  	├──core
	│   ├── clientserver.py  #主逻辑功能程序
  	│
	├──conf
	    ├── settings.py # 配置文件


注意事项：
	该程序使用python3版本编写，不兼容python2版本
	
使用方法：
	bin/client.py  ftpclient启动接口
	bin/server.py  ftpserver启动接口
	
	dir 查看FTP根目录文件列表
	get filename 下载文件
	put filename 上传文件
	

版本：
     1.0
	
	
更新日志：
     v1.0 2017.03.9
	
	
