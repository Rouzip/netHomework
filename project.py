#coding=utf-8
# author :Rouzip
# Time:2017.3.12
# version:1.1.1
from socket import *
import struct
import os


class project(object):
    HOST = '202.197.61.231'
    PORT = 10086
    # 服务器地址
    ADR = (HOST, PORT)
    def __init__(self):
        # 连接到服务器
        try:
            self.socketCilent = socket(AF_INET, SOCK_STREAM)
            self.socketCilent.connect(self.ADR)
            while True:
                choice = self.sendMSG()
                if 'Put' == choice:
                    self.Put()
                elif 'Get' == choice:
                    self.Get()
                elif 'ListAll' == choice:
                    self.listAll()
                else:
                    break
        except socket.error as exc:
            print('Socket error {0}'.format(exc))
        finally:
            self.socketCilent.close()


    # 向服务器发送消息
    def sendMSG(self):
        mesg = input('Please input your command:ListAll  Put  Get  exit\n')
        choice = ['ListAll', 'Put', 'Get', 'exit']
        for i in choice:
            if mesg == i:
                break
        # 选择错误
        else:
            print('error, please choose again!')
            mesg = self.sendMSG()
        return mesg


    # 显示服务器列表
    def listAll(self):
        listMsg = struct.pack('!B', 1)
        # 发送消息
        self.socketCilent.send(listMsg)
        rec = self.socketCilent.recv(1024)
        mesSign, listLen = struct.unpack('!BH',rec)
        print('----------------SIGN-----------------\n\n{0}'.format(mesSign))
        print('-------------LISTLENGTH----------------\n{0}'.format(listLen))
        dataLen = 0
        while dataLen < listLen:
            data = self.socketCilent.recv(1024)
            print(str(data,encoding='utf-8'))
            dataLen += len(data)
        self.socketCilent.close()
        # 重新连接
        self.socketCilent = socket(AF_INET,SOCK_STREAM)
        self.socketCilent.connect(self.ADR)



    # 从服务器下载文件
    def Get(self):
        fileName = input('Please input the file you want to download:')
        nameLen = len(fileName.encode('utf-8'))
        getInfo = struct.pack('!BB'+str(nameLen)+'s',\
                              0,\
                              nameLen,\
                              bytes(fileName,encoding='utf-8'))
        self.socketCilent.send(getInfo)
        rec = self.socketCilent.recv(1024)
        # 文件下载成功
        if rec[0] == 2:
            fileSize, = struct.unpack('!L',bytes(rec[1:]))
            receSize = 0
            # 储存进缓存区，然后写入文件
            with open(fileName,'wb') as fp:
                while receSize<fileSize:
                    fileData = self.socketCilent.recv(1024)
                    receSize += len(fileData)
                    fp.write(fileData)
            print('File has received successfully!')
            self.socketCilent.close()
        # 文件下载失败，服务器传回错误信息
        else:
            errSize = rec[1]
            errInfo = self.socketCilent.recv(errSize)
            print(str(errInfo,encoding = 'utf-8'))
            self.socketCilent.close()
        # 重新连接
        self.socketCilent = socket(AF_INET,SOCK_STREAM)
        self.socketCilent.connect(self.ADR)


    # 从本地上传文件
    def Put(self):
        fileName = input('Please input the file you want to input:')
        # 判断本地是否有这个文件
        dir = os.listdir('.')
        for i in dir:
            if i == fileName:
                break
        else:
            print('Don\' has this document, please choose again!')
            self.Put()
        nameLen = len(fileName.encode('utf-8'))
        # 打开并读取文件
        with open(fileName,'rb') as fp:
            fileData = bytes()
            for line in fp:
                fileData += line
        fileLength = len(fileData)
        putInf = struct.pack('!BBL' + str(nameLen) + 's'+str(fileLength)+'s',\
                            2,\
                            nameLen,\
                            fileLength,\
                            bytes(fileName,encoding='utf-8'),\
                            fileData)
        # 发送文件
        self.socketCilent.send(putInf)
        print('Input successfully!')
        self.socketCilent.close()
        # 重新连接
        self.socketCilent = socket(AF_INET,SOCK_STREAM)
        self.socketCilent.connect(self.ADR)

# 主函数调用
if __name__ == '__main__':
    p = project()

