# -*- coding: utf-8 -*-
from Ui_login import Ui_Dialog
from UI_ZJ import *
from  UI_LH import *
import sys
import ConfigParser

class user_info:
    def __init__(self,filename):
        self.config = ConfigParser.ConfigParser()       #创建配置文件对象
        self.config.readfp(open(filename))      #打开并读取配置文件
    def get_info(self,session,key):
        return self.config.get(session,key)     #读取配置文件config中指定段的键值
    def session(self):
        return self.config.sections()       #获取所有的段

class Login(QtGui.QDialog,Ui_Dialog):
    def __init__(self, parent=None):
        global a,b,c
        super(Login, self).__init__(parent)
        self.setupUi(self)
        self.setWindowFlags(Qt.Qt.FramelessWindowHint)
        self.lineEdit_2.setEchoMode(QtGui.QLineEdit.Password)
        self.radioButton.setChecked(1)
        self.userinfo = user_info("ini\user.ini")
        self.pushButton.clicked.connect(self.login)

    #用户名与密码匹配
    def login(self):
        global name
        s = self.userinfo.session()     #调用session函数获取所有信息
        for a in s:
            username = self.userinfo.get_info(a,"username")     #调用函数get_info获取配置文件中键为username的值
            password = self.userinfo.get_info(a,"passwd")       #获取配置文件中键为passwd的值
            if self.lineEdit.text()==username and  self.lineEdit_2.text()==password:        #判断对话框中的账号和密码
                name = self.userinfo.get_info(a,"name")     #获取配置文件中键为name的值
                self.accept()  # 关闭对话框并返回1
                break
            else:
                QtGui.QMessageBox.critical(self, u'错误', u'用户名密码不匹配')        #提示用户名和密码错误

if __name__ =='__main__':
    app =QtGui.QApplication(sys.argv)       #创建QApplication对象,每个程序都会创建
    dialog = Login()
    if dialog.exec_():
        if dialog.radioButton.isChecked():      #整机
            mainWindow = Windows(name)
            mainWindow.show()
            sys.exit(app.exec_())
        elif dialog.radioButton_2.isChecked():  #老化
            windows = MainWindow()
            windows.show()
            sys.exit(app.exec_())
        elif dialog.radioButton_3.isChecked():  #单板
            print("单板")


