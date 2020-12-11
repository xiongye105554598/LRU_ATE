# -*- coding: utf-8 -*-
from PyQt4 import QtCore
import os,time,datetime,codecs
import telnetlib        #telnet连接模块
import paramiko         #ssh连接模块
import ConfigParser     #配置文件模块
import sys,socket
import thread           #处理和控制线程
import gc               #垃圾回收
reload(sys)             #重新加载sys模块
sys.setdefaultencoding('utf8')      #设置utf8为默认编码

#Telnet登录
class Telnet():
    def __init__(self,host):
        self.telnet = telnetlib.Telnet(host, port = 10020, timeout=10)      #连接telnet服务器
        self.telnet.set_debuglevel(2)

    #读取用户名及密码
    def Read(self,Prompt,Timeout):
        buff = ""
        try:
            buff += self.telnet.read_until(Prompt,Timeout)      #读取指定的用户名或密码,Timeout超时
        except:
            self.Send("\n")
            buff += self.telnet.read_until(Prompt,Timeout)
        return buff

    #发送命令
    def Send(self,Command):
        self.telnet.write(str(Command)+'\n')        #向远端发送命令

    #关闭连接
    def Close(self):
        self.telnet.close()         #终止telnet连接

#ssh登录
class ssh():
    def __init__(self,host,username,passwd):
        self.s = paramiko.SSHClient()       #建立一个连接对象
        self.s.set_missing_host_key_policy(paramiko.AutoAddPolicy()) #允许将信任的主机自动加入到host_allow 列表，此方法必须放在connect方法的前面
        self.s.connect(hostname=host,port=22, username=username, password=passwd,timeout = 30)    #连接服务器
        self.ssh = self.s.invoke_shell()    #建立交互式shell连接
        time.sleep(2)

    #发送数据
    def Send(self,Command):
        self.ssh.send(str(Command) + '\r')

    #接收数据
    def Recv(self,Buff_Size,Time):
        buff = ""
        try:
            buff += self.ssh.recv(Buff_Size,Time)       #获取回显
        except:
            self.Send("\n")
            buff += self.ssh.recv(Buff_Size,Time)
        return buff

    #关闭连接
    def Close(self):
        self.s.close()

#获取配置文件信息
class Config_ini():
    def __init__(self,filename):
        self.config = ConfigParser.ConfigParser()       #创建配置文件对象
        self.config.readfp(open(filename))      #打开并读取配置文件
    def get_info(self,session,key):
        return self.config.get(session,key)     #读取配置文件中指定段的键值
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
        self.working = True

    def write_log(self,PD,SN,Time):
        if not os.path.exists(os.getcwd() + "\\log"):       #exists()函数判断路径,getcwd()函数返回当前路径
            os.makedirs(os.getcwd() + "\\log")      #递归创建目录
        Path = os.getcwd() + "\\log\\"      #文件路径
        self.data_file = Path + PD + "_whole_" + SN + "_" + Time + ".log"     #在Path路径下创建log文件
        while self.working:         #循环
            s = self.data.get()     #获取测试数据
            F = codecs.open(self.data_file, "a+", encoding='gb18030')       #以指定的编码读取模式打开文件
            F.write(s + "\r\n")     #写入文件
            F.close()               #关闭文件

