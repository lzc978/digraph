#!/usr/bin/env bash

if [ $USER = "root" ]; then
        echo "请使用非root用户执行该脚本"
        exit 1
else
        echo "当前用户是: $USER"
fi

#python部分信息
PYTHON_VERSION='python-3.7.4'                             #python的版本
#存放二进制包的路径
SOFTWARE_PATH='/opt/software'

pip install -r $HOME/digraph/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple


#1 步骤输出 紫色
#2 正确输出 绿色
#3 错误输出 红色
#4 提示输出 蓝色
#5 警告输出 黄色
#根据不同的颜色打印出提示信息
function echo_fun(){
  if [ $# -ge 2 ];then
      params_num=$1
      shift 1
      params_mes=$@
  else
      echo_fun 3 请至少输入两个参数 echo_fun ..
      exit
  fi
  case $params_num in
        1)
        echo -e "\n\033[35;40;1m ****************************** ${params_mes} ******************************\033[0m\r\n"
        ;;
        2)
        echo -e "\033[32;40;1m ${params_mes}\033[0m\r\n"
        ;;
        3)
        echo -e "\n\033[31;40;1m ${params_mes}\033[0m\r\n"
        ;;
        4)
        echo -e "\033[36;40;1m ${params_mes}\033[0m\r\n"
        ;;
        5)
        echo -e "\033[33;40;1m ${params_mes} \033[0m\r\n"
        ;;
        *)
        echo_fun 3 参数异常第一个参数应为1,2,3,4,5
        ;;
   esac
}

function init_dir() {
    mkdir -p $HOME/digraph/log
    echo "创建日志路径完成"
    mkdir -p $HOME/digraph/model
    echo "创建数据模型路径完成"
    mkdir -p $HOME/digraph/correct
    echo "创建文本路径完成"
}

function run() {
    pid='lsof -Pti:4599'
    if [ "$pid" = "" ];then
            echo "dg 还未启动"
    else
            kill -9 $pid
            echo 'dg 关闭成功'
    fi
    cd $HOME/digraph && nohup python dg_run.py -d
    if [ "$?" != "0" ]; then
       echo "cannot change directory" 1>&2
       exit 1
    fi
    echo "dg running!"
}

function check() {
    echo "检查部署效果"
    netstat -tnulp | grep ':4599'
    write_log "检查部署效果"
}
