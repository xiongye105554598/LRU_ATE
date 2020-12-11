# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'untitled.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui,Qt
import sys,re
import thread
from Main_LH import *
from Queue import Queue

try:
    _fromUtf8 = QtCore.QString.fromUtf8
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

class Button(QtGui.QPushButton):
    def __init__(self,ID, parent=None):
        super(Button, self).__init__(parent)
        self.data = Queue()
        self.ID = ID
        self.RightMenuShow()
        self.Test = Main_Test(self.data)
        self.Consumer = Consumer(self.data)
        self.connect(self.Test, QtCore.SIGNAL('color'), self.Cell_Color)
        self.connect(self.Test, QtCore.SIGNAL('status'), self.Cell_Status)

    #右击菜单显示
    def RightMenuShow(self):
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)
        self.contextMenu = QtGui.QMenu(self)
        self.TWCU = self.contextMenu.addMenu("TWCU")
        self.BI5 = self.TWCU.addAction(u'老化')
        self.BI5.triggered.connect(lambda: self.Production(8))

    def showContextMenu(self):
        #菜单显示前，将它移动到鼠标点击的位置
        self.contextMenu.exec_(QtGui.QCursor.pos())
        #self.contextMenu.move(QtGui.QCursor.pos())
        #self.contextMenu.show()

    #IP匹配
    def input_ip_address(self,message):
        Input_IP_address,OK=QtGui.QInputDialog.getText(self, '',message,QtGui.QLineEdit.Normal, "")
        if Input_IP_address !="":
            match ="^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
            if re.match(match,Input_IP_address):
                return Input_IP_address
            else:
                return self.input_ip_address(" Cell " + str(self.ID) +u" IP地址输入错误,输入格式必须为: x.x.x.x")

    #输入设备SN
    def Cell_SN(self):
        sn, OK = QtGui.QInputDialog.getText(self, '', u"请输入Cell "+ str(self.ID)+u" 设备标签上的SN", QtGui.QLineEdit.Normal, "")
        if sn != "" and len(sn) < 13:
            self.sn = sn
        else:
            return self.Cell_SN()

    #按钮颜色
    def Cell_Color(self, message):
        self.setStyleSheet(message)

    #按钮显示
    def Cell_Status(self, Status):
        self.setText(self.IP + "\n SN: " + self.sn + "\n" + Status)

    #IP设置
    def Production(self,Value):
        if Value == 8:self.PD_Name = "TWCU"
        self.Time = time.strftime("%Y%m%d-%H%M%S", time.localtime())
        self.Cell_SN()
        self.IP = self.input_ip_address(u"请输入 Cell " + str(self.ID) + u" 地址")
        Remote_IP= self.input_ip_address(u"请输入服务器IP地址，如果没有请不要输入")
        thread.start_new_thread(self.Test.Script_Start, (Value,self.PD_Name, self.sn, self.IP,self.Time,Remote_IP))
        thread.start_new_thread(self.Consumer.write_log, (self.PD_Name, self.sn,self.Time))

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(763, 485)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.Cell1 = Button(0,self.centralwidget)
        self.Cell1.setGeometry(QtCore.QRect(10, 10, 141, 61))
        self.Cell1.setObjectName(_fromUtf8("Cell1"))
        self.Cell2 = Button(1,self.centralwidget)
        self.Cell2.setGeometry(QtCore.QRect(160, 10, 141, 61))
        self.Cell2.setObjectName(_fromUtf8("Cell2"))
        self.Cell3 = Button(3,self.centralwidget)
        self.Cell3.setGeometry(QtCore.QRect(310, 10, 141, 61))
        self.Cell3.setObjectName(_fromUtf8("Cell3"))
        self.Cell4 = Button(4,self.centralwidget)
        self.Cell4.setGeometry(QtCore.QRect(460, 10, 141, 61))
        self.Cell4.setObjectName(_fromUtf8("Cell4"))
        self.Cell5 = Button(5,self.centralwidget)
        self.Cell5.setGeometry(QtCore.QRect(610, 10, 141, 61))
        self.Cell5.setObjectName(_fromUtf8("Cell5"))
        self.Cell6 = Button(6,self.centralwidget)
        self.Cell6.setGeometry(QtCore.QRect(10, 80, 141, 61))
        self.Cell6.setObjectName(_fromUtf8("Cell6"))
        self.Cell7 = Button(7,self.centralwidget)
        self.Cell7.setGeometry(QtCore.QRect(160, 80, 141, 61))
        self.Cell7.setObjectName(_fromUtf8("Cell7"))
        self.Cell8 = Button(8,self.centralwidget)
        self.Cell8.setGeometry(QtCore.QRect(310, 80, 141, 61))
        self.Cell8.setObjectName(_fromUtf8("Cell8"))
        self.Cell9 = Button(9,self.centralwidget)
        self.Cell9.setGeometry(QtCore.QRect(460, 80, 141, 61))
        self.Cell9.setObjectName(_fromUtf8("Cell9"))
        self.Cell10 = Button(10,self.centralwidget)
        self.Cell10.setGeometry(QtCore.QRect(610, 80, 141, 61))
        self.Cell10.setObjectName(_fromUtf8("Cell10"))
        self.Cell11 = Button(11,self.centralwidget)
        self.Cell11.setGeometry(QtCore.QRect(10, 150, 141, 61))
        self.Cell11.setObjectName(_fromUtf8("Cell11"))
        self.Cell12 = Button(12,self.centralwidget)
        self.Cell12.setGeometry(QtCore.QRect(160, 150, 141, 61))
        self.Cell12.setObjectName(_fromUtf8("Cell12"))
        self.Cell13 = Button(13,self.centralwidget)
        self.Cell13.setGeometry(QtCore.QRect(310, 150, 141, 61))
        self.Cell13.setObjectName(_fromUtf8("Cell13"))
        self.Cell14 = Button(14,self.centralwidget)
        self.Cell14.setGeometry(QtCore.QRect(460, 150, 141, 61))
        self.Cell14.setObjectName(_fromUtf8("Cell14"))
        self.Cell15 = Button(15,self.centralwidget)
        self.Cell15.setGeometry(QtCore.QRect(610, 150, 141, 61))
        self.Cell15.setObjectName(_fromUtf8("Cell15"))
        self.Cell16 = Button(16,self.centralwidget)
        self.Cell16.setGeometry(QtCore.QRect(10, 220, 141, 61))
        self.Cell16.setObjectName(_fromUtf8("Cell16"))
        self.Cell17 = Button(17,self.centralwidget)
        self.Cell17.setGeometry(QtCore.QRect(160, 220, 141, 61))
        self.Cell17.setObjectName(_fromUtf8("Cell17"))
        self.Cell18 = Button(18,self.centralwidget)
        self.Cell18.setGeometry(QtCore.QRect(310, 220, 141, 61))
        self.Cell18.setObjectName(_fromUtf8("Cell18"))
        self.Cell19 = Button(19,self.centralwidget)
        self.Cell19.setGeometry(QtCore.QRect(460, 220, 141, 61))
        self.Cell19.setObjectName(_fromUtf8("Cell19"))
        self.Cell20 = Button(20,self.centralwidget)
        self.Cell20.setGeometry(QtCore.QRect(610, 220, 141, 61))
        self.Cell20.setObjectName(_fromUtf8("Cell20"))
        self.Cell21 = Button(21,self.centralwidget)
        self.Cell21.setGeometry(QtCore.QRect(10, 290, 141, 61))
        self.Cell21.setObjectName(_fromUtf8("Cell21"))
        self.Cell22 = Button(22,self.centralwidget)
        self.Cell22.setGeometry(QtCore.QRect(160, 290, 141, 61))
        self.Cell22.setObjectName(_fromUtf8("Cell22"))
        self.Cell23 = Button(23,self.centralwidget)
        self.Cell23.setGeometry(QtCore.QRect(310, 290, 141, 61))
        self.Cell23.setObjectName(_fromUtf8("Cell23"))
        self.Cell24 = Button(24,self.centralwidget)
        self.Cell24.setGeometry(QtCore.QRect(460, 290, 141, 61))
        self.Cell24.setObjectName(_fromUtf8("Cell24"))
        self.Cell25 = Button(25,self.centralwidget)
        self.Cell25.setGeometry(QtCore.QRect(610, 290, 141, 61))
        self.Cell25.setObjectName(_fromUtf8("Cell25"))
        self.Cell26 = Button(26,self.centralwidget)
        self.Cell26.setGeometry(QtCore.QRect(10, 360, 141, 61))
        self.Cell26.setObjectName(_fromUtf8("Cell26"))
        self.Cell27 = Button(27,self.centralwidget)
        self.Cell27.setGeometry(QtCore.QRect(160, 360, 141, 61))
        self.Cell27.setObjectName(_fromUtf8("Cell27"))
        self.Cell28 = Button(28,self.centralwidget)
        self.Cell28.setGeometry(QtCore.QRect(310, 360, 141, 61))
        self.Cell28.setObjectName(_fromUtf8("Cell28"))
        self.Cell29 = Button(29,self.centralwidget)
        self.Cell29.setGeometry(QtCore.QRect(460, 360, 141, 61))
        self.Cell29.setObjectName(_fromUtf8("Cell29"))
        self.Cell30 = Button(30,self.centralwidget)
        self.Cell30.setGeometry(QtCore.QRect(610, 360, 141, 61))
        self.Cell30.setObjectName(_fromUtf8("Cell30"))
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 763, 26))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menu = QtGui.QMenu(self.menubar)
        self.menu.setObjectName(_fromUtf8("menu"))
        self.menu_2 = QtGui.QMenu(self.menubar)
        self.menu_2.setObjectName(_fromUtf8("menu_2"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)
        self.action = QtGui.QAction(MainWindow)
        self.action.setObjectName(_fromUtf8("action"))
        self.action_2 = QtGui.QAction(MainWindow)
        self.action_2.setObjectName(_fromUtf8("action_2"))
        self.menu_2.addAction(self.action)
        self.menu_2.addAction(self.action_2)
        self.Test_Result = QtGui.QAction(MainWindow)
        self.menu.addAction(self.Test_Result)
        self.Test_Result.setObjectName(_fromUtf8("Test_Result"))
        self.menubar.addAction(self.menu.menuAction())
        self.menubar.addAction(self.menu_2.menuAction())
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        self.Cell1.setText(_translate("MainWindow", "Cell 1", None))
        self.Cell2.setText(_translate("MainWindow", "Cell 2", None))
        self.Cell3.setText(_translate("MainWindow", "Cell 3", None))
        self.Cell4.setText(_translate("MainWindow", "Cell 4", None))
        self.Cell5.setText(_translate("MainWindow", "Cell 5", None))
        self.Cell6.setText(_translate("MainWindow", "Cell 6", None))
        self.Cell7.setText(_translate("MainWindow", "Cell 7", None))
        self.Cell8.setText(_translate("MainWindow", "Cell 8", None))
        self.Cell9.setText(_translate("MainWindow", "Cell 9", None))
        self.Cell10.setText(_translate("MainWindow", "Cell 10", None))
        self.Cell11.setText(_translate("MainWindow", "Cell 11", None))
        self.Cell12.setText(_translate("MainWindow", "Cell 12", None))
        self.Cell13.setText(_translate("MainWindow", "Cell 13", None))
        self.Cell14.setText(_translate("MainWindow", "Cell 14", None))
        self.Cell15.setText(_translate("MainWindow", "Cell 15", None))
        self.Cell16.setText(_translate("MainWindow", "Cell 16", None))
        self.Cell17.setText(_translate("MainWindow", "Cell 17", None))
        self.Cell18.setText(_translate("MainWindow", "Cell 18", None))
        self.Cell19.setText(_translate("MainWindow", "Cell 19", None))
        self.Cell20.setText(_translate("MainWindow", "Cell 20", None))
        self.Cell21.setText(_translate("MainWindow", "Cell 21", None))
        self.Cell22.setText(_translate("MainWindow", "Cell 22", None))
        self.Cell23.setText(_translate("MainWindow", "Cell 23", None))
        self.Cell24.setText(_translate("MainWindow", "Cell 24", None))
        self.Cell25.setText(_translate("MainWindow", "Cell 25", None))
        self.Cell26.setText(_translate("MainWindow", "Cell 26", None))
        self.Cell27.setText(_translate("MainWindow", "Cell 27", None))
        self.Cell28.setText(_translate("MainWindow", "Cell 28", None))
        self.Cell29.setText(_translate("MainWindow", "Cell 29", None))
        self.Cell30.setText(_translate("MainWindow", "Cell 30", None))
        self.menu.setTitle(_translate("MainWindow", "测试记录", None))
        self.Test_Result.setText(_translate("MainWindow", "测试结果", None))
        self.menu_2.setTitle(_translate("MainWindow", "关于", None))
        self.action.setText(_translate("MainWindow", "设计人员", None))
        #self.action_2.setText(_translate("MainWindow", "版本信息", None))

class Memu_Window(QtGui.QWidget):
    def __init__(self, parent = None):
        super(Memu_Window, self).__init__(parent)
        self.setWindowFlags(Qt.Qt.WindowCloseButtonHint)

    def Display(self,Title,Name,Info = ''):
        self.setWindowTitle(Title)
        self.Lable1 = QtGui.QLabel(self)
        self.Lable1.setGeometry(QtCore.QRect(10, 20, 100, 20))
        self.Lable1.setText(Title + ": ")
        self.Lable2 = QtGui.QLabel(self)
        self.Lable2.setText("<font color=Blue><font size = 10>%s</font>" % Name)
        self.Lable2.setGeometry(QtCore.QRect(100, 2, 100, 50))
        self.Lable3 = QtGui.QLabel(self)
        self.Lable3.setText(Info)
        self.Lable3.setGeometry(QtCore.QRect(10, 30, 400, 50))

class Table(QtGui.QWidget):
    def __init__(self, parent = None):
        super(Table, self).__init__(parent)
        self.setWindowFlags(Qt.Qt.WindowCloseButtonHint)
        self.setWindowFlags(Qt.Qt.MSWindowsFixedSizeDialogHint)
        self.Lable1 = QtGui.QLabel(self)
        self.Lable1.setText("SN: ")
        self.LineEdit = QtGui.QLineEdit(self)
        self.Find = QtGui.QPushButton(self)
        self.Find.setText(u"查询")
        self.resize(600, 320)
        hbox1 = QtGui.QHBoxLayout()
        hbox1.addWidget(self.Lable1)
        hbox1.addWidget(self.LineEdit)
        hbox1.addWidget(self.Find)
        self.TableView = QtGui.QTableView(self)
        hbox2 = QtGui.QVBoxLayout()
        hbox2.addLayout(hbox1)
        hbox2.addWidget(self.TableView)
        self.setLayout(hbox2)
        self.TableView_Set()
        self.Find.clicked.connect(self.Result_Show)

    def TableView_Set(self):
        self.model = QtGui.QStandardItemModel(self.TableView)
        # 设置表格属性：
        self.model.setRowCount(100)
        self.model.setColumnCount(4)
        # 设置表头
        self.model.setHeaderData(0, QtCore.Qt.Horizontal, _fromUtf8(u'产品名称'))
        self.model.setHeaderData(1, QtCore.Qt.Horizontal, _fromUtf8(u'产品序号'))
        self.model.setHeaderData(2, QtCore.Qt.Horizontal, _fromUtf8(u'测试结果'))
        self.model.setHeaderData(3, QtCore.Qt.Horizontal, _fromUtf8(u'测试时间'))
        self.TableView.setModel(self.model)
        # 设置列宽
        self.TableView.setColumnWidth(0, 100)
        # 设置单元格禁止更改
        # self.tableView.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        # 表头信息显示居左
        # self.tableView.horizontalHeader().setDefaultAlignment(QtCore.Qt.AlignLeft)
        # 表头信息显示居中
        self.TableView.horizontalHeader().setDefaultAlignment(QtCore.Qt.AlignCenter)

    def Result_Show(self):
        SN = self.LineEdit.text()
        try:
            if not os.path.exists(os.getcwd() + "\\Record"):
                    os.makedirs(os.getcwd() + "\\Record")
            Path = os.getcwd() + "\\Record\\"
            Data = open(Path + 'Upgrade.log', "r")
            i = 0
            for line in Data.readlines():
                if str(SN) in str(line):
                    data = line.split(" ")
                    print data[1]
                    self.model.setItem(i, 0, QtGui.QStandardItem(_fromUtf8(data[0])))
                    self.model.setItem(i, 1, QtGui.QStandardItem(_fromUtf8(data[1])))
                    self.model.setItem(i, 2, QtGui.QStandardItem(_fromUtf8(data[3])))
                    if data[3] == "Fail":
                        self.model.setItem(i, 2, QtGui.QStandardItem(_fromUtf8(data[3])))
                        # 设置字体颜色
                        self.model.item(i, 2).setForeground(QtGui.QBrush(QtGui.QColor(255, 0, 0)))
                    else:
                        self.model.setItem(i, 2, QtGui.QStandardItem(_fromUtf8(data[3])))
                    self.model.setItem(i, 3, QtGui.QStandardItem(_fromUtf8(data[8])))
                    i = i+1
            Data.close()
        except Exception, e:
            print e

class MainWindow(QtGui.QMainWindow):
    def __init__(self,parent=None):
        super(MainWindow, self).__init__(parent)
        self.new = Ui_MainWindow()
        self.new.setupUi(self)
        self.setFixedSize(self.width(), self.height())      #设置固定大小
        self.setWindowTitle(u"四川飞天联合系统技术有限公司-老化测试")
        #界面Memu参数传递
        self.Designer(u"设计人员",u"熊军")
        self.Version(u"版本信息",u"正式版本")
        self.Result_Check(u"测试记录查询")

        self.new.menu.setToolTip('Test Record')  # 鼠标悬停提示
        self.new.menu_2.setToolTip('about')  # 鼠标悬停提示

    def Designer(self,Title,User):
        self.designer = Memu_Window()
        self.designer.resize(200, 100)
        self.designer.Display(Title,User)
        self.new.action.triggered.connect(self.designer.show)

    def Version(self,Title,Version):
        self.version = Memu_Window()
        self.version.resize(300, 100)
        self.version.Display(Title,"<font color=Blue><font size = 5>%s</font>" % Version)
        self.new.action_2.triggered.connect(self.version.show)

    def Result_Check(self,Title):
        self.Record = Table()
        self.Record.setWindowTitle(Title)
        self.new.Test_Result.triggered.connect(self.Record.show)

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    windows = MainWindow()
    windows.show()
    sys.exit(app.exec_())
