# -*- coding: utf-8 -*-
from PyQt4 import QtCore
import os,time,socket,datetime,codecs
import telnetlib,thread
import paramiko
import ConfigParser

import sys
import gc
reload(sys)
sys.setdefaultencoding('utf8')

#ssh登录
class ssh():
    def __init__(self,host,username,passwd):
        self.s = paramiko.SSHClient()
        self.s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.s.connect(hostname=host,port=22, username=username, password=passwd,timeout = 30)
        self.ssh = self.s.invoke_shell()
        time.sleep(2)

    def Send(self,Command):
        self.ssh.send(str(Command) + '\r')
        time.sleep(1)

    def Recv(self,Buff_Size,click_time):
        try:
            buff = self.ssh.recv(Buff_Size,click_time)
        except:
            self.Send("\n")
            buff = self.ssh.recv(Buff_Size, click_time)
        return buff

    #关闭连接
    def Close(self):
        self.s.close()

#获取配置文件信息
class Config_ini():
    def __init__(self,filename):
        self.config = ConfigParser.ConfigParser()       #创建配置文件
        self.config.readfp(open(filename))      #打开并读取配置文件
    def get_info(self,session,key):
        return self.config.get(session,key)     #读取配置文件config中指定段的键值

    def session(self):
        return self.config.sections()           #获取所有的段

    def option(self,session):
        return self.config.options(session)     #得到指定段的所有信息

    def set(self,session,option,value):
        return self.config.set(session,option,value)        #修改配置文件的值

#log信息保存
class Consumer(QtCore.QThread):
    def __init__(self,queue,parent = None):
        super(Consumer,self).__init__(parent)
        self.data = queue

    def write_log(self,PD,SN,Time):
        if not os.path.exists(os.getcwd() + "\\log"):
            os.makedirs(os.getcwd() + "\\log")
        Path = os.getcwd() + "\\log\\"
        self.data_file = Path + PD + "_aging_" + SN + "_" + Time + ".log"
        while True:
            s = self.data.get()
            F = codecs.open(self.data_file, "a+",encoding='gb18030')
            F.write(s)
            F.close()

