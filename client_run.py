#!/usr/bin/env python
# client socket

__author__ = "BraveHeart"
__version__ = 0.1

try:
    import socket, pickle
    from get_config import ReadConfigFile
except: print('请先执行pip install -r requirements -i https://pypi.tuna.tsinghua.edu.cn/simple')


def test_client_run():
    skt = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    print('TCP socket')
    skt.connect(('192.168.50.185', 4599))
    data = skt.recv(1024)
    if data: print(pickle.loads(data))
    while True:
        content = input("退出输入exit; 矫正句子输入中文; ")
        if content == 'exit': skt.close(); break
        elif all(map(lambda c: '\u4e00' <= c <= '\u9fa5', content)):
            skt.sendall(pickle.dumps(content))
            data = skt.recv(1024)
            if not data:
                break  # 连接已经关闭
            print(pickle.loads(data))
        else: print("请正确输入！")


if __name__ == '__main__':
    # 客户端测试
    test_client_run()