# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'untitled.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!
from PyQt4 import QtCore,QtGui,Qt
import re,sys,os,time,thread
from Main_ZJ import *
from Queue import Queue     #队列

try:
    _fromUtf8 = QtCore.QString.fromUtf8     #将utf8编码赋值变量
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

#创建主窗口类
class Ui_Form(object):
    #拖拽控件描述
    def setupUi(self, Form):
        Form.setObjectName(_fromUtf8("Form"))       #设置窗口名
        Form.resize(1099, 620)      #设置窗口大小
        self.centralwidget = QtGui.QWidget(Form)            #创建控件对象
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)    #窗口改变是可以伸展和搜索
        sizePolicy.setHorizontalStretch(100)
        sizePolicy.setVerticalStretch(100)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        Form.setMinimumSize(QtCore.QSize(0, 0))
        Form.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.horizontalLayout = QtGui.QHBoxLayout(Form)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.groupBox = QtGui.QGroupBox(Form)
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setMinimumSize(QtCore.QSize(500, 300))
        self.groupBox.setAlignment(QtCore.Qt.AlignJustify|QtCore.Qt.AlignVCenter)
        self.groupBox.setFlat(False)
        self.groupBox.setCheckable(False)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.groupBox1 = QtGui.QGroupBox(self.groupBox)
        self.groupBox1.setGeometry(QtCore.QRect(10, 100, 231, 161))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.groupBox1.sizePolicy().hasHeightForWidth())
        self.groupBox1.setSizePolicy(sizePolicy)
        self.groupBox1.setTitle(_fromUtf8(""))
        self.groupBox1.setObjectName(_fromUtf8("groupBox1"))
        self.label = QtGui.QLabel(self.groupBox1)
        self.label.setGeometry(QtCore.QRect(10, 10, 72, 15))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.label.setFont(font)
        self.label.setObjectName(_fromUtf8("label"))
        self.Select_PD = QtGui.QComboBox(self.groupBox1)
        self.Select_PD.setGeometry(QtCore.QRect(100, 10, 121, 22))
        self.Select_PD.setObjectName(_fromUtf8("Select_PD"))
        self.Telnet = QtGui.QCheckBox(self.groupBox1)
        self.Telnet.setGeometry(QtCore.QRect(100, 130, 71, 19))
        self.Telnet.setObjectName(_fromUtf8("Telnet"))
        self.SSH = QtGui.QCheckBox(self.groupBox1)
        self.SSH.setGeometry(QtCore.QRect(180, 130, 61, 19))
        self.SSH.setObjectName(_fromUtf8("SSH"))
        self.SSH.setChecked(1)
        self.label_13 = QtGui.QLabel(self.groupBox1)
        self.label_13.setGeometry(QtCore.QRect(10, 130, 72, 15))
        self.label_13.setObjectName(_fromUtf8("label_13"))
        self.Host_IP = QtGui.QLineEdit(self.groupBox1)
        self.Host_IP.setGeometry(QtCore.QRect(100, 40, 121, 21))
        self.Host_IP.setObjectName(_fromUtf8("Host_IP"))
        self.label_3 = QtGui.QLabel(self.groupBox1)
        self.label_3.setGeometry(QtCore.QRect(10, 40, 72, 15))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.label_4 = QtGui.QLabel(self.groupBox1)
        self.label_4.setGeometry(QtCore.QRect(10, 100, 91, 16))
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.Server_IP = QtGui.QLineEdit(self.groupBox1)
        self.Server_IP.setGeometry(QtCore.QRect(100, 100, 121, 21))
        self.Server_IP.setObjectName(_fromUtf8("Server_IP"))
        self.groupBox_4 = QtGui.QGroupBox(self.groupBox)
        self.groupBox_4.setGeometry(QtCore.QRect(10, 270, 231, 181))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_4.sizePolicy().hasHeightForWidth())
        self.groupBox_4.setSizePolicy(sizePolicy)
        self.groupBox_4.setObjectName(_fromUtf8("groupBox_4"))
        self.label_9 = QtGui.QLabel(self.groupBox_4)
        self.label_9.setGeometry(QtCore.QRect(10, 20, 72, 15))
        self.label_9.setObjectName(_fromUtf8("label_9"))
        self.label_10 = QtGui.QLabel(self.groupBox_4)
        self.label_10.setGeometry(QtCore.QRect(10, 50, 72, 15))
        self.label_10.setObjectName(_fromUtf8("label_10"))
        self.label_11 = QtGui.QLabel(self.groupBox_4)
        self.label_11.setGeometry(QtCore.QRect(10, 80, 72, 15))
        self.label_11.setObjectName(_fromUtf8("label_11"))
        self.label_12 = QtGui.QLabel(self.groupBox_4)
        self.label_12.setGeometry(QtCore.QRect(10, 110, 72, 15))
        self.label_12.setObjectName(_fromUtf8("label_12"))
        self.Boot = QtGui.QLineEdit(self.groupBox_4)
        self.Boot.setGeometry(QtCore.QRect(100, 20, 121, 21))
        self.Boot.setObjectName(_fromUtf8("Boot"))
        self.Kernel = QtGui.QLineEdit(self.groupBox_4)
        self.Kernel.setGeometry(QtCore.QRect(100, 50, 121, 21))
        self.Kernel.setObjectName(_fromUtf8("Kernel"))
        self.APP = QtGui.QLineEdit(self.groupBox_4)
        self.APP.setGeometry(QtCore.QRect(100, 80, 121, 21))
        self.APP.setObjectName(_fromUtf8("APP"))
        self.Config = QtGui.QLineEdit(self.groupBox_4)
        self.Config.setGeometry(QtCore.QRect(100, 110, 121, 21))
        self.Config.setObjectName(_fromUtf8("Config"))
        self.MAC = QtGui.QLineEdit(self.groupBox_4)
        self.MAC.setGeometry(QtCore.QRect(100, 140, 121, 21))
        self.MAC.setObjectName(_fromUtf8("MAC"))
        self.label_14 = QtGui.QLabel(self.groupBox_4)
        self.label_14.setGeometry(QtCore.QRect(10, 140, 101, 16))
        self.label_14.setObjectName(_fromUtf8("label_14"))
        self.groupBox_5 = QtGui.QGroupBox(self.groupBox)
        self.groupBox_5.setGeometry(QtCore.QRect(10, 460, 231, 111))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_5.sizePolicy().hasHeightForWidth())
        self.groupBox_5.setSizePolicy(sizePolicy)
        self.groupBox_5.setObjectName(_fromUtf8("groupBox_5"))
        self.Upgrade = QtGui.QCheckBox(self.groupBox_5)
        self.Upgrade.setGeometry(QtCore.QRect(10, 20, 91, 19))
        self.Upgrade.setObjectName(_fromUtf8("Upgrade"))
        self.Test = QtGui.QCheckBox(self.groupBox_5)
        self.Test.setGeometry(QtCore.QRect(10, 50, 91, 19))
        self.Test.setObjectName(_fromUtf8("Test"))
        self.Test.setChecked(1)
        self.Modify_IP = QtGui.QCheckBox(self.groupBox_5)
        self.Modify_IP.setGeometry(QtCore.QRect(110, 50, 91, 19))
        self.Modify_IP.setObjectName(_fromUtf8("Modify_IP"))
        self.Format_Disk = QtGui.QCheckBox(self.groupBox_5)
        self.Format_Disk.setGeometry(QtCore.QRect(110, 20, 111, 19))
        self.Format_Disk.setObjectName(_fromUtf8("Format_Disk"))
        self.Rsync = QtGui.QCheckBox(self.groupBox_5)
        self.Rsync.setGeometry(QtCore.QRect(10, 80, 91, 19))
        self.Rsync.setObjectName(_fromUtf8("Rsync"))
        self.Shipout = QtGui.QCheckBox(self.groupBox_5)
        self.Shipout.setGeometry(QtCore.QRect(110, 80, 91, 19))
        self.Shipout.setObjectName(_fromUtf8("Shipout"))
        self.Start = QtGui.QPushButton(self.groupBox)
        self.Start.setGeometry(QtCore.QRect(990, 550, 71, 31))
        self.Start.setObjectName(_fromUtf8("Start"))
        self.Stop = QtGui.QPushButton(self.groupBox)
        self.Stop.setGeometry(QtCore.QRect(900, 550, 71, 31))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Stop.sizePolicy().hasHeightForWidth())
        self.Stop.setSizePolicy(sizePolicy)
        self.Stop.setObjectName(_fromUtf8("Stop"))
        self.text = QtGui.QTextEdit(self.groupBox)
        self.text.setGeometry(QtCore.QRect(250, 10, 821, 531))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.text.sizePolicy().hasHeightForWidth())
        self.text.setSizePolicy(sizePolicy)
        self.text.setSizeIncrement(QtCore.QSize(99, 100))
        self.text.setBaseSize(QtCore.QSize(100, 100))
        self.text.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.text.setAutoFillBackground(True)
        self.text.setObjectName(_fromUtf8("text"))
        self.Current_Test = QtGui.QLabel(self.groupBox)
        self.Current_Test.setGeometry(QtCore.QRect(250, 550, 431, 31))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.Current_Test.setFont(font)
        self.Current_Test.setText(_fromUtf8(""))
        self.Current_Test.setObjectName(_fromUtf8("Current_Test"))
        self.name = QtGui.QLabel(self.groupBox)
        self.name.setGeometry(QtCore.QRect(10, 10, 231, 41))        #设置标签大小与位置
        self.name.setText(_fromUtf8(""))
        self.name.setTextFormat(QtCore.Qt.AutoText)
        self.name.setAlignment(QtCore.Qt.AlignCenter)
        self.name.setObjectName(_fromUtf8("name"))      #设置标签名
        self.name_2 = QtGui.QLabel(self.groupBox)
        self.name_2.setGeometry(QtCore.QRect(10, 60, 231, 31))
        self.name_2.setText(_fromUtf8(""))
        self.name_2.setTextFormat(QtCore.Qt.AutoText)
        self.name_2.setAlignment(QtCore.Qt.AlignCenter)
        self.name_2.setObjectName(_fromUtf8("name_2"))
        self.SN = QtGui.QLineEdit(self.groupBox)
        self.SN.setGeometry(QtCore.QRect(110, 170, 121, 21))
        self.SN.setObjectName(_fromUtf8("SN"))
        self.Lab_SN_3 = QtGui.QLabel(self.groupBox)
        self.Lab_SN_3.setGeometry(QtCore.QRect(20, 170, 91, 16))
        self.Lab_SN_3.setObjectName(_fromUtf8("Lab_SN_3"))
        self.horizontalLayout.addWidget(self.groupBox)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    #将所有控件调用utf8编码重新编译并设置显示文字
    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "Form", None))       #设置窗口标题
        self.label.setText(_translate("Form", "LRU:", None))       #设置标签显示文字
        self.Telnet.setText(_translate("Form", "Telnet", None))
        self.SSH.setText(_translate("Form", "SSH", None))
        self.label_13.setText(_translate("Form", "Connection:", None))
        self.label_3.setText(_translate("Form", "LRU address:", None))
        self.label_4.setText(_translate("Form", "Server Address:", None))
        self.groupBox_4.setTitle(_translate("Form", "Upgrade Burning", None))
        self.label_9.setText(_translate("Form", "Packages:", None))
        self.label_10.setText(_translate("Form", "Kernel:", None))
        self.label_11.setText(_translate("Form", "APP:", None))
        self.label_12.setText(_translate("Form", "Config:", None))
        self.label_14.setText(_translate("Form", "MAC(后六位):", None))
        self.groupBox_5.setTitle(_translate("Form", "Test items", None))
        self.Upgrade.setText(_translate("Form", "Upgrade", None))
        self.Test.setText(_translate("Form", "Test", None))
        self.Modify_IP.setText(_translate("Form", "Modify IP", None))
        self.Shipout.setText(_translate("Form", "Factory", None))
        self.Start.setText(_translate("Form", "Start Test", None))
        self.Stop.setText(_translate("Form", "End Test", None))
        self.Lab_SN_3.setText(_translate("Form", "SN:", None))
        self.Format_Disk.setText(_translate("Form", "Formatting", None))
        self.Rsync.setText(_translate("Form", "Synchronous Data", None))


