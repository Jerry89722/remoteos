#########################################################################
# File Name: boot.sh
# Author: Jerry
# mail: zhangjie89722@163.com
# Created Time: 2020-03-19
#########################################################################
#!/bin/sh
#set -v

# TODO , 用于控制此系统的运行, 目前还没做好, 无法正常使用
start(){
	python manage.py runserver 0.0.0.0:8000
}

stop(){
  echo "http stop"
}

restart(){
	echo "restart"
	stop
	start
}

case $1 in
	"start")
		start
		exit 0
		;;
	"stop")
		stop
		exit 0
		;;
	"restart")
		restart
		exit 0
		;;
	*)
		echo "unknown command"
		exit 0
		;;
esac


