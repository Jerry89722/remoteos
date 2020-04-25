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
#  echo "-------- $PS1 ---------"
#	echo $PS1 | grep -qs "remoteos"
#	if [ $? != 0 ]; then
#		workon remoteos
#	fi
#
#	echo "start"
#
#	celery -A celery_tasks.tasks worker -l info &
#	pids="$!"
#	python manage.py runserver 0.0.0.0:8000 &
#	pids="$! $pids"
#	/home/zjay/usr/local/vlc/bin/vlc -I oldrc --rc-unix=/home/zjay/.vlc-cache/vlc.sock -f --network-caching 50000
#  pids="$! $pids"
#	echo "$pids" > /home/zjay/Desktop/pid.log
  echo "start"
}

stop(){
  pids=`ps aux | grep -e celery -e manage.py -e vlc | grep -v grep | awk '{print $2}'`
#  pids=`cat /home/zjay/Desktop/pid.log`
  echo "stop: $pids"
  kill -9 $pids
}

restart(){
	echo "restart"
	stop
	start
}

case $1 in
	"start")
		source virtualenvwrapper.sh
		workon remoteos
		if [ -d /media/zjay/Datas/Works/projects/remoteos ]; then
		  cd /media/zjay/Datas/Works/projects/remoteos
		else
		  exit 1
		fi
		./celery_boot.sh start &
		./http_boot.sh start &
		./vlc_boot.sh start
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