class Windows(QtGui.QWidget):
    def __init__( self,ID="", parent = None):
        super(Windows, self ).__init__(parent)
        #self.thread = Main_Test()
        self.ID= ID
        self.new = Ui_Form()        #创建Ui_Form对象
        self.new.setupUi(self)      #调用setupUi方法
        self.data = Queue()         #创建一个队列对象
        self.Main_Test = Main_Test(self.data)       #创建Main_Test对象
        self.Consumer = Consumer(self.data)         #创建一个Consumer对象
        self.setWindowTitle(u"四川飞天联合系统技术有限公司-整机测试")        #设置窗口标题
        self.setWindowFlags(Qt.Qt.MSWindowsFixedSizeDialogHint)         #禁止对话框放大缩小
        self.new.name.setText("<font color=black><font size = 8>%s</font>" % u"GNS V31")
        self.new.name_2.setText("<font color=black><font size = 4>%s</font>" % u"LRU ATE")
        self.group = QtGui.QButtonGroup(self)
        self.group.setExclusive(True)               #容器内的选项框只能选择一种
        self.group.addButton(self.new.Test)
        self.group.addButton(self.new.Upgrade)
        self.group.addButton(self.new.Modify_IP)
        self.group.addButton(self.new.Format_Disk)
        self.group.addButton(self.new.Rsync)
        self.group.addButton(self.new.Shipout)
        self.group1 = QtGui.QButtonGroup(self)
        self.group1.setExclusive(True)
        self.group1.addButton(self.new.Telnet)
        self.group1.addButton(self.new.SSH)

        self.new.Select_PD.addItem("GNS")

        self.new.Rsync.setDisabled(1)           #设置同步数据不可用
        self.new.Format_Disk.setDisabled(1)     #设置硬盘格式化不可用
        self.new.Upgrade.setDisabled(1)         #设置升级不可用
        self.new.Modify_IP.setDisabled(1)
        self.new.Shipout.setDisabled(1)

        self.new.label.setToolTip(u'LRU')  # 鼠标悬停提示
        self.new.label_3.setToolTip(u'LRU地址')
        self.new.label_4.setToolTip(u'服务器地址')
        self.new.label_13.setToolTip(u'连接方式')
        self.new.groupBox_4.setToolTip(u'升级烧录')
        self.new.groupBox_5.setToolTip(u'测试项目')
        self.new.Upgrade.setToolTip(u'升级')
        self.new.Test.setToolTip(u'测试')
        self.new.Modify_IP.setToolTip(u'修改IP')
        self.new.Shipout.setToolTip(u'出厂配置')
        self.new.Start.setToolTip(u'开始测试')
        self.new.Stop.setToolTip(u'结束测试')
        self.new.Lab_SN_3.setToolTip(u'SN')
        self.new.Format_Disk.setToolTip(u'硬盘格式化')
        self.new.Rsync.setToolTip(u'同步数据')

        #self.setWindowFlags(Qt.Qt.FramelessWindowHint)
        #窗口居中显示
        #desktop =QtGui.QApplication.desktop()
        #width = desktop.width()
        #height = desktop.height()
        #self.move((width - self.width())/2, (height - self.height())/2)

        #界面信号传递
        self.new.Start.setStyleSheet("QPushButton{background-color: LIGHTGRAY }")
        self.new.Stop.setStyleSheet("QPushButton{background-color: LIGHTGRAY }")
        self.connect(self.new.Start, QtCore.SIGNAL('clicked()'), self.Start)        #连接信号槽Start Test函数
        self.connect(self.new.Boot,QtCore.SIGNAL('selectionChanged()'),self.Get_Filename)   #连接升级文件选择方法
        self.connect(self.new.Kernel,QtCore.SIGNAL('selectionChanged()'),self.Get_Filename)
        self.connect(self.new.APP,QtCore.SIGNAL('selectionChanged()'),self.Get_Filename)
        self.connect(self.new.Config,QtCore.SIGNAL('selectionChanged()'),self.Get_Filename)
        self.connect(self.new.Test,QtCore.SIGNAL('clicked()'),self.select)          #连接测试选择框方法
        self.connect(self.new.Upgrade,QtCore.SIGNAL('clicked()'),self.select)       #连接升级选择框方法
        self.connect(self.new.Modify_IP,QtCore.SIGNAL('clicked()'),self.select)     #连接修改IP选择框方法
        self.connect(self.new.Format_Disk,QtCore.SIGNAL('clicked()'),self.select)   #连接硬盘格式化选择框方法
        self.connect(self.new.Shipout,QtCore.SIGNAL('clicked()'),self.select)       #连接出厂配置选择框方法
        self.new.Select_PD.currentIndexChanged.connect(self.GNS_select)

        self.connect(self.Main_Test,QtCore.SIGNAL('error'), self.error)             #主测试程序与设置测试错误消息显示为红色
        self.connect(self.Main_Test,QtCore.SIGNAL('output(QString)'),self.SlotAdd)  #主测试程序与测试信息追加到文本框中
        self.connect(self.Main_Test,QtCore.SIGNAL('stop'),self.SlotStop)            #主测试程序与测试信息终止
        self.connect(self.Main_Test,QtCore.SIGNAL('input'),self.input_ip_address)   #主测试程序与提示IP地址输入
        self.connect(self.Main_Test,QtCore.SIGNAL('ship'),self.Ship_Out_Address)    #主测试程序与提示外部地址输入
        self.connect(self.Main_Test,QtCore.SIGNAL('Prompt'),self.Prompt)            #主测试程序与消息选择框
        self.connect(self.new.Stop,QtCore.SIGNAL('clicked()'),self.Stop)            #主测试程序与测试程序终止
        self.connect(self.Main_Test, QtCore.SIGNAL('color'), self.Cell_Color)       #主测试程序与开始控件颜色设置
        self.connect(self.Main_Test, QtCore.SIGNAL('pass'), self.Cell_Pass)         #主测试程序与设置测试信息显示为绿色
        self.connect(self.Main_Test, QtCore.SIGNAL('dis_message'), self.display_test_information)   #主测试程序与设置测试信息显示为蓝色

    #变量定义
    def Var(self):
        self.select_PD =self.new.Select_PD.currentText()
        self.tn = self.new.Telnet
        self.SSH = self.new.SSH
        self.Host_IP =str(self.new.Host_IP.text())
        self.Server_IP=str(self.new.Server_IP.text())
        self.SN = self.new.SN.text()
        self.MAC = '5C:E0:CA:'+ self.new.MAC.text()
        self.Boot = self.new.Boot.text()
        self.Kernel = self.new.Kernel.text()
        self.APP = self.new.APP.text()
        self.Config = self.new.Config.text()
        self.Upgrade = self.new.Upgrade
        self.Test = self.new.Test
        self.Modify_IP = self.new.Modify_IP
        self.Format_Disk = self.new.Format_Disk
        self.Rsync = self.new.Rsync
        self.Shipout = self.new.Shipout

    #控件状态设置
    def select(self):
        self.new.MAC.setDisabled(1)             #设置为不可用状态
        self.new.Boot.setDisabled(1)
        self.new.Kernel.setDisabled(1)
        self.new.APP.setDisabled(1)
        self.new.Config.setDisabled(1)
        self.new.SN.setDisabled(1)
        self.new.Server_IP.setDisabled(1)
        if self.new.Shipout.isChecked():        #检测出厂配置是否选中
            self.new.Config.setDisabled(0)      #设置为可用状态
            self.new.Server_IP.setDisabled(0)   #设置为可用状态
        elif self.new.Upgrade.isChecked():      #检测升升级是否选中
            self.new.MAC.setDisabled(0)         #设置为可用状态
            self.new.Boot.setDisabled(0)
            self.new.Kernel.setDisabled(0)
            self.new.APP.setDisabled(0)
            self.new.Config.setDisabled(0)
            self.new.Server_IP.setDisabled(0)
        elif self.new.Test.isChecked():         #检测测试是否选中
            self.new.SN.setDisabled(0)          #设置为可用状态
            self.new.Server_IP.setDisabled(0)

    def GNS_select(self,message):
        if message !=9:
            self.new.Format_Disk.setDisabled(1)
            self.new.Rsync.setDisabled(1)

    #开始控件颜色设置
    def Cell_Color(self, message):
        self.new.Start.setStyleSheet(message)

    #设置测试信息显示为绿色
    def Cell_Pass(self,message):
        self.new.text.append("<font color=green><font size = 4>%s</font>" % message)

    #设置测试错误消息显示为红色
    def error(self,message):
        if message !="":
            self.new.text.append("<font color=red><font size = 4>%s</font>" %message)

    #设置测试信息显示为蓝色
    def display_test_information(self,message):
        self.new.text.append("<font color=blue><font size = 4>%s</font>"%message)

    #提示IP地址输入
    def input_ip_address(self,message):
        if message != " ":
            Input_IP_address,OK=QtGui.QInputDialog.getText(self, U"Input IP",message,QtGui.QLineEdit.Normal, "")    #弹框Input IP
            match ="^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
            if re.match(match,Input_IP_address):
                self.Main_Test.Input_IP_address = Input_IP_address
                self.Main_Test.isWait = False
            else:
                return self.input_ip_address(u"The IP address format is incorrectly entered. The format should be:x.x.x.x")

    #提示外部地址输入
    def Ship_Out_Address(self,message):
        if message != " ":
            Ship_Out_Address,OK=QtGui.QInputDialog.getText(self, U"Input IP",message,QtGui.QLineEdit.Normal, "")
            self.Main_Test.Ship_Out_Address=Ship_Out_Address
            self.Main_Test.isWait=False

    #消息选择框
    def Prompt(self,message):
        reply= QtGui.QMessageBox.information(self,u"提示框", message, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            self.Main_Test.isWait=False         #消息提示选择框为Yes，测试继续进行
        else:
            self.Stop()

    #测试信息追加到文本框中
    def SlotAdd(self, message):
        self.new.text.append(message)       #数据追加到文本显示框
        self.new.text.moveCursor(QtGui.QTextCursor.End)     #设置光标移动到文本框末尾

    #测试信息终止
    def SlotStop(self,message):
        if message == False:
            self.Consumer.working = False
            self.new.Start.setEnabled(True)
            self.new.Start.setText(u'Start Test')
            self.new.Start.setStyleSheet("QPushButton{background-color: LIGHTGRAY }")

    #测试程序终止
    def Stop(self):
        self.Consumer.working = False
        self.Main_Test.working = False
        self.new.Start.setEnabled(True)
        self.new.Start.setText(u'Start Test')
        self.new.Start.setStyleSheet("QPushButton{background-color: LIGHTGRAY }")

    #Start Test
    def Start(self):
        self.new.Start.setEnabled(False)        #设置Start Test控件为不可用状态
        self.new.Start.setStyleSheet("QPushButton{background-color:YELLOW}")    #设置测试中的按钮为黄色
        self.new.Start.setText(u"test...")          #设置控件显示为"测试中"
        self.Time = time.strftime("%Y%m%d-%H%M%S", time.localtime())        #接收并格式化返回本地时间
        self.Var()              #调用变量定义函数
        self.new.Current_Test.clear()       #清空之前数据
        self.new.text.setText(u"ID:" + self.ID)
        self.new.text.append(u"PD:" + self.select_PD)
        self.new.text.append(u"SN:" + self.SN)
        self.Consumer.working = True
        match ="^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"  #正则表达式
        if re.match(match,self.Host_IP):    #匹配设备IP
            if self.Test.isChecked():       #检测测试选择框是否选中
                thread.start_new_thread(self.Main_Test.Script_Start,(self.select_PD, self.SN,self.Time, self.Host_IP, self.Server_IP))  #产生新线程1
                thread.start_new_thread(self.Consumer.write_log, (self.select_PD, self.SN, self.Time))  #产生新线程2
            elif self.Shipout.isChecked():      #检测出厂配置选择框是否选中
                thread.start_new_thread(self.Main_Test.Ship_Out, (self.select_PD,self.Host_IP, self.Config, self.Server_IP))
            elif self.Upgrade.isChecked():      #检测升级选中框是否选中
                thread.start_new_thread(self.Main_Test.upgrade,(self.select_PD, self.Host_IP,self.Boot,self.Kernel,self.APP,self.Config, self.MAC,self.Server_IP))
            elif self.Format_Disk.isChecked():  #检测格式化选中框是否选中
                thread.start_new_thread(self.Main_Test.Format_Disk,(self.select_PD,self.Host_IP))
            elif self.Modify_IP.isChecked():    #检测修改IP选中框是否选中
                thread.start_new_thread(self.Main_Test.Modify_IP, (self.select_PD,self.Host_IP))

        else:
            QtGui.QMessageBox.warning(self,u"提示",u"Device address error",QtGui.QMessageBox.Yes , QtGui.QMessageBox.No)    #提示消息框提示
            self.new.Start.setEnabled(True)             #设置控件为可用状态
            self.new.Start.setText(u'Start Test')          #设置控件显示Start Test
            self.new.Start.setStyleSheet("QPushButton{background-color: LIGHTGRAY }")       #设置控件颜色

    #升级文件
    def Get_Filename(self):
        if not os.path.exists(os.getcwd()+ "\\TFTPFILE"):       #判断当前目录文件夹是否存在
            os.makedirs(os.getcwd()+ "\\TFTPFILE")              #若目录不存在，递归创建文件夹
        Path = os.getcwd()+ "\\TFTPFILE\\"
        filename = QtGui.QFileDialog.getOpenFileName(self,u"打开文件",  Path,  "All Files (*)")     #打开文件
        name = os.path.basename(str(filename))      #获取文件名
        if 'boot' in name:
            self.new.Boot.setText(name)     #boot单选框显示boot文件名
        elif 'kernel' in name:
            self.new.Kernel.setText(name)
        elif 'con' in name:
            self.new.Config.setText(name)
        else :
            self.new.APP.setText(name)

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    windows = Windows()
    windows.show()
    sys.exit(app.exec_())
