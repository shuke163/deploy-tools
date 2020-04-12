#!/bin/sh

ip=$1
password=`cat global.conf|grep -v ^#|grep ssh_pwd|awk -F ':' '{print$2}'`
port=`cat global.conf|grep -v ^#|grep ssh_port|awk -F ':' '{print$2}'`
if [ ! -f /root/.ssh/id_rsa ];then
                ssh-keygen  -t rsa -P '' -f /root/.ssh/id_rsa
fi
if [ ! -z $password ]; then
	echo $password > mypwd
	rpm -ivh packages/centos7/sshpass-1.06-2.el7.x86_64.rpm
	sshpass -f mypwd ssh-copy-id -o StrictHostKeyChecking=no -p $port $ip
else
	key=`cat global.conf|grep -v ^#|grep ssh_key|awk -F ':' '{print$2}'`
	if [ -z $key ]; then
		echo "no password no key, can not do anything!"
		exit
	else
		rsa=`cat /root/.ssh/id_rsa.pub`
		ssh -i $key -o StrictHostKeyChecking=no -p $port $ip "echo $rsa >> /root/.ssh/authorized_keys"
		ssh -i $key -o StrictHostKeyChecking=no -p $port $ip "chmod 600 /root/.ssh/authorized_keys"
		echo "$ip set ok"
	fi
fi
