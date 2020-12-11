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
            F.close()       #关闭文件

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
        self.GNS_SWV = self.Config_ini.get_info("GNS", "swv")   #获取GNS段swv信息
        self.GNS_SPN = self.Config_ini.get_info("GNS", "spn")
        self.GNS_DPN = self.Config_ini.get_info("GNS", "dpn")
        self.GNS_BPN = self.Config_ini.get_info("GNS", "bpn")
        self.GNS_FPGAPN = self.Config_ini.get_info("GNS", "fpgapn")
        self.GNS_ISOPN = self.Config_ini.get_info("GNS", "isopn")
        self.GNS_MOD=self.Config_ini.get_info("GNS", "mod")
        self.GNS_FPGA=self.Config_ini.get_info("GNS","fpga_version")
        self.GNS_Docker = self.Config_ini.get_info("GNS", "docker")
        self.GNS_Nginx = self.Config_ini.get_info("GNS", "nginx")
        self.GNS_Nodejs = self.Config_ini.get_info("GNS", "nodejs")
        self.GNS_Mongodb = self.Config_ini.get_info("GNS", "mongodb")
        self.GNS_Underlying = self.Config_ini.get_info("GNS", "underlying")

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
        username = "gns"
        passwd = "feitian"
        try:
            self.Connect = ssh(str(host), username, passwd)     #ssh连接服务器
            self.Send_Command("\n")
        except Exception, e:
            self.Test_Fail(str(e))

    #发送接收数据
    def Send_Command(self, Command, Prompt='#', Timeout=10,wait_time=1):
        try:
            buff = ""
            log = ""
            self.Connect.Send(Command)              #发送命令
            starttime = datetime.datetime.now()     #获取当前时间
            # while not buff.endswith(Prompt):
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
        thread.exit_thread()  # 终止线程

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
        thread.exit_thread()  # 终止线程

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
            self.Test_Running(u"##### Login #####")           #测试开始信号
            self.Connection(Host)                             #连接测试设备
            os.system('netsh firewall set opmode disable')    #后台关闭windows系统防火墙
            os.system("start /b iperf.exe -s -w1m&")          #windows系统后台运行iperf，并指定选项
            time.sleep(5)
            self.Install_Tools()                              #GNS工具安装
            while self.working == True:
                self.VersionCheck()                           #版本检测
                self.MAC_check()                              #MAC地址检测
                self.ShowTemperature()                        #温度检测
                self.MemeryCheck()                            #内存检测
                if Server_IP != "":
                    self.clock_test(Server_IP)                #时钟检测
                self.Discrete()                               #离散量检测
                if Server_IP != "":
                    self.EthSpeedCheck(Server_IP)             #网口速率检测
                self.USBCheck()                               #USB检测
                self.SSDCheck()                               #硬盘检测
                self.Clean_Caches()                           #清理缓存
                os.system('netsh firewall set opmode mode=enable')  #开启Windows防火墙
                os.system("taskkill /f /t /im iperf.exe")     #关闭iperf进程
                os.system("taskkill /f /t /im cmd.exe")       #关闭dos窗口
                self.Test_Finished(u"<font size = 10>LRU Test Completed PASS</font>")
            gc.collect()                                      #垃圾回收
        else:
            self.Test_Fail(u"IP ping failed")
            self.Prompt(u"IP ping failed")

    #GNS工具安装
    def Install_Tools(self):
        self.Send_Command("cd /root/software/gns_test/")
        self.Send_Command("chmod +x *")
        self.Send_Command("./install_sysstat.sh","#",60)
        time.sleep(3)
        self.Send_Command("\cp -f kcpu /sbin")
        self.Send_Command("\cp -f iozone /sbin")
        self.Send_Command("\cp -f nmon /sbin")
        self.Send_Command("\cp -f iperf /sbin")
        self.Send_Command("\cp -f cpulimit /sbin")
        self.Send_Command("\cp -f run_kcpu.sh /sbin")
        self.Send_Command("cd 429")
        self.Send_Command("\cp -f * /sbin")
        self.Send_Command('cd /')

    #清理缓存
    def Clean_Caches(self):
        self.Send_Command("echo 3 >> /proc/sys/vm/drop_caches&")
        time.sleep(3)
        self.Send_Command("free -m")
        self.Send_Command('cd /')

    #MAC地址检测
    def MAC_check(self):
        self.Test_Running(u"### MAC Check ###")
        MAC = self.Send_Command("ifconfig | grep eth0")
        if "5C:E0:CA" in MAC:
            self.Test_Pass(u"MAC PASS")
        else:
            self.Test_Fail(u"MAC FAIL")

    #时钟检测
    def clock_test(self, Server_IP):
        self.Test_Running(U"##### NTP Check #####")
        os.system(
            'reg add HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\W32Time\TimeProviders\NtpServer /v Enabled /t REG_DWORD /d 1 /f')  # 修改注册表
        os.system(
            'reg add HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\W32Time\Config /v AnnounceFlags /t REG_DWORD /d 5 /f')  # 修改注册表
        os.system("net stop w32time & net start w32time")  # 后台停止和启动windows系统NTP服务
        self.Send_Command("service ntpd stop")
        self.Send_Command("ntpdate %s &" % Server_IP, "Done", 15)
        time.sleep(5)
        date = self.Send_Command("date")            #获取设备时间
        clock = str(datetime.datetime.now().year)   #获取本地时间
        if clock in date:
            self.Test_Pass(u'NTP PASS')
        else:
            self.Test_Fail(u"NTP FAIL")

    #网口速率
    def EthSpeedCheck(self, Server_IP):
        self.Test_Running(u" Ethernet Front-end Ports Rate Check ")
        Ping_message = self.Send_Command("ping %s -c5" % Server_IP)
        if "Host Unreachable" in Ping_message:
            self.Test_Fail(u"Ping Server Fail")
        else:
            time.sleep(5)
            for count in range (1,6):
                time.sleep(3)
                Eth_Speed = self.Send_Command("iperf -c "+Server_IP+" -w1m -i1 -t30 | grep '0.0-3'&","Done",40)
                if "Broken pipe" not in Eth_Speed:
                    result= self.GetMiddleStr(str(Eth_Speed),'Bytes',"Mbits")
                    if float(result) >500:      #以太网接口速率大于500兆
                        if count < 5 :
                            info = u'Ethernet port '+ str(count) + u' rate：' + str(result) + u'Mbits/sec PASS,please connect to ETH' + str(count+1)
                        else :
                            info = u'Ethernet port 5 rate：%sMbits/sec PASS'% str(result)
                        self.Test_Pass(info)
                        self.Prompt(info)
                    else:
                        info = u'Ethernet port rate ' + str(result) +u'Mbits/sec,FAIL.'
                        self.Test_Fail(info)
                else:
                    self.Test_Fail(u'Iperf address access failed')

    #温度检测
    def ShowTemperature(self):
        self.Test_Running(u"##### Temperature Check #####")
        temp = self.Send_Command("sensors -u&", "Done", 10)
        Core0 = self.GetMiddleStr(str(temp), 'temp2_input:', "temp2_max:")
        if float(Core0) > 96:
            self.Test_Fail(u"CPU Core 0 Temperature:%s℃,More than 96℃,FAIL" % Core0)
        else:
            self.Test_Pass(u"CPU Core 0 Temperature:%s℃,PASS" % Core0)
        Core1 = self.GetMiddleStr(str(temp), 'temp3_input:', "temp3_max:")
        if float(Core1) > 96:
            self.Test_Fail(u"CPU Core 1 Temperature:%s℃,More than 96℃,FAIL" % Core1)
        else:
            self.Test_Pass(u"CPU Core 1 Temperature:%s℃,PASS" % Core1)

    #内存检测
    def MemeryCheck(self):
        self.Test_Running(u"##### Memory Check #####")
        self.Send_Command("iostat -m")
        mem = self.Send_Command("free | grep Mem | awk '{print $2}'", "#", 30)
        mem = self.GetMiddleStr(str(mem), "}'", "[").strip()
        if float(mem) < 8126000:
            self.Test_Fail(u"Memory ＜ 8G,FAIL")
        else:
            self.Test_Pass(u"Memory:%s,PASS" % mem)

    #版本检测
    def VersionCheck(self):
        self.Test_Running(u"##### Version Check #####")
        vershow = self.Send_Command("vershow&", "Done", 60,5)
        underlying_version=self.GetMiddleStr(vershow,'underlying version:',"Config").strip()
        if underlying_version == self.GNS_Underlying:
            self.Test_Pass(u"Software Version：%s,PASS" % underlying_version)
        else:
            self.Test_Fail(u"Software Version：%s,FAIL" % underlying_version)
        fpga = self.Send_Command('fpga_version')
        FPGA=self.GetMiddleStr(fpga,'version:',"[").strip()
        if FPGA == self.GNS_FPGA:
            self.Test_Pass(u"FPGA：%s,PASS" % FPGA)
        else:
            self.Test_Fail(u"FPGA：%s,FAIL" % FPGA)
        swv = self.Send_Command('swv_read')
        swv = self.GetMiddleStr(swv, "version :", "[").strip()
        if swv == self.GNS_SWV:
            self.Test_Pass(u"SWV：%s,PASS" % swv)
        else:
            self.Test_Fail(u"SWV：%s,FAIL" % swv)
        mod = self.Send_Command('mod_read')
        mod = self.GetMiddleStr(mod, "Mod number:", "[").strip()
        if mod == self.GNS_MOD:
            self.Test_Pass(u"MOD：%s,PASS" % mod)
        else:
            self.Test_Fail(u"MOD：%s,FAIL" % mod)
        spn = self.Send_Command('spn_read')
        spn = self.GetMiddleStr(spn, "part number:", "[").strip()
        if spn == self.GNS_SPN:
            self.Test_Pass(u"SPN：%s,PASS" % spn)
        else:
            self.Test_Fail(u"SPN：%s,FAIL" % spn)
        dpn = self.Send_Command('dpn_read')
        dpn = self.GetMiddleStr(dpn, "PN_VERSION:", "[").strip()
        if dpn == self.GNS_DPN:
            self.Test_Pass(u"DPN：%s,PASS" % dpn)
        else:
            self.Test_Fail(u"DPN：%s,FAIL" % dpn)
        bpn = self.Send_Command('board_pn_read')
        bpn = self.GetMiddleStr(bpn, "Board_Product_Number:", "[").strip()
        if bpn == self.GNS_BPN:
            self.Test_Pass(u"BPN：%s,PASS" % bpn)
        else:
            self.Test_Fail(u"BPN：%s,FAIL" % bpn)

        fpgapn = self.Send_Command('fpgapn_read')
        fpgapn = self.GetMiddleStr(fpgapn, "fpga part number:", "[").strip()
        if fpgapn == self.GNS_FPGAPN:
            self.Test_Pass(u"FPGA PN：%s,PASS" % fpgapn)
        else:
            self.Test_Fail(u"FPGA PN：%s,FAIL" % fpgapn)

        isopn = self.Send_Command('isopn_read')
        isopn = self.GetMiddleStr(isopn, "iso part number:", "[").strip()
        if isopn == self.GNS_ISOPN:
            self.Test_Pass(u"ISO PN：%s,PASS" % isopn)
        else:
            self.Test_Fail(u"ISO PN：%s,FAIL" % isopn)

        if "3.10.5-3.el6.x86_64" in self.Send_Command('uname -a'):
            self.Test_Pass(u"System Version：3.10.5-3.el6.x86_64,PASS")
        else:
            self.Test_Fail(u"System Version：3.10.5-3.el6.x86_64,FAIL")

        dsn = self.Send_Command('dsn_read')
        bsn = self.Send_Command('board_sn_read')

        if "failed" in vershow:
            self.Test_Fail(u"Version Upgrade FAIL")

    #USB模块检测
    def USBCheck(self):
        self.Test_Running(u"##### USB Check #####")
        self.Prompt(u"Please insert a USB flash drive in FAT32 format")     #消息提示
        self.Send_Command('mkdir usb','#',10)
        usb_drive=self.Send_Command("fdisk -l | grep FAT32 | awk '{print $1}'")
        drive= self.GetMiddleStr(str(usb_drive),"}'","[").strip()
        if '/dev/sd' in drive:
            self.Test_Pass('U Disk PASS')
            self.Send_Command('mount %s usb' % drive)
            self.Send_Command('cd usb' )
            usb_wr = self.Send_Command('dd bs=1M count=100 if=%s of=test conv=fsync'%drive,'#',30)
            usb_wr_A= self.GetMiddleStr(str(usb_wr),'s,',"[")
            self.Send_Command('rm -rf test')
            self.Send_Command('cd ..' )
            self.Send_Command('umount usb')
            self.Send_Command('rm -rf usb')
            self.Test_Pass(u"USB W+R Rate: %s"%str(usb_wr_A) )
        else:
            self.Test_Fail(u'U Disk FAIL' )

    #硬盘检测
    def SSDCheck(self):
        self.Test_Running(u"### SSD Check ###")
        if 'SATA' in self.Send_Command('lspci'):
            self.Test_Pass(u'SSD Module Recognition PASS')
        else:
            self.Test_Fail(u"SSD Module Recognition FAIL")
        num1 = self.Send_Command("fdisk -l | grep -c sda")
        num2 = self.Send_Command("df | grep -c sda")
        if "7" in num1 and "4" in num2:
            GNS_DISK = self.Send_Command('fdisk -l | grep sda')
            sda_size = self.GetMiddleStr(GNS_DISK, '/dev/sda:', "GB")
            if float(sda_size) > 950:
                self.Test_Pass(u"SSD-1 size=%sGB PASS" % sda_size)
            else:
                self.Test_Fail(u"SSD-1 size＜950GB FAIL")

            GNS_DISK = self.Send_Command('fdisk -l | grep sdb')
            if '/dev/sdb' in GNS_DISK:
                sdb_size = self.GetMiddleStr(str(GNS_DISK), 'Disk /dev/sdb: ', "GB,")
                if float(sdb_size) > 950:
                    self.Test_Pass(u"SSD-2 size=%sGB PASS" % sdb_size)
                else:
                    self.Test_Fail(u"SSD-2 size＜950GB FAIL")
            else:
                self.Test_Fail(u"SSD-2 Recognition FAIL ")
            HD_write = self.Send_Command('dd bs=16M count=1024 if=/dev/zero of=test conv=fdatasync', '#', 300,10)
            HD_write_A = self.GetMiddleStr(str(HD_write), 's,', "MB/s")
            HD_read = self.Send_Command('dd bs=16M if=test of=/dev/null', '#', 300,10)
            HD_read_A = self.GetMiddleStr(str(HD_read), 's,', "MB/s")
            self.Send_Command("rm -rf test", "#", 30)
            if float(HD_write_A) < 150:
                self.Test_Fail(u"SSD Write Rate < 150MB/s FAIL")
            elif float(HD_read_A) < 170:
                self.Test_Fail(u"SSD Read Rate < 170MB/s FAIL")
            else:
                self.Test_Pass(u"SSD Read Rate：%sMB/s PASS" % str(HD_read_A))
                self.Test_Pass(u"SSD Write Rate：%sMB/s PASS" % str(HD_write_A))
        else:
            self.Test_Fail(u"SSD Partition FAIL")

    #离散量检测
    def Discrete(self):
        self.Test_Running(u"#### Discrete Check ####")
        self.Send_Command("arinc set_control_off")
        for i in range(1,17):
            if i<15:
                self.Send_Command("hi8435_cfg wrDiscOut %s low" % str(i))
            else:
                self.Send_Command("hi8435_cfg wrDiscOut %s low" % str(i))
        low = self.Send_Command("arinc  get_signalstatusmatrix", '#', 5)
        low=self.GetMiddleStr(low,'get_signalstatusmatrix','[')
        low = int(low[3] + low[7] + low[11] + low[15] + low[19] + low[23] + low[27] + low[31] + low[35] + low[39] + low[44] +low[49] + low[54])
        for i in range(1, 17):
            if i < 15:
                self.Send_Command("hi8435_cfg wrDiscOut %s high" % str(i))
            else:
                self.Send_Command("hi8435_cfg wrDiscOut %s high" % str(i))
        high = self.Send_Command("arinc  get_signalstatusmatrix", '#', 5)
        high = self.GetMiddleStr(high,'get_signalstatusmatrix','[')
        high = int(high[3] + high[7] + high[11] + high[15] + high[19] + high[23] + high[27] + high[31] + high[35] + high[39] +high[44] + high[49] + high[54])
        log1=low+high
        for i in range(1, 17):
            if i < 15:
                self.Send_Command("hi8435_cfg wrDiscOut %s low" % str(i))
            else:
                self.Send_Command("hi8435_cfg wrDiscOut %s low" % str(i))
        low = self.Send_Command("arinc  get_signalstatusmatrix", '#', 5)
        low = self.GetMiddleStr(low, 'get_signalstatusmatrix', '[')
        low = int(low[3] + low[7] + low[11] + low[15] + low[19] + low[23] + low[27] + low[31] + low[35] + low[39] + low[44] +low[49] + low[54])
        log2=high+low
        if log1==1111111111111 and log2==1111111111111:
            self.Test_Pass('Discrete Check PASS')
        else:
            self.Test_Fail('Discrete Check FAIL')

        #429检测
        self.Test_Running(u"##### ARINC429 Check #####")
        self.Send_Command("hi3593_c0_cfg setRx1BitRate  high\r")
        self.Send_Command("hi3593_c0_cfg setRx2BitRate  high\r")
        self.Send_Command("hi3593_c0_cfg setTxBitRate high\r")
        self.Send_Command("hi3593_c1_cfg setRx1BitRate  high\r")
        self.Send_Command("hi3593_c1_cfg setRx2BitRate  high\r")
        self.Send_Command("hi3593_c1_cfg setTxBitRate high\r")

        if int(self.GetMiddleStr(self.Send_Command("ps | grep -c netlink_u_self.APP"), "self.APP", "[")) < 1:
            self.Send_Command("netlink_u_app &\r", '#', 3)
        c = self.Send_Command("hi429_sendmsg_user_chip0 123 3\r")

        if "0x42910001" in c:
            self.Test_Pass(u"ARINC429 CHIP0 PASS")
            #if "0x42910002" not in c:
                #self.Test_Fail(u"429 CHIP0 RX2  测试失败")
        else:
            self.Test_Fail(u"ARINC429 CHIP0 FAIL")

        d = self.Send_Command("hi429_sendmsg_user_chip1 456 3\r")
        if "0x42920001" in d:
            self.Test_Pass(u"ARINC429 CHIP1 PASS")
            #if "0x42920002" not in d:
                #self.Test_Fail(u"429 CHIP1 RX4 测试失败")
        else:
            self.Test_Fail(u"ARINC429 CHIP1 FAIL")

    #升级
    def upgrade(self,PD,Host,Boot,Kernel,APP,Config,MAC,Server_IP):

        self.working = True
        self.starttime = datetime.datetime.now()
        self.PD = PD
        self.Host = Host
        self.Boot = Boot
        self.Kernel = Kernel
        self.APP = APP
        self.Config = Config
        self.MAC = MAC
        self.error_count = 0
        self.Connection(Host)
        time.sleep(5)

        PD_message = self.Send_Command("cat /sbin/PRODUCT_MESSAGE ","#",5 )
        SN = self.GetMiddleStr(str(PD_message),'SN_VERSION:',"PN_VERSION:").strip()
        PN = self.GetMiddleStr(str(PD_message),"PN_VERSION:",'CPLD').strip()
        if self.Boot == '' and self.Kernel == "" and self.APP == "" and self.Config == "":
            if "failed" not in self.Send_Command("vershow",'#',15):
                if len(self.MAC) == 17:
                    self.Test_Running(u"program PD information")
                    self.Send_Command("pm_flash " + str(self.PD).lower() +" "+ PN + " "+ self.MAC + " "+ SN,"complete",20 )
                    self.Send_Command("configsave","Config save success",10)
                    self.Send_Command("\r")
            else:
                self.Test_Fail(u'请先升级')
        else:
            while self.working :
                if self.Boot != '':
                    self.Test_Running(u"upgrade Boot")
                    if "timeout" in self.Send_Command("tftp -gr "+ self.Boot + " "+ Server_IP,"#",10):
                        self.Test_Fail(u"文件上传失败")
                    if 'failed ' in self.Send_Command("bootupdate "+ self.Boot,"#",30):
                        self.Test_Fail(u'Boot文件不匹配')
                    self.Send_Command("\r")

                if self.Kernel != "":
                    self.Test_Running(u"upgrade Kernel")
                    self.Send_Command("tftp -gr " + self.Kernel + " "+ Server_IP,"#",30 )
                    self.Send_Command("kernelupdate " + self.Kernel,"system for testing",150)
                    self.Send_Command("\r")

                if self.APP != "":
                    self.Test_Running(u"upgrade APP")
                    self.Send_Command("rm /mnt/mmcfs/fsself.APP*")
                    self.Send_Command("ls -l /mnt/mmcfs","#",5)
                    self.Send_Command("tftp -gr " + self.APP + " "+ Server_IP,"#",30)
                    self.Send_Command("fsappsave %s &"%self.APP,"Done",600)
                    self.Send_Command("\r")

                if self.Config != "":
                    self.Test_Running(u"upgrade Configuration")
                    self.Send_Command("rm /mnt/mmcfs/fscon*")
                    self.Send_Command("ls -l /mnt/mmcfs","#",5)
                    self.Send_Command("tftp -gr " + self.Config + " " +Server_IP,"#",10 )
                    if self.PD == 'CWAP' or self.PD == 'TWCU':
                        self.Send_Command("fsconsave 0 " + self.Config,"save succes",30)
                    else:
                        self.Send_Command("fsconsave 10 " + self.Config,"save succes",30)
                    self.Send_Command("\r")
                self.Send_Command("reboot\r","reboot")
                self.Connect.Close()
                self.Test_Running(u"rebooting")
                time.sleep(100)
                if self.PD == 'RWS22':
                    Host_IP = "10.66.10.1"
                    self.Connection(str(Host_IP))

                if len(self.MAC) == 17:
                    self.Test_Running(u"program PD information")
                    self.Send_Command("pm_flash " + str(self.PD).lower() +" "+ PN + " "+ self.MAC + " "+ SN,"complete",20 )
                    self.Send_Command("configsave","save success",10)
                    self.Send_Command("\r")

                if self.Boot != '':
                    self.Test_Running(u"upgrade sBoot2")
                    self.Send_Command("tftp -gr "+ self.Boot + " "+ Server_IP,"#",10)
                    self.Send_Command("bootupdate "+ self.Boot,"#",30)
                    self.Send_Command("\r")

                if self.Kernel != "":
                    self.Test_Running(u"upgrade Kernel 2")
                    self.Send_Command("kernelconfirm")
                    self.Send_Command("tftp -gr " + self.Kernel + " "+ Server_IP ,"#",30)
                    self.Send_Command("\r")
                    self.Send_Command("kernelupdate " + self.Kernel,"system for testing",150)
                    self.Send_Command("\r")

                if self.APP != "":
                    self.Test_Running(u"upgrade APP 2")
                    self.Send_Command("tftp -gr " + self.APP + " "+ Server_IP,"#",30 )
                    self.Send_Command("fsappsave %s &"%self.APP,"Done",600)
                    self.Send_Command("\r")
                if self.Config != "":
                    self.Test_Running(u"upgrade Configuration 2")
                    self.Send_Command("tftp -gr " + self.Config + " " +Server_IP,"#",10)
                    if self.PD == 'CWAP' or self.PD == 'TWCU':
                        self.Send_Command("fsconsave 0 " + self.Config,"save succes",30)
                    else:
                        self.Send_Command("fsconsave 10 " + self.Config,"save succes",30)
                    self.Send_Command("\r")

                self.Send_Command("reboot\r","reboot")
                self.Connect.Close()
                self.Test_Running(u"rebooting")
                time.sleep(100)
                self.Connection(str(Host_IP))
                if self.Kernel != "":
                    self.Send_Command("kernelconfirm")
                self.Test_Running(u"checking version")
                if "failed" in self.Send_Command("vershow",'#',15):
                    self.Test_Fail(u'版本错误,升级失败')
                else:
                    self.Test_Finished(u"升级成功")

    #升级config
    def Ship_Out(self,PD,Host,Config,Server_IP):
        self.PD = PD
        self.Connection(Host)       #连接主机
        time.sleep(5)
        if Config != "":
                self.Test_Running(u"upgrade configuration")
                self.Send_Command("rm /mnt/mmcfs/fscon*")
                self.Send_Command("ls -l /mnt/mmcfs","#",5)
                self.Send_Command("tftp -gr " + Config + " " +Server_IP,"#",5 )
                self.Ship_Out_Address_setting(U"请输入需要设置的二、三段地址")
                self.Send_Command("fsconsave " + self.Ship_Out_Address + " " + Config,"save succes",30)
                self.Send_Command("\r")
                self.Send_Command("reboot\r","reboot")
                self.Connect.Close()
                self.Test_Running(u"rebooting")
                time.sleep(120)
                Ship_IP = "10."+self.Ship_Out_Address+".1"
                self.Connection(str(Ship_IP))
                self.Test_Running(u"upgrade configuration 2")
                self.Send_Command("tftp -gr " + Config + " " +Server_IP,"#",5)
                self.Send_Command("fsconsave " + self.Ship_Out_Address + " " + Config,"save succes",30)
                self.Send_Command("\r")
                self.Send_Command("reboot\r","reboot")
                self.Connect.Close()
                self.Test_Running(u"rebooting")
                time.sleep(100)
                self.Connection(str(Ship_IP))
                self.Test_Running(u"checking version")
                if "failed" in self.Send_Command("vershow",'#',15):
                    self.Test_Fail(u'版本错误,升级失败')
                else:
                    self.Test_Finished(u"出厂配置完成")

    #修改IP地址
    def Modify_IP(self,PD,Host):
        self.PD = PD
        self.Connection(Host)
        time.sleep(5)
        self.Test_Running(u"Modify IP address:")
        self.Send_Command("\r")
        IP_Modify = self.Input_IP(U"请输入你想改成的设备IP地址:")
        PCB_MAC = self.Send_Command("cat sbin/PRODUCT_MESSAGE | grep MacAddr | awk '{print $1}'")
        FT600_MAC = str(PCB_MAC[-13:-8])
        self.Send_Command("sed -i 's/" + Host + "/" + IP_Modify + "/g' /etc/config/Ethernet")
        self.Send_Command("sed -i 's/255.255.255.0/255.0.0.0/g' /etc/config/Ethernet")
        self.Send_Command("cat /etc/config/Ethernet")
        self.Send_Command("configsave", "config save success", 30)
        self.Send_Command("reboot","reboot")
        if PD == 'RWLU-1U':
            self.Connect.Close()
            FT600_IP = str(Host[:-3] + str(int(Host[-3:]) + 100))
            FT600_Modify_IP = IP_Modify[:-3] + str(int(IP_Modify[-3:]) + 100)
            try:
                self.Connection(str(FT600_IP))
            except Exception, e:
                self.Test_Fail(e)
            self.FT600_Login()
            self.Send_Command("sed -i 's/11:12/" + str(FT600_MAC).upper() + "/g' /sbin/PRODUCT_MESSAGE ")
            self.Send_Command("rm /etc/config/wireless")
            self.Send_Command("sed -i '/br-lan/'d /etc/rc.d/rcS")
            self.Send_Command("sed -i '/net.sh start/a\ifconfig br-lan " + FT600_Modify_IP + "' /etc/rc.d/rcS ")
            self.Send_Command("sed -n '/br-lan/p' /etc/rc.d/rcS")
            self.Send_Command("reboot","reboot")
            time.sleep(2)
        self.Test_Finished(u"IP修改成功")

    #磁盘格式化
    def Format_Disk(self,PD, Host):
        self.PD = PD
        self.Connection(Host)
        time.sleep(5)
        self.Test_Running(u"Format DISK")
        if '5' not in self.Send_Command('fdisk -l  | grep -c "/dev/sda"'):
                self.Send_Command("fdisk /dev/sda","Command (m for help):")
                self.Send_Command("n",":")
                self.Send_Command("p","Partition number (1-4):")
                self.Send_Command("1","):")
                self.Send_Command("","):")
                self.Send_Command("+900M","Command (m for help):")
                self.Send_Command("n",":")
                self.Send_Command("p","Partition number (1-4):")
                self.Send_Command("2","):")
                self.Send_Command("","):")
                self.Send_Command("+100M","Command (m for help):")
                self.Send_Command("n",":")
                self.Send_Command("p","Partition number (1-4):")
                self.Send_Command("3","):")
                self.Send_Command("","):")
                self.Send_Command("+2048M","Command (m for help):")
                self.Send_Command("n",":")
                self.Send_Command("p","Partition number (1-4):")
                self.Send_Command("","):")
                self.Send_Command("","Command (m for help):")
                self.Send_Command("t","Partition number (1-4):")
                self.Send_Command("3","Hex code (type L to list codes):")
                self.Send_Command("82","Command (m for help):")
                self.Send_Command("p","Command (m for help):")
                self.Send_Command("w"," #")
                self.Send_Command("fdisk -l"," #")
                self.Send_Command("mkfs.ext3 /dev/sda1"," #")
                self.Send_Command("mkfs.ext3 /dev/sda2"," #")
                self.Send_Command("mkfs.ext3 /dev/sda3"," #")
                self.Send_Command("mkfs.ext3 /dev/sda4"," #")
                self.Send_Command("mount /dev/sda4 /mnt/mmc0")
                self.Send_Command("mount /dev/sda1 /mnt/mmc1")
                self.Send_Command("df -h")
        self.Test_Finished(u"硬盘格式化成功")