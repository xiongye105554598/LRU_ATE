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

#Telnet登录
class Telnet():
    def __init__(self,host):
        self.telnet = telnetlib.Telnet(host, port = 10020, timeout=10)
        self.telnet.set_debuglevel(2)

    def Read(self,Prompt,Timeout):
        buff = ""
        try:
            buff += self.telnet.read_until(Prompt,Timeout)
        except:
            self.Send("\n")
            buff += self.telnet.read_until(Prompt,Timeout)
        return buff

    def Send(self,Command):
        self.telnet.write(str(Command)+'\n')

    def Close(self):
        self.telnet.close()

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

    def Recv(self,Buff_Size,click_time):
        try:
            buff = self.ssh.recv(Buff_Size,click_time)
        except:
            self.Send("\n")
            buff = self.ssh.recv(Buff_Size, click_time)
        return buff

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
        return self.config.sections()       #获取所有的段
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

    #获取本地IP
    def Local_IP(self):
        Local_IP = socket.gethostbyname(socket.gethostname())
        return Local_IP

    #连接设备
    def Connection(self,host):
        username = "admin"
        passwd = "Feitianlianhe"
        try:
            self.Connect = ssh(str(host),username,passwd)
            self.Login_Shell()
        except Exception,e:
            self.Test_Fail(str(e))

    #发送接收数据
    def Send_Command(self,Command,Prompt='#',Timeout=10,click_time=1):
        try:
            buff = ""
            log = ""
            self.Connect.Send(Command)
            runtime = datetime.datetime.now()
            #while not buff.endswith(Prompt):
            while Prompt not in buff:
                buff = ""
                time.sleep(1)
                buff += self.Connect.Recv(99999,click_time)
                log += buff
                self.data.put(buff)
                steptime = datetime.datetime.now()
                if (steptime - runtime).seconds > Timeout:
                    self.Test_Fail(u"超时, %s 不能找到" % Prompt)
                    break
            return log
        except Exception,E:
            self.Test_Fail(u"%s 不能找到" % Prompt)

    #记录结果
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
        self.Save_Result(self.SN, " Fail", self.Time)               #保存失败结果
        self.Set_Color(self.Red)                                    #测试失败显示红色
        Faillentime = datetime.datetime.now()                       #获取失败时间
        second = (Faillentime - self.starttime).total_seconds()     #获得老化时间
        Time = u"测试时间：" + self.Running_time(second)             #获得老化时间
        self.Set_Status(message + "\n" + Time)                      #按钮显示状态
        self.data.put(message + "  " + Time)                        #入队列
        thread.exit_thread()                                        #线程结束

    #测试开始提示
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
        self.starttime = datetime.datetime.now()   #获取本地时间
        self.endtime = self.starttime + datetime.timedelta(hours=48)        #设置结束时间
        self.Test_Running(u'登录设备')              #登录信号
        self.Connection(self.Host)                 #连接设备
        time.sleep(5)
        self.BI(Remote_IP)                         #老化测试

    #老化测试
    def BI(self,Remote_IP):
        iperf = os.popen("tasklist|find /c \"iperf.exe\"")  # 执行统计iperf进程命令
        iperf_number = iperf.read()                         # 读取iperf进程数量
        if int(iperf_number) < 1:
            os.system("start /b iperf.exe -s -w1m&")        # 后台运行iperf
        os.system('netsh firewall set opmode disable')      # 关闭windows系统防火墙
        os.system(
            'reg add HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\W32Time\TimeProviders\NtpServer /v Enabled /t REG_DWORD /d 1 /f')  # 修改注册表
        os.system(
            'reg add HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\W32Time\Config /v AnnounceFlags /t REG_DWORD /d 5 /f')  # 修改注册表
        os.system("net stop w32time & net start w32time")  # 停止和启动windows系统NTP服务
        self.Test_Running(U"老化测试")           #开始老化信号
        self.Check_Process()                    #测试过程提升CPU利用率
        self.VersionCheck()                     #版本检测
        self.MAC_check()                        #MAC地址检测
        while self.working == True:
            time.sleep(5)
            self.ShowTemperature()              #温度检测
            self.Clock_Test()                   #时钟检测
            self.MemeryCheck()                  #内存检测
            self.WlanCheck()                    #WLAN模块检测
            if Remote_IP != None:
                self.EthSpeedCheck(Remote_IP)   #网口速率测试
            time.sleep(20)
            self.Clean_Caches()                 #清理内存
            Finish_time = datetime.datetime.now()
            if (Finish_time - self.endtime).days >= 0:
                self.Test_Pass(u"老化测试成功")
                break
            gc.collect()
        #os.system('netsh firewall set opmode mode=enable')  # 开启Windows防火墙
        #os.system("taskkill /f /t /im iperf.exe")  # 关闭iperf进程
        #os.system("taskkill /f /t /im cmd.exe")  # 关闭dos窗口

    #清理内存
    def Clean_Caches(self):
        self.Send_Command("echo 3 >> /proc/sys/vm/drop_caches&")
        time.sleep(3)
        self.Send_Command("free -m")
        self.Send_Command('cd /')

    #测试过程提升CPU利用率
    def Check_Process(self):
        if int(self.GetMiddleStr(self.Send_Command("ps | grep -c cpu.sh"), "cpu.sh", "~ #")) < 2:
            self.Send_Command("cd /")
            self.Send_Command("rm -rf cpu.sh")
            self.Send_Command("echo 'while true;do A=A;done' >> cpu.sh")
            self.Send_Command("chmod +x cpu.sh")
            self.Send_Command("sh cpu.sh &")

    #MAC地址检测
    def MAC_check(self):
        self.Test_Running(u"MAC地址检测")
        MAC = self.Send_Command("ifconfig | grep eth0")
        if "5C:E0:CA" not in MAC:
            self.Test_Fail(u"MAC地址格式错误")

    #时钟检测
    def Clock_Test(self):
        self.Test_Running(u"NTP检测")
        self.Send_Command("sntp -s %s "% self.Local_IP())
        time.sleep(10)
        date = self.Send_Command("date")            #获取设备时间
        time.sleep(3)
        clock = str(datetime.datetime.now().year)   #获取本地时间
        if clock not in date:
            self.Test_Fail(u"时钟错误")

    #网口速率测试
    def EthSpeedCheck(self,Remote_IP):
        self.Test_Running(u"网口速率检测")
        Ping_message = self.Send_Command("ping %s -c5" % Remote_IP)
        if "Host Unreachable" in Ping_message:
            self.Test_Fail(u"Iperf 服务器不通")
        else:
            Eth_Speed = self.Send_Command("iperf -c %s -w1m -i1 -t30 | grep '0.0-3'" % Remote_IP, "#", 60,10)
            if "Broken pipe" in Eth_Speed:
                self.Test_Fail(u"Iperf 服务器不通")

    #温度检测
    def ShowTemperature(self):
        self.Test_Running(u"温度检测")
        temp = self.Send_Command("echo $((`i2cget -y 1 0x4c 0` - 64))")
        time.sleep(3)
        temp = self.GetMiddleStr(str(temp), '))', "~ #")
        if int(temp) > 96:
            self.Test_Fail(u"温度超过96℃,当前温度：%s℃"%temp)

    #WLAN模块检测
    def WlanCheck(self):
        self.Test_Running(U"WIFI模块检测")
        wifi2 = self.Send_Command("lspci | grep -c '003c'","~ #",30)
        wifi2 = self.GetMiddleStr(str(wifi2), "3c'", "~ #").strip()
        time.sleep(1)
        wifi3 = self.Send_Command("lspci | grep -c '0033'","~ #",30)
        wifi3 = self.GetMiddleStr(str(wifi3), "33'", "~ #").strip()
        time.sleep(1)
        wifi4 = self.Send_Command("lspci | grep -c '002a'","~ #",30)
        wifi4 = self.GetMiddleStr(str(wifi4), "2a'", "~ #").strip()
        time.sleep(1)
        wifi1 = int(wifi2) + int(wifi3) + int(wifi4)
        if wifi1 != 4:
            self.Test_Fail(U"WIFI 模块未识别")

    #内存检测
    def MemeryCheck(self):
        self.Test_Running(u"内存检测")
        self.Send_Command("iostat -m")
        mem = self.Send_Command("free | grep Mem | awk '{print $2}'", "#", 30)
        mem = self.GetMiddleStr(str(mem), "}'", "~ #").strip()
        time.sleep(5)
        if float(mem) < 1024000:
            self.Test_Fail(u"内存 ＜1G")

    #版本检测
    def VersionCheck(self):
        self.Test_Running(u"版本检测")
        self.Send_Command("sed -n '1,3p' /sbin/PRODUCT_MESSAGE")
        s = self.Send_Command("vershow")
        time.sleep(3)
        if "failed" in s:
            self.Test_Fail(u"版本未完全升级")