#主测试程序
class Main_Test(QtCore.QThread):
    def __init__(self,queue,parent = None):
        super(Main_Test,self).__init__(parent)
        self.data = queue               #数据
        self.isWait = True              #等待
        self.working = True             #工作
        self.Input_IP_address=None
        self.error_count=0              #错误次数为0
        self.Ship_Out_Address=None
        self.Red = "QPushButton{background-color:RED}"          #红色
        self.Yellow = "QPushButton{background-color:YELLOW}"    #黄色
        self.Green = "QPushButton{background-color:GREEN}"      #绿色
        self.Config_ini = Config_ini("ini/Paramiters.ini")      #获取配置文件信息

        self.CWAP_SWV = self.Config_ini.get_info("CWAP", "swv") #获取CWAP段swv信息
        self.CWAP_SPN = self.Config_ini.get_info("CWAP", "spn")
        self.CWAP_DPN = self.Config_ini.get_info("CWAP", "dpn")
        self.CWAP_BPN = self.Config_ini.get_info("CWAP", "bpn")
        self.CWAP_BOOT = self.Config_ini.get_info("CWAP", "boot")
        self.CWAP_MOD=self.Config_ini.get_info("CWAP", "mod")

        self.MAC = ""
        self.Boot = ""
        self.Kernel = ""
        self.APP = ""
        self.Config = ""

    #获取IP地址
    def Local_IP(self):
        self.Local_IP = socket.gethostbyname(socket.gethostname())      #获取本地主机名的IP地址
        return str(self.Local_IP)

    #连接设备
    def Connection(self, host):
        username = "admin"
        passwd = "Feitianlianhe"
        try:
            self.Connect = ssh(str(host), username, passwd)     #ssh连接服务器
            self.Login_Shell()
        except Exception, e:
            self.Test_Fail(str(e))

    #发送接收数据
    def Send_Command(self, Command, Prompt='#', Timeout=10,wait_time=1):
        try:
            buff = ""
            log = ""
            self.Connect.Send(Command)              #发送命令
            starttime = datetime.datetime.now()     #获取当前时间
            while Prompt not in buff:
                buff = ""
                time.sleep(1)
                buff += self.Connect.Recv(99999,wait_time)
                log += buff
                self.data.put(buff)
                self.emit(QtCore.SIGNAL('output(QString)'), buff)
                endtime = datetime.datetime.now()
                if (endtime - starttime).seconds > Timeout:
                    self.Test_Fail(u"超时, %s 不能找到" % Prompt)
                    break
            return log
        except Exception, E:
            self.Test_Fail(u"命令错误，%s 不能找到" % Prompt)

    #登录方法
    def Login_Shell(self):
        self.Send_Command("man", "(Enter)")
        self.Send_Command("", ":")
        self.Send_Command("12345678", "#")
        self.Send_Command("rootprivilege", "(privilege)#")
        self.Send_Command("_admin_shell_", ":")
        self.Send_Command("_fdaCVIbew$%^&*vcmzCnv+m_")

    #通过开头和结尾字符串获取中心字符串
    def GetMiddleStr(self, content, startStr, endStr):
        try:
            startIndex = content.index(startStr)        #检测content字符串中是否包含startstr字符串,返回开始的索引
            if startIndex >= 0:
                startIndex += len(startStr)
            endIndex = content.index(endStr)            #检测content字符串中是否包含endstr字符串,返回开始的索引
            return content[startIndex:endIndex].strip() #移除字符串收尾的空格，并返回字符串指定的字符
        except Exception, e:
            self.Test_Fail(u"内容返回错误")

    #设置颜色
    def Set_Color(self, message):
        self.emit(QtCore.SIGNAL('color'), message)

    #设置地址
    def Set_Status(self, message):
        self.emit(QtCore.SIGNAL('status'), message)

    #错误消息
    def error(self,message):
        if message !="":
            self.emit(QtCore.SIGNAL('error'),message)
            self.data.put(message)

    #测试通过提示
    def Test_Pass(self,message):
        if message !="":
            self.emit(QtCore.SIGNAL('pass'),message)        #发送信号
            self.data.put(message)

    #测试开始
    def Test_Running(self,message):
        l = "########################################" + message + "########################################"
        self.emit(QtCore.SIGNAL('dis_message'), l)          #发送信号
        self.data.put(l)        #入队

    #测试失败
    def Test_Fail(self,message):
        self.working = False
        self.error_count = 1        #错误计数
        self.Set_Color(self.Red)
        self.data.put(message)      #测试失败信息入队
        self.error(message)         #发送错误信息
        self.emit(QtCore.SIGNAL('error'), "<font color=red><font size = 10>%s</font>" % u"Test FAIL\n")
        self.emit(QtCore.SIGNAL('stop'), self.working)
        thread.exit_thread()        #终止线程

    #输入IP地址
    def Input_IP(self,message):
        self.emit(QtCore.SIGNAL('input'),message)
        while self.isWait:
            time.sleep(1)
        self.isWait = True
        return self.Input_IP_address

    #输入地址
    def Ship_Out_Address_setting(self,message):
        self.emit(QtCore.SIGNAL('ship'),message)
        while self.isWait:
            time.sleep(1)
        self.isWait = True
        return self.Ship_Out_Address

    #提示消息
    def Prompt(self,message):
        self.emit(QtCore.SIGNAL('Prompt'),message)
        while self.isWait:
            time.sleep(1)
        self.isWait=True

    #测试完成
    def Test_Finished(self,message):
        self.working = False
        if self.error_count == 0:
            self.Test_Pass(message)
            self.emit(QtCore.SIGNAL('stop'),self.working)
        thread.exit_thread()

    #程序运行
    def Script_Start(self,PD,SN,Time,Host,Server_IP = None):
        self.working = True
        self.PD = PD
        self.SN = SN
        self.Host = Host
        self.Time = Time
        self.error_count = 0        #错误计数
        Ping=os.system("ping -n 5 %s"%Host)
        if Ping == 0:
            self.Test_Running(u"##### Login #####")         #测试开始信号
            self.Connection(Host)                             #连接测试设备
            os.system('netsh firewall set opmode disable')    #后台关闭windows系统防火墙
            os.system("start /b iperf.exe -s -w1m&")          #windows系统后台运行iperf，并指定选项
            time.sleep(5)
            while self.working == True:
                self.VersionCheck()                           #版本检测
                self.MAC_check()                              #MAC地址检测
                self.ShowTemperature()                        #温度检测
                self.MemeryCheck()                            #内存检测
                if Server_IP != "":
                    self.clock_test(Server_IP)                #时钟检测
                #self.WlanCheck()                              #WIFI检测
                if Server_IP != "":
                    self.EthSpeedCheck(Server_IP)             #网口速率检测
                self.Clean_Caches()                           #清理缓存
                os.system('netsh firewall set opmode mode=enable')  # 开启Windows防火墙
                os.system("taskkill /f /t /im iperf.exe")  # 关闭iperf进程
                os.system("taskkill /f /t /im cmd.exe")  # 关闭dos窗口
                self.Test_Finished(u"<font size = 10>LRU Test Completed PASS</font>")
            gc.collect()                              #垃圾回收
        else:
            self.Test_Fail(u"IP ping failed")
            self.Prompt(u"IP ping failed")

    #清理缓存
    def Clean_Caches(self):
        self.Send_Command("echo 3 >> /proc/sys/vm/drop_caches&")
        time.sleep(3)
        self.Send_Command("free -m")

    #版本检测
    def VersionCheck(self):
        self.Test_Running(u"##### Version Check #####")
        self.Send_Command("sed -n '1,12p' /sbin/PRODUCT_MESSAGE &", "Done", 30)
        swv = self.Send_Command('swv_read')
        swv = self.GetMiddleStr(swv, "version:", "~ #").strip()
        spn = self.Send_Command('spn_read')
        spn = self.GetMiddleStr(spn, "part number:", "~ #").strip()
        dpn = self.Send_Command('dpn_read')
        dpn = self.GetMiddleStr(dpn, "part number:", "~ #").strip()

        bpn = self.Send_Command('board_pn_read')
        bpn = self.GetMiddleStr(bpn, "Board_Product_Number:", "~ #").strip()

        dsn = self.Send_Command('dsn_read')
        bsn = self.Send_Command('board_sn_read')
        boot = self.Send_Command('boot_read')
        boot = self.GetMiddleStr(boot, "BOOT_VERSION:", "~ #").strip()
        mod = self.Send_Command('mod_read')
        mod = self.GetMiddleStr(mod, "Mod number:", "~ #").strip()
        if swv == self.CWAP_SWV:
            self.Test_Pass(u"SWV：%s,PASS" % swv)
        else:
            self.Test_Fail(u"SWV：%s,FAIL" % swv)
        if mod == self.CWAP_MOD:
            self.Test_Pass(u"MOD：%s,PASS" % mod)
        else:
            self.Test_Fail(u"MOD: %s,FAIL" % mod)
        if spn == self.CWAP_SPN:
            self.Test_Pass(u"SPN：%s,PASS" % spn)
        else:
            self.Test_Fail(u"SPN: %s,FAIL" % spn)
        if dpn == self.CWAP_DPN:
            self.Test_Pass(u"DPN：%s,PASS" % dpn)
        else:
            self.Test_Fail(u"DPN：%s,FAIL" % dpn)
        if bpn == self.CWAP_BPN:
            self.Test_Pass(u"BPN：%s,PASS" % bpn)
        else:
            self.Test_Fail(u"BPN：%s,FAIL" % bpn)
        if boot == self.CWAP_BOOT:
            self.Test_Pass(u"BOOT：%s,PASS" % boot)
        else:
            self.Test_Fail(u"BOOT：%s,FAIL" % boot)
        s = self.Send_Command("vershow&", "Done", 60)
        if "failed" in s:
            self.Test_Fail(u"Version Upgrade FAIL")

    #MAC地址检测
    def MAC_check(self):
        self.Test_Running(u"### MAC Check ###")
        MAC = self.Send_Command("ifconfig | grep eth0")
        if "5C:E0:CA" in MAC:
            self.Test_Pass(u"MAC PASS")
        else:
            self.Test_Fail(u"MAC FAIL")

    #温度检测
    def ShowTemperature(self):
        self.Test_Running(u"##### Temperature Check #####")
        temp = self.Send_Command("echo $((`i2cget -y 1 0x4c 0` - 64))&", "Done", 5)
        temp = self.GetMiddleStr(str(temp), '~ # ', "[")
        if int(temp) > 96:
            self.Test_Fail(u"Temperature:%s℃,More than 96℃,FAIL" % temp)
        else:
            self.Test_Pass(u"Temperature:%s℃,PASS" % temp)

    #内存检测
    def MemeryCheck(self):
        self.Test_Running(u"##### Memory Check #####")
        self.Send_Command("iostat -m")
        mem = self.Send_Command("free | grep Mem | awk '{print $2}'", "#", 30)
        mem = self.GetMiddleStr(str(mem), "}'", "~ #").strip()
        if float(mem) < 1024000:
            self.Test_Fail(u"Memory ＜ 1G,FAIL")
        else:
            self.Test_Pass(u"Memory:%s,PASS" % mem)

    #时钟检测
    def clock_test(self, Server_IP):
        self.Test_Running(U"##### NTP Check #####")
        os.system(
            'reg add HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\W32Time\TimeProviders\NtpServer /v Enabled /t REG_DWORD /d 1 /f')  # 修改注册表
        os.system(
            'reg add HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\W32Time\Config /v AnnounceFlags /t REG_DWORD /d 5 /f')  # 修改注册表
        os.system("net stop w32time & net start w32time")  # 后台停止和启动windows系统NTP服务
        self.Send_Command("sntp -s %s &" % Server_IP, "Done", 15)
        time.sleep(5)
        date = self.Send_Command("date")            #获取设备时间
        clock = str(datetime.datetime.now().year)   #获取本地时间
        if clock in date:
            self.Test_Pass(u'NTP PASS')
        else:
            self.Test_Fail(u"NTP FAIL")

    #WIFI模块检测
    def WlanCheck(self):
        self.Test_Running(U"## WIFI Module Check ##")
        i = 1
        wifi2 = self.Send_Command("lspci | grep -c '003c'", "~ #", 30)
        wifi2 = self.GetMiddleStr(str(wifi2), "3c'", "~ #").strip()
        time.sleep(1)
        wifi3 = self.Send_Command("lspci | grep -c '0033'", "~ #", 30)
        wifi3 = self.GetMiddleStr(str(wifi3), "33'", "~ #").strip()
        time.sleep(1)
        wifi4 = self.Send_Command("lspci | grep -c '002a'", "~ #", 30)
        wifi4 = self.GetMiddleStr(str(wifi4), "2a'", "~ #").strip()
        time.sleep(1)
        wifi1 = int(wifi2) + int(wifi4) + int(wifi3)
        WIFI_IP = self.Input_IP(u"Please connect PED to WIFI" + str(i) + u'Enter the address obtained by PED')
        WIFI_Ping_message = self.Send_Command("ping " + WIFI_IP + " -c5", "#", 7)
        if "100% packet loss" in WIFI_Ping_message:
            self.Test_Fail("PED address access failed")
        else:
            if wifi1 != 4:
                self.Test_Fail("WIFI Module≠4,FAIL")
            else:
                for i in range(1, 5):
                    time.sleep(3)
                    WIFI_Speed = self.Send_Command("iperf -c " + WIFI_IP + " -i1 -t40 | grep '0.0-4'&", "Done", 60)
                    if "Broken pipe" not in WIFI_Speed:
                        result = self.GetMiddleStr(str(WIFI_Speed), 'Bytes', "Mbits")
                        if float(result) > 30:  # 无线接口速率大于30兆
                            if i < 4:
                                info = 'WIFI' + str(i) + u' rate:' + str(
                                    result) + u'Mbits/sec,PASS,Please connect to WIFI' + str(i + 1)
                            else:
                                info = 'WIFI4' + u' rate:' + str(result) + u'Mbits/sec,PASS'
                            self.Test_Pass(info)
                            self.Prompt(info)
                        else:
                            info = u'WIFI Rate Test FAIL:' + str(result) + u'Mbits/sec.'
                            self.Test_Fail(info)
                    else:
                        self.Test_Fail(u'Iperf address access failed')

    #网口速率
    def EthSpeedCheck(self, Server_IP):
        self.Test_Running(u"## Ethernet Front-end Ports Rate Check ##")
        Ping_message = self.Send_Command("ping %s -c5" % Server_IP)
        if "Host Unreachable" in Ping_message:
            self.Test_Fail(u"Ping Server Fail")
        else:
            time.sleep(5)
            R1 = self.Send_Command("iperf -c "+Server_IP+" -w1m -i1 -t30 | grep '0.0-3'&","Done",40)
            if "Broken pipe" not in R1:
                result= self.GetMiddleStr(str(R1),'Bytes',"Mbits")
                if float(result) > 100:# 网口速率大于100兆
                    self.Test_Pass(u'ETH0 PASS, Ethernet port rate：' + str(result) + 'Mbits/sec')
                    self.Prompt(u'ETH0 Ethernet port rate：' + str(result) +u'Mbits/sec,PASS,Please connect to ETH1')
                    time.sleep(5)
                    R2=self.Send_Command("iperf -c "+ Server_IP+" -w1m -i1 -t30 | grep '0.0-3'&","Done",40)
                    result= self.GetMiddleStr(R2,'Bytes',"Mbits")
                    if float(result) > 100:
                        self.Test_Pass(u'ETH1 PASS,Ethernet port rate：' + str(result) +'Mbits/sec')
                    else:
                        self.Test_Fail(u'ETH1 ＜100Mbs FAIL')
                else:
                    self.Test_Fail(u'ETH0 ＜100Mbs FAIL')
            else:
                self.Test_Fail(u'Iperf address access failed')











