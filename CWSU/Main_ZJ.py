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

#ssh登录
class ssh():
    def __init__(self,host,username,passwd):
        self.s = paramiko.SSHClient()       #建立一个连接对象
        self.s.set_missing_host_key_policy(paramiko.AutoAddPolicy()) #允许将信任的主机自动加入到host_allow 列表，此方法必须放在connect方法的前面
        self.s.connect(hostname=host,port=22, username=username, password=passwd,timeout = 30)    #连接服务器
        self.ssh = self.s.invoke_shell()    #建立交互式shell连接
        time.sleep(2)

    # 发送数据
    def Send(self,Command):
        self.ssh.send(str(Command) + '\r')
        time.sleep(2)

    # 接收数据
    def Recv(self,Buff_Size,Time):
        buff = ""
        time.sleep(1)
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
            F.close()       #关闭文件

#主测试程序
class Main_Test(QtCore.QThread):
    def __init__(self,queue,parent = None):
        super(Main_Test,self).__init__(parent)
        self.data = queue               #数据
        self.isWait = True
        self.working = True             #工作
        self.Input_IP_address=None
        self.error_count=0              #错误次数为0
        self.Ship_Out_Address=None
        self.Red = "QPushButton{background-color:RED}"          #红色
        self.Yellow = "QPushButton{background-color:YELLOW}"    #黄色
        self.Green = "QPushButton{background-color:GREEN}"      #绿色
        self.Config_ini = Config_ini("ini/Paramiters.ini")      #获取配置文件信息

        self.CWSU_SWV = self.Config_ini.get_info("CWSU", "swv") #获取CWSU段swv信息
        self.CWSU_CFV = self.Config_ini.get_info("CWSU", "cfv")
        self.CWSU_SPN = self.Config_ini.get_info("CWSU", "spn")
        self.CWSU_MOD=self.Config_ini.get_info("CWSU", "mod")
        self.CWSU_BPN = self.Config_ini.get_info("CWSU", "bpn")
        self.CWSU_USER = self.Config_ini.get_info("CWSU", "user")
        self.CWSU_PASSWORD1 = self.Config_ini.get_info("CWSU", "password1")
        self.CWSU_PASSWORD2 = self.Config_ini.get_info("CWSU", "password2")
        self.CWSU_PASSWORD3 = self.Config_ini.get_info("CWSU", "password3")
        self.CWSU_PASSWORD4 = self.Config_ini.get_info("CWSU", "password4")
        self.AVSP_VEL = self.Config_ini.get_info("CWSU", "vel")
        self.AVSP_EVO = self.Config_ini.get_info("CWSU", "evo")
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
            self.Connect = ssh(str(host), username, passwd)  #ssh连接服务器
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
        except Exception:
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
        except Exception:
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

    #测试通过
    def Test_Pass(self,message):
        if message !="":
            self.emit(QtCore.SIGNAL('pass'),message)        #发送信号
            self.data.put(message)

    #测试开始
    def Test_Running(self,message):
        l = "##############################"+message+"##############################"
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
        Ping=os.system("ping -n 3 %s" % Host)
        if Ping == 0:
            self.Test_Running(u"################### Login ###################")           #测试开始信号
            self.Connection(Host)                               #连接测试设备
            os.system('netsh firewall set opmode disable')      #关闭windows系统防火墙
            os.system("start /b iperf.exe -s -w1m&")  #windows系统后台运行iperf，并指定选项
            time.sleep(5)
            while self.working == True:
                self.VersionCheck()                   #版本检测
                self.MAC_check()                      #MAC地址检测
                self.ShowTemperature()                #温度检测
                self.MemeryCheck()                    #内存检测
                self.Discrete()                       #离散量检测
                if Server_IP != "":
                    self.clock_test(Server_IP)        #时钟检测
                    self.EthSpeedCheck(Server_IP)     #网口速率检测
                self.Clean_Caches()                   #清理内存
                self.AVSP()                           #卫星板检测
                self.Serial()                         #序号检测
                os.system('netsh firewall set opmode mode=enable')  # 开启Windows防火墙
                os.system("taskkill /f /t /im iperf.exe")  # 关闭iperf进程
                os.system("taskkill /f /t /im cmd.exe")  # 关闭dos窗口
                self.Test_Finished(u"<font size = 10>LRU Test Completed PASS</font>")
            gc.collect()                              #垃圾回收
        else:
            self.Test_Fail(u"IP ping failed")
            self.Prompt(u"IP ping failed")

    #清理内存
    def Clean_Caches(self):
        self.Send_Command("echo 3 >> /proc/sys/vm/drop_caches&")
        time.sleep(3)
        self.Send_Command("free -m")
        self.Send_Command('cd /')

    #版本检测
    def VersionCheck(self):
        self.Test_Running(u"############### Version Check ###############")
        self.Send_Command("sed -n '1,12p' /sbin/PRODUCT_MESSAGE &", "Done", 30)
        swv = self.Send_Command('swv_read')
        swv = self.GetMiddleStr(swv, "version :", "~ #").strip()
        cfv = self.Send_Command('cfv_read')
        cfv = self.GetMiddleStr(cfv, "version :", "~ #").strip()
        spn = self.Send_Command('spn_read')
        spn = self.GetMiddleStr(spn, "part number:", "~ #").strip()
        mod = self.Send_Command('mod_read')
        mod = self.GetMiddleStr(mod, "Mod number:", "~ #").strip()
        bpn = self.Send_Command('board_pn_read')
        bpn = self.GetMiddleStr(bpn, "Board_Product_Number:", "~ #").strip()

        if swv == self.CWSU_SWV:
            self.Test_Pass(u"SWV：%s,PASS" % swv)
        else:
            self.Test_Fail(u"SWV: %s,FAIL" % swv)

        if cfv == self.CWSU_CFV:
            self.Test_Pass(u"CFV：%s,PASS" % cfv)
        else:
            self.Test_Fail(u"CFV: %s,FAIL" % cfv)

        if mod == self.CWSU_MOD:
            self.Test_Pass(u"MOD：%s,PASS" % mod)
        else:
            self.Test_Fail(u"MOD: %s,FAIL" % mod)

        if spn == self.CWSU_SPN:
            self.Test_Pass(u"SPN：%s,PASS" % spn)
        else:
            self.Test_Fail(u"SPN: %s,FAIL" % spn)

        if self.CWSU_BPN in bpn:
            self.Test_Pass(u"BPN：%s,PASS" % bpn)
        else:
            self.Test_Fail(u"BPN：%s,FAIL" % bpn)

        s = self.Send_Command("vershow &", "Done", 60)
        if "failed" in s:
            self.Test_Fail(u"Version Upgrade FAIL")

    #MAC地址检测
    def MAC_check(self):
        self.Test_Running(u"################ MAC Check ################")
        MAC = self.Send_Command("ifconfig | grep eth0")
        if "5C:E0:CA" in MAC:
            self.Test_Pass(u"MAC PASS")
        else:
            self.Test_Fail(u"MAC FAIL")

    #时钟检测
    def clock_test(self, Server_IP):
        self.Test_Running(U"############### NTP Check ###############")
        os.system(
            'reg add HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\W32Time\TimeProviders\NtpServer /v Enabled /t REG_DWORD /d 1 /f')  # 修改注册表
        os.system(
            'reg add HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\W32Time\Config /v AnnounceFlags /t REG_DWORD /d 5 /f')  # 修改注册表
        os.system("net stop w32time & net start w32time")  #停止和启动windows系统NTP服务
        self.Send_Command("sntp -s %s &" % Server_IP, "Done", 15)
        time.sleep(5)
        date = self.Send_Command("date")            #获取设备时间
        clock = str(datetime.datetime.now().year)   #获取本地时间
        if clock in date:
            self.Test_Pass(u'NTP PASS')
        else:
            self.Test_Fail(u"NTP FAIL")

    #网口速率
    def EthSpeedCheck(self, Server_IP):
        self.Test_Running(u"## Ethernet Front-end Ports Rate Check ##")
        Ping_message = self.Send_Command("ping %s -c3" % Server_IP)
        if "Host Unreachable" in Ping_message:
            self.Test_Fail(u"Ping Server Fail")
        else:
            time.sleep(3)
            for count in range (1,4):
                time.sleep(1)
                Eth_Speed = self.Send_Command("iperf -c "+Server_IP+" -w1m -i1 -t30 | grep '0.0-3' &","Done",60)
                if "Broken pipe" not in Eth_Speed:
                    result= self.GetMiddleStr(str(Eth_Speed),'Bytes',"Mbits")
                    if float(result) >100:      #以太网接口速率大于100兆
                        if count < 3 :
                            info = u'Ethernet port'+ str(count)  + u'rate：' + str(result) + u'Mbits/sec,replace' + str(count+1)
                        else :
                            info = u'Ethernet port 3 rate' + str(result) + u'Mbits/sec,PASS'
                        self.Test_Pass(info)
                        self.Prompt(info)
                    else:
                        info = u'Ethernet port rate %s Mbits/sec, FAIL'% str(result)
                        self.Test_Fail(info)
                else:
                    self.Test_Fail(u'Iperf address access failed')

    #温度检测
    def ShowTemperature(self):
        self.Test_Running(u"############ Temperature Check ############")
        temp = self.Send_Command("tmp_get")
        temp = self.GetMiddleStr(str(temp), 'tmp_get', "~ # ")
        if int(temp) > 96:
            self.Test_Fail(u"Temperature:%s℃,More than 96℃,FAIL" % temp)
        else:
            self.Test_Pass(u"Temperature:%s℃,PASS" % temp)

    #内存检测
    def MemeryCheck(self):
        self.Test_Running(u"############## Memory Check ##############")
        self.Send_Command("iostat -m")
        mem = self.Send_Command("free | grep Mem | awk '{print $2}'", "#", 30)
        mem = self.GetMiddleStr(str(mem), "}'", "~ #").strip()
        if float(mem) < 512000:
            self.Test_Fail(u"Memory ＜ 512MB,FAIL")
        else:
            self.Test_Pass(u"Memory:%s,PASS" % mem)


    #离散量检测
    def Discrete(self):
        self.Test_Running(u"############# Discrete Check #############")
        for i in range(1, 5):
            self.Send_Command("hi8425_cfg wrDiscOut %s low"%str(i))
        log1 = self.Send_Command("hi8425_cfg rdDiscIn", '#', 5)
        if '0x7f' in log1:
            self.Test_Pass(u"Discrete setting low PASS")
        else:
            self.Test_Fail(u"Discrete setting low FAIL")
        for i in range(1, 5):
            self.Send_Command("hi8425_cfg wrDiscOut %s high"%str(i))
        log2 = self.Send_Command("hi8425_cfg rdDiscIn", '#', 5)
        if "0x0" in log2:
            self.Test_Pass(u"Discrete setting high PASS")
        else:
            self.Test_Fail(u"Discrete setting high FAIL")
        for i in range(1, 5):
            self.Send_Command("hi8425_cfg wrDiscOut %s low"%str(i))
        log3 = self.Send_Command("hi8425_cfg rdDiscIn", '#', 5)
        if '0x7f' in log3:
            self.Test_Pass(u"Discrete setting low PASS")
        else:
            self.Test_Fail(u"Discrete setting low FAIL")

        self.Test_Running(u"############### 429 Check ###############")
        self.Send_Command("hi3593_c0_cfg setRx2BitRate high", '#', 5)
        log = self.Send_Command("hi429_sendmsg_user_chip", '#', 5)
        if "OK" in log:
            self.Test_Pass(u"429 PASS")
        else:
            self.Test_Fail(u"429 FAIL")

    #卫星板检测
    def AVSP(self):
        self.Test_Running(u"############### AVSP Check ###############")
        sp = self.Send_Command("curl -u %s:%s -S -k -X GET https://192.168.1.1/api/1.0/terminal/config/identity" % (self.CWSU_USER,self.CWSU_PASSWORD1))  # 获取卫星板信息
        if 'Failed' not in sp:
            if "tpk" in sp or "model" in sp or "mac" in sp:
                model = self.GetMiddleStr(sp, '"model":"', '","sub_functional_id"')
                tpk = self.GetMiddleStr(sp, '"tpk":"', '","system_type"')
                mac = self.GetMiddleStr(sp, '"mac":"', '","version"')
                self.Test_Pass(u"\r\n AVSP Model：%s\r\n" % model)
                self.Test_Pass(u"\r\n AVSP TPK：%s\r\n" % tpk)
                self.Test_Pass(u"\r\n AVSP MAC：%s\r\n" % mac)
            else:
                self.Test_Fail(u"AVSP FAIL")
        Sate_IP='192.168.1.1'
        self.Connect = ssh(Sate_IP, 'root',self.CWSU_PASSWORD2)
        self.Send_Command("telnet 0", "name:", 60, 20)
        self.Send_Command("admin", "word:")
        self.Send_Command(self.CWSU_PASSWORD3, ">")
        par = self.Send_Command("partitions_info",">",30,10)
        if self.AVSP_VEL in par:
            self.Test_Pass("VEL:%s" % self.AVSP_VEL)
        else:
            self.Test_Fail("VEL_version FAIL")

        if self.AVSP_EVO in par:
            self.Test_Pass("VEL:%s" % self.AVSP_EVO)
        else:
            self.Test_Fail("VEL_version FAIL")
        self.Send_Command("exit")

        self.Send_Command("service idirect_falcon stop","#",90,10)
        self.Send_Command("flashdbmgr --set wd stop","#",30,5)
        self.Send_Command("startavsp.sh","name:",600,20)
        time.sleep(20)
        self.Send_Command("admin", "word:")
        self.Send_Command("iDirect", ">")
        self.Send_Command("board info",">",30,10)

        self.Test_Running(u"######### CX780 temperature Check #########")
        tem=self.Send_Command("temperature",">",10)
        if 'LM73' not in tem and 'FPGA' not in tem:
            self.Test_Fail(u"CX780 temperature FAIL")

        self.Test_Running(u"############# CX780 LED Check #############")
        self.Prompt(u"Check if the LED is blinking")
        list = ["rx1","tx","net"]
        for green in list:
            for i in range (1,5):
                self.Send_Command("led %s grn off" % green, ">", 10, 1)
                self.Send_Command("led %s grn on" % green, ">", 10, 1)
            if not self.Prompt(u"%s Whether the LED is blinking" % green):
                self.Test_Pass(u"%s LED Flashing PASS" % green)
            else:
                self.Test_Fail(u"%s LED Flashing FAIL" % green)

        self.Test_Running(u"############# CX780 Ber Check #############")
        self.Send_Command("stresstest on", '>', 600, 60)
        self.Send_Command("tx cw on", '>', 60,10)
        self.Send_Command("tx freq 950", '>', 60,10)
        self.Send_Command("tx power 0", '>', 60,10)
        RX=self.Send_Command("rx power", '>', 60,20)
        RX1 = self.GetMiddleStr(str(RX),'RX Power: ','[console]').strip()
        if float(RX1)<=-25  or float(RX1)>=-10:
            self.Test_Fail(u'CX780 BER RX Power：%s,FAIL'%RX1)

        self.Send_Command("tx power -20", '>', 60,10)
        RX=self.Send_Command("rx power", '>', 60,20)
        RX1 = self.GetMiddleStr(str(RX),'RX Power: ','[console]').strip()
        if float(RX1)<=-45  or float(RX1)>=-30:
            self.Test_Fail(u'CX780 BER RX Power: %s,FAIL'%RX1)

        self.Send_Command("tx power -40", '>', 60, 10)
        RX = self.Send_Command("rx power", '>', 60, 20)
        RX1 = self.GetMiddleStr(str(RX), 'RX Power: ', '[console]').strip()
        if float(RX1) <= -65 or float(RX1) >= -55:
            self.Test_Fail(u'CX780 BER RX Power: %s,FAIL' % RX1)

        self.Send_Command("tx cw off", ">", 20,10)
        result = self.Send_Command("stresstest result",">",600,30)
        if "Total Fails		: 0" in result:
            if "Cumulative Errors 0" in result:
                self.Test_Pass(u"Ber:0,PASS")
            else:
                self.Test_Fail(u"Ber FAIL")
        else:
            self.Test_Fail(u"AVSP Stress Test FAIL")
        self.Send_Command("stresstest off", '> ', 1800, 60)

        self.Test_Running(u"############# CX780 NET Check #############")
        self.Send_Command("exit", "#")
        if int(self.GetMiddleStr(self.Send_Command("ps | grep -c iperf"),"iperf","#")) < 2:
            self.Send_Command("iperf -s &\r")
        self.Connection(self.Host)
        Eth_Speed = self.Send_Command("iperf3 -c %s -w1m -i1 -t30 | grep '0.00-3'&" % Sate_IP, "Done", 40)
        if "Broken pipe" not in Eth_Speed:
            result = self.GetMiddleStr(str(Eth_Speed), 'Bytes', "Mbits")
            if float(result) > 100:  # 卫星板接口速率大于100兆
                info = u'CX780 Ethernet Port Rate:%s Mbits/sec, PASS' % str(result)
                self.Test_Pass(info)
            else:
                info = u'CX780 Ethernet Port Rate:%s Mbits/sec, FAIL' % str(result)
                self.Test_Fail(info)
        else:
            self.Test_Fail(u'CX780 Iperf address access failed')

    #序号检测
    def Serial(self):
        self.Test_Running(u"############# Serial Check #############")
        self.Send_Command("export TERMINFO=/usr/share/terminfo")
        self.Send_Command("cd /root")
        self.Send_Command("./minicom","keys",20)
        self.Send_Command("\r","iDirectCM",20)
        time.sleep(5)
        self.Send_Command("root", 'Password:',30)
        time.sleep(5)
        self.Send_Command(self.CWSU_PASSWORD4, '#', 10)