#主测试程序
class Main_Test(QtCore.QThread):
    def __init__(self,queue,parent = None):
        super(Main_Test,self).__init__(parent)
        self.data = queue
        self.isWait = True
        self.working = True
        self.Red = "QPushButton{background-color:RED}"
        self.Yellow = "QPushButton{background-color:YELLOW}"
        self.Green = "QPushButton{background-color:GREEN}"
        self.Config_ini = Config_ini("ini/Paramiters.ini")
        self.CWSU_aging_time = int(self.Config_ini.get_info("CWSU", "aging_time"))
        self.CWSU_PASSWORD=self.Config_ini.get_info("CWSU", "password1")

    #获取本地IP地址
    def Local_IP(self):
        Local_IP = socket.gethostbyname(socket.gethostname())   #获取本地ip
        return Local_IP

    #连接设备
    def Connection(self, host):
        username = "admin"
        passwd = "Feitianlianhe"
        try:
            self.Connect = ssh(str(host), username, passwd)  # ssh连接服务器
            self.Login_Shell()
        except Exception, e:
            self.Test_Fail(str(e))

    #发送接收数据
    def Send_Command(self,Command,Prompt='# ',Timeout=10,click_time=2):
        try:
            buff = ""
            log = ""
            self.Connect.Send(Command)
            time.sleep(1)
            runtime = datetime.datetime.now()
            while Prompt not in buff:
                buff = ""
                time.sleep(3)
                buff += self.Connect.Recv(1024,click_time)
                log += buff
                self.data.put(buff)
                steptime = datetime.datetime.now()
                if (steptime - runtime).seconds > Timeout:
                    self.Test_Fail(u"超时, %s 不能找到" % Prompt)
                    break
            return log
        except Exception:
            self.Connection(self.Host)
            #self.Test_Fail(u"%s 不能找到" % Prompt)

    #保存测试记录
    def Save_Result(self,SN,Status,Time):
        try:
            if not os.path.exists(os.getcwd() + "\\Record"):
                os.makedirs(os.getcwd() + "\\Record")
            Path = os.getcwd() + "\\Record\\"
            F = open(Path + 'Upgrade.log', "a+")
            F.seek(0,0)
            F.write("\n" + self.PD + " " + str(SN) + " " + Status + " , Test time : " + str(Time))
            F.close()
        except Exception, e:
            return str(e)

    #登录方法
    def Login_Shell(self):
        self.Send_Command("man", "(Enter)")
        self.Send_Command("", ":")
        self.Send_Command("12345678", "#")
        self.Send_Command("rootprivilege", "(privilege)#")
        self.Send_Command("_admin_shell_", ":")
        self.Send_Command("_fdaCVIbew$%^&*vcmzCnv+m_")

    #通过开头和结尾字符串获取中心字符串
    def GetMiddleStr(self,content,startStr,endStr):
        try:
            startIndex = content.index(startStr)
            if startIndex >= 0:
                startIndex += len(startStr)
            endIndex = content.index(endStr)
            return content[startIndex:endIndex].strip()
        except Exception,e:
            self.Test_Fail(str(e))

    #设置颜色
    def Set_Color(self,message):
        self.emit(QtCore.SIGNAL('color'),message)

    #设置状态
    def Set_Status(self,message):
        self.emit(QtCore.SIGNAL('status'),message)

    #测试通过提示
    def Test_Pass(self,message):
        self.working = False
        self.Save_Result(self.SN," Pass",self.Time)         #保存通过结果
        self.data.put(message)                              #入队列
        self.Set_Color(self.Green)                          #测试通过显示为绿色
        self.Set_Status(message)                            #按钮显示状态

    #测试失败提示
    def Test_Fail(self,message):
        self.working = False
        self.error_count = self.error_count + 1
        self.Save_Result(self.SN, " Fail", self.Time)       #保存失败结果
        self.Set_Color(self.Red)                            #测试失败显示红色
        Faillentime = datetime.datetime.now()               #fail当前时间
        second = (Faillentime - self.starttime).total_seconds()     #获取时间总差值秒数
        Time = u"测试时间：" + self.Running_time(second)     #获得老化时间
        self.Set_Status(message + "\n" + Time)              #按钮显示状态
        self.data.put(message + "  " + Time)                #入队列
        thread.exit_thread()                                #线程结束

    #测试开始信号
    def Test_Running(self,message):
        self.Set_Color(self.Yellow)         #显示黄色
        self.Set_Status(message)

    #运行时间
    def Running_time(self,second):
        h = int(second/3600)
        m = int((second - h*3600)/60)
        s = int(second - h*3600 - m*60)
        test_time = str(h) + "h:" + str(m) + "m:" + str(s) + "s"
        return test_time

    #程序运行
    def Script_Start(self,Value,PD,SN,Host,Time,Remote_IP = None):
        self.working = True
        self.PD = PD
        self.SN = SN
        self.Host = Host
        self.Value =Value
        self.Time=Time
        self.error_count = 0
        self.starttime = datetime.datetime.now()        #获取本地时间
        self.endtime = self.starttime + datetime.timedelta(hours=self.CWSU_aging_time)        #设置结束时间
        self.Test_Running(u'登录设备')       #登录信号
        self.Connection(self.Host)      #连接设备
        time.sleep(5)
        self.BI(Remote_IP)              #老化测试

    #老化测试
    def BI(self,Remote_IP):
        iperf = os.popen("tasklist|find /c \"iperf.exe\"")  # 执行统计iperf进程命令
        iperf_number = iperf.read()  # 读取iperf进程数量
        if int(iperf_number) < 1:
            os.system("start /b iperf.exe -s -w1m&")  # 后台运行iperf
        os.system('netsh firewall set opmode disable')  # 关闭windows系统防火墙
        os.system(
            'reg add HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\W32Time\TimeProviders\NtpServer /v Enabled /t REG_DWORD /d 1 /f')  # 修改注册表
        os.system(
            'reg add HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\W32Time\Config /v AnnounceFlags /t REG_DWORD /d 5 /f')  # 修改注册表
        os.system("net stop w32time & net start w32time")  # 停止和启动windows系统NTP服务
        self.Test_Running(u"老化测试")               #开始老化信号
        self.VersionCheck()                         #版本检测
        self.MAC_check()                            #MAC地址检测
        self.Clock_Test()                           #时钟检测
        i = 0
        while self.working == True:
            time.sleep(5)
            self.ShowTemperature()                  #温度检测
            self.MemeryCheck()                      #内存检测
            self.Discrete()                         #离散量测试
            if Remote_IP != None:
                self.EthSpeedCheck(Remote_IP)       #网口速率测试
            self.Clean_Caches()                     #清理缓存
            print(i)
            if  i % 300 == 0:
                self.AVSP()                             #卫星板检测
            Finish_time = datetime.datetime.now()       #当前最新时间
            if (Finish_time - self.endtime).days >= 0:
                self.Test_Pass(u"老化测试成功")
                break
            gc.collect()
            i=i+1
            print('i:',i)

    # 版本检测
    def VersionCheck(self):
        self.Test_Running(u"版本检测")
        self.Send_Command("sed -n '1,3p' /sbin/PRODUCT_MESSAGE &", "Done", 30)
        self.Send_Command('swv_read')
        self.Send_Command('spn_read')
        self.Send_Command('mod_read')
        self.Send_Command('board_pn_read')
        s = self.Send_Command("vershow &", "Done", 60)
        if "failed" in s:
            self.Test_Fail(u"版本未完全升级")

    #MAC地址检测
    def MAC_check(self):
        self.Test_Running(u"MAC地址检测")
        MAC = self.Send_Command("ifconfig | grep eth0")
        if "5C:E0:CA" not in MAC:
            self.Test_Fail(u"MAC地址格式错误")

    #温度检测
    def ShowTemperature(self):
        self.Test_Running(u"温度检测")
        temp = self.Send_Command("tmp_get")
        temp = self.GetMiddleStr(str(temp), 'tmp_get', "~ # ")
        if int(temp) > 96:
            self.Test_Fail(u"温度超过96℃,当前温度：%s℃" % temp)

    #时钟检测
    def Clock_Test(self):
        self.Test_Running(u"NTP 检测")
        self.Send_Command("sntp -s %s " % self.Local_IP())     #时间同步
        time.sleep(5)
        date = self.Send_Command("date")            #获取设备时间
        clock = str(datetime.datetime.now().year)   #获取本地时间
        if clock not in date:
            self.Test_Fail(u"时钟错误")

    #内存检测
    def MemeryCheck(self):
        self.Test_Running(u"内存检测")
        self.Send_Command("iostat -m")
        mem = self.Send_Command("free | grep Mem | awk '{print $2}'", "#", 30)
        mem = self.GetMiddleStr(str(mem), "}'", "~ #").strip()
        if float(mem) < 512000:
            self.Test_Fail(u"内存 ＜512MB")

    #离散量检测
    def Discrete(self):
        self.Test_Running(u"离散量检测")
        for i in range(1, 5):
            self.Send_Command("hi8425_cfg wrDiscOut %s low" % str(i))
        log = self.Send_Command("hi8425_cfg rdDiscIn", '#', 5)
        if "0x7f" not in log:
            self.Test_Fail(u"离散量设置低位失败")
        for i in range(1, 5):
            self.Send_Command("hi8425_cfg wrDiscOut %s high" % str(i))
        log = self.Send_Command("hi8425_cfg rdDiscIn", '#', 5)
        if "0x0" not in log:
            self.Test_Fail(u"离散量设置高位失败")
        for i in range(1, 5):
            self.Send_Command("hi8425_cfg wrDiscOut %s low" % str(i))
        log = self.Send_Command("hi8425_cfg rdDiscIn", '#', 5)
        if "0x7f" not in log:
            self.Test_Fail(u"离散量设置低位失败")

        self.Test_Running(u"429测试")
        self.Send_Command("hi3593_c0_cfg setRx2BitRate high", '#', 5)
        log = self.Send_Command("hi429_sendmsg_user_chip", '#', 5)
        if "OK" not in log:
            self.Test_Fail(u"429测试失败")

    #网口速率
    def EthSpeedCheck(self,Remote_IP):
        self.Test_Running(u"网口速率检测")
        Ping_message = self.Send_Command("ping %s -c5" % Remote_IP)
        if "Host Unreachable" in Ping_message:
            self.Test_Fail(u"iperf 服务器不通")
        else:
            Eth_Speed = self.Send_Command("iperf -c %s -w1m -i1 -t30 | grep '0.0-3' " % Remote_IP,"#", 60,10)
            if "Broken pipe" in Eth_Speed:
                self.Test_Fail(u"Iperf 服务器不通")

    #清除内存
    def Clean_Caches(self):
        self.Send_Command("echo 3 > /proc/sys/vm/drop_caches &")
        time.sleep(3)
        self.Send_Command("free -m")
        self.Send_Command('cd /')

    #卫星板检测
    def AVSP(self):
        self.Test_Running(u"卫星板检测")
        Sate_IP = '192.168.1.1'
        self.Connect = ssh(Sate_IP, 'root', self.CWSU_PASSWORD)
        self.Send_Command("uptime")                         #查询卫星板运行时间
        self.Send_Command("service idirect_falcon stop","# ",90,30)
        self.Send_Command("flashdbmgr --set wd stop","# ",30,5)
        self.Send_Command("killall lookbusy")
        self.Send_Command("startavsp.sh","Username:",300,20)
        self.Send_Command("admin", "word:")
        self.Send_Command("iDirect", ">")
        self.Send_Command("board info",">",30,10)
        self.Test_Running(u"CX780 温度检测")
        tem = self.Send_Command("temperature", ">", 10)
        if 'LM73' not in tem and 'FPGA' not in tem:
            self.Test_Fail(u"未获取到CX780温度")
        self.Test_Running(u"CX780 Ber检测")
        self.Send_Command("stresstest on", '> ',1800,60)
        result = self.Send_Command("stresstest result", "> ", 600, 30)
        if "Total Fails		: 0" in result:
            if "Cumulative Errors 0" not in result:
                self.Test_Fail(u"Ber 测试失败")
        else:
            self.Test_Fail(u"AVSP 压力测试失败")
        self.Send_Command("tx cw on", '>', 60, 10)
        self.Send_Command("tx freq 950", '>', 60, 10)
        self.Send_Command("tx power 0", '>', 60)
        RX=self.Send_Command("rx power", '>', 60,20)
        RX1 = self.GetMiddleStr(str(RX),'RX Power: ','[console]').strip()
        if float(RX1) <= -25 or float(RX1) >= -10:
            self.Test_Fail(U'CX780 BER RX Power值为 %s,测试失败' % RX1)

        self.Send_Command("tx power -20", '>', 60)
        RX=self.Send_Command("rx power", '>', 60,20)
        RX1 = self.GetMiddleStr(str(RX),'RX Power: ','[console]').strip()
        if float(RX1) <= -45 or float(RX1) >= -30:
            self.Test_Fail(U'CX780 BER RX Power值为 %s,测试失败' % RX1)

        self.Send_Command("tx power -40", '>', 60)
        RX = self.Send_Command("rx power", '>', 60, 20)
        RX1 = self.GetMiddleStr(str(RX), 'RX Power: ', '[console]').strip()
        if float(RX1) <= -65 or float(RX1) >= -55:
            self.Test_Fail(U'CX780 BER RX Power值为 %s,测试失败' % RX1)
        self.Send_Command("tx cw off", ">", 20, 10)
        self.Send_Command("stresstest off", '> ', 1800, 60)

        self.Test_Running(u"CX780 NET检测")
        self.Send_Command("exit", "#")
        if int(self.GetMiddleStr(self.Send_Command("ps | grep -c iperf"),"iperf","#")) < 2:
            self.Send_Command("iperf -s &\r")
        self.Connection(self.Host)
        Eth_Speed=self.Send_Command("iperf3 -c %s -w1m -i1 -t30 | grep '0.00-3' &" % Sate_IP,"Done",60,10)
        if "Broken pipe" in Eth_Speed:
            self.Test_Fail(u'CX780 Iperf服务器不通')
