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

'''
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
'''
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
        return self.config.sections()       	#获取所有的段
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
        #self.GNS_Server_IP = self.Config_ini.get_info("GNS", "Server_IP")
        self.GNS_aging_time = int(self.Config_ini.get_info("GNS", "aging_time"))

    # 获取本地ip
    def Local_IP(self):
        Local_IP = socket.gethostbyname(socket.gethostname())
        return Local_IP

    #连接设备
    def Connection(self,host):
        username = "gns"
        passwd = "feitian"
        try:
            self.Connect = ssh(str(host),username,passwd)
            self.Send_Command("\n")
        except Exception,e:
            self.Test_Fail(str(e))

    #发送接收数据
    def Send_Command(self,Command,Prompt='#',Timeout=10,click_time=1):
        try:
            buff = ""
            log = ""
            self.Connect.Send(Command)
            time.sleep(1)
            runtime = datetime.datetime.now()
            while Prompt not in buff:
                buff = ""
                time.sleep(3)
                buff += self.Connect.Recv(999999,click_time)
                log += buff
                self.data.put(buff)
                steptime = datetime.datetime.now()
                if (steptime - runtime).seconds > Timeout:
                    self.Test_Fail(u"超时, %s 不能找到" % Prompt)
                    break
            return log
        except Exception:
            self.Test_Fail(u"%s不能找到" % Prompt)

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
        Faillentime = datetime.datetime.now()
        second = (Faillentime - self.starttime).total_seconds()
        Time = u"测试时间：" + self.Running_time(second)     #获得老化时间
        self.Set_Status(message + "\n" + Time)              #按钮显示状态
        self.data.put(message + "  " + Time)                #入队列
        thread.exit_thread()                                #线程结束

    #测试开始提示
    def Test_Running(self,message):
        self.Set_Color(self.Yellow)         #显示黄色
        self.Set_Status(message)

    #运行时间
    def Running_time(self,second):
        h = int(second / 3600)
        m = int((second - h * 3600) / 60)
        s = int(second - h * 3600 - m * 60)
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
        self.endtime = self.starttime + datetime.timedelta(hours=self.GNS_aging_time)        #设置结束时间
        self.Test_Running(u'登录设备')           #登录信号
        self.Connection(self.Host)              #连接设备
        time.sleep(5)
        if self.Value == 0 :
            self.Rsync()                        #同步数据
            if self.error_count == 0:
                self.Test_Pass(u"同步成功")
        else:
            self.BI(Remote_IP)                  #老化测试

    '''
    #同步数据
    def Rsync(self):
        self.Test_Running(u"同步数据")
        rusername = 'safi'
        Rsync_IP = self.GNS_Server_IP
        self.Send_Command("cd /opt")
        self.Send_Command("touch feitian ")
        self.Send_Command('echo "feitian"  > feitian ')
        self.Send_Command('chmod 600 feitian ')
        log = self.Send_Command("ping " + Rsync_IP + " -c5" , "#" , 20)
        if "100% packet loss" in log:
            self.Test_Fail(u"服务器不能Ping通")
        else:
            log = self.Send_Command("rsync -auvzP --delete --password-file=feitian " + rusername + '@' + Rsync_IP + "::GNS /opt&","total size",72000)
            if "rsync error" in log:
                self.Test_Fail(u"rsync 同步失败")
            else :
                self.Send_Command('chmod 777 Local_deploy_gns.sh', "#", 60)
                self.Send_Command('./Local_deploy_gns.sh install',"#",60)
    '''

    #老化测试
    def BI(self,Remote_IP):
        iperf = os.popen("tasklist|find /c \"iperf.exe\"")  #执行统计iperf进程命令
        iperf_number = iperf.read()                         #读取iperf进程数量
        if int(iperf_number) < 1:
            os.system("start /b iperf.exe -s -w1m&")        #后台运行iperf
        os.system('netsh firewall set opmode disable')      #关闭windows系统防火墙
        os.system(
            'reg add HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\W32Time\TimeProviders\NtpServer /v Enabled /t REG_DWORD /d 1 /f')  # 修改注册表
        os.system(
            'reg add HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\W32Time\Config /v AnnounceFlags /t REG_DWORD /d 5 /f')  # 修改注册表
        os.system("net stop w32time & net start w32time")   #停止和启动windows系统NTP服务
        self.Test_Running(U"老化测试")           #开始老化信号
        self.Check_Process()                    #测试过程提升CPU利用率
        self.VersionCheck()                     #版本检测
        self.MAC_check()                        #MAC地址检测
        while self.working == True:
            time.sleep(5)
            self.ShowTemperature()              #温度检测
            self.Clock_Test()                   #时钟检测
            self.MemeryCheck()                  #内存检测
            #self.Discrete()                     #离散量检测
            if Remote_IP != None:
                self.EthSpeedCheck(Remote_IP)   #网口速率检测
            self.SSDCheck()                     #硬盘检测
            time.sleep(20)
            self.Clean_Caches()                 #清除内存
            Finish_time = datetime.datetime.now()
            if (Finish_time - self.endtime).days >= 0:
                self.Test_Pass(u"老化测试成功")
                break
            gc.collect()

    #清除内存
    def Clean_Caches(self):
        self.Test_Running(u"清除内存")
        self.Send_Command("echo 3 >> /proc/sys/vm/drop_caches&")
        time.sleep(3)
        self.Send_Command("free -m")
        self.Send_Command('cd /')

    #测试过程提升CPU利用率
    def Check_Process(self):
        if int(self.GetMiddleStr(self.Send_Command("ps -A | grep -c kcpu"), "kcpu", "[")) < 2:
            self.Send_Command("cd /sbin")
            self.Send_Command("./run_kcpu.sh start 80")
            self.Send_Command("cd /")

    #MAC地址检测
    def MAC_check(self):
        self.Test_Running(u"MAC地址检测")
        MAC = self.Send_Command("ifconfig | grep eth0")
        if "5C:E0:CA" not in MAC:
            self.Test_Fail(u"MAC地址格式错误")

    #时钟检测
    def Clock_Test(self):
        self.Test_Running(u"NTP检测")
        self.Send_Command("service ntpd stop")
        self.Send_Command("ntpdate %s &" % self.Local_IP())
        time.sleep(10)
        date = self.Send_Command("date")            #获取设备时间
        clock = str(datetime.datetime.now().year)   #获取本地时间
        if clock not in date:
            self.Test_Fail(u"时钟错误")

    #网口速率测试
    def EthSpeedCheck(self,Remote_IP):
        self.Test_Running(u"网口速率检测")
        Ping_message = self.Send_Command("ping %s -c5" % Remote_IP)
        if "Host Unreachable" in Ping_message:
            self.Test_Fail(u"Iperf 服务器地址不能Ping通")
        else:
            Eth_Speed = self.Send_Command("iperf -c %s -w1m -i1 -t30 | grep '0.0-3'" % Remote_IP, "#", 60,10)
            if "Broken pipe" in Eth_Speed:
                self.Test_Fail(u"Iperf 服务器不通")
            self.Send_Command("del_time")

    #温度检测
    def ShowTemperature(self):
        self.Test_Running(u"温度检测")
        temp = self.Send_Command("sensors -u &","Done",20)
        Core0 = self.GetMiddleStr(str(temp), 'temp2_input:', "temp2_max:")
        if float(Core0) > 96:
            self.Test_Fail(u"CPU Core 0 温度超过96℃,当前温度：%s℃" % Core0)
        Core1 = self.GetMiddleStr(str(temp), 'temp3_input:', "temp3_max:")
        if float(Core1) > 96:
            self.Test_Fail(u"CPU Core 1 温度超过96℃,当前温度：%s℃" % Core0)

    #内存检测
    def MemeryCheck(self):
        self.Test_Running(u"内存检测")
        self.Send_Command("iostat -m")
        mem = self.Send_Command("free | grep Mem | awk '{print $2}'", "#", 30)
        mem = self.GetMiddleStr(str(mem), "}'", "[").strip()
        if float(mem) < 8126000:
            self.Test_Fail(u"内存 ＜8G")

    #版本检测
    def VersionCheck(self):
        self.Test_Running(u"版本检测")
        self.Send_Command("vershow | grep Config | awk '{print $2}'",'#',10)
        self.Send_Command('fpga_version&',"Done",30)
        self.Send_Command('swv_read&',"Done",30)
        self.Send_Command('spn_read&',"Done",30)
        self.Send_Command('dpn_read&',"Done", 30)
        self.Send_Command('board_pn_read&',"Done", 30)
        self.Send_Command('mod_read&',"Done",30)
        self.Send_Command('uname -a&',"Done",30)
        self.Send_Command('dsn_read&',"Done",30)
        self.Send_Command('board_sn_read&',"Done",30)
        self.Send_Command('fpgapn_read&', "Done", 30)
        self.Send_Command('isopn_read&', "Done", 30)
        s = self.Send_Command("vershow&","Done",60)
        if "failed" in s:
            self.Test_Fail(u"版本未完全升级")

    #硬盘检测
    def SSDCheck(self):
        self.Test_Running(u"硬盘检测")
        if 'SATA' not in self.Send_Command('lspci'):
            self.Test_Fail(u"硬盘模块识别失败")
        num1 = self.Send_Command("fdisk -l | grep -c sda")
        num2 = self.Send_Command("df | grep -c sda")
        if "7" in num1 and "4" in num2:
            GNS_DISK = self.Send_Command('fdisk -l | grep sda')
            sda_size = self.GetMiddleStr(GNS_DISK, '/dev/sda:', "GB")
            if float(sda_size) < 950:
                self.Test_Fail(u"第一硬盘容量 ＜950GB")
            if self.PD == 'GNS':
                GNS_DISK = self.Send_Command('fdisk -l | grep sdb')
                if '/dev/sdb' in GNS_DISK:
                    sdb_size = self.GetMiddleStr(str(GNS_DISK), 'Disk /dev/sdb: ', "GB,")
                    if float(sdb_size) < 950:
                        self.Test_Fail(u"第二硬盘容量 ＜950GB")
                else:
                    self.Test_Fail(u"未识别到第二硬盘")
            if int(self.GetMiddleStr(self.Send_Command("ps -A | grep -c dd"), "dd", "[")) < 2:
                self.Send_Command('dd bs=16M count=1024 if=/dev/zero of=test conv=fdatasync &')
                time.sleep(400)
                self.Send_Command('dd bs=16M if=test of=/dev/null &')
                time.sleep(400)
            self.Send_Command("rm -rf test &")
            time.sleep(30)
        else:
            self.Test_Fail(u"硬盘分区未识别")
        time.sleep(30)

    #离散量测试
    def Discrete(self):
        self.Test_Running(u"离散量检测")
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
        if log1!=1111111111111 and log2!=1111111111111:
            self.Test_Fail('Discrete Check FAIL')

        # 429检测
        self.Test_Running(u"429检测")
        self.Send_Command("hi3593_c0_cfg setRx1BitRate  high\r")
        self.Send_Command("hi3593_c0_cfg setRx2BitRate  high\r")
        self.Send_Command("hi3593_c0_cfg setTxBitRate high\r")
        self.Send_Command("hi3593_c1_cfg setRx1BitRate  high\r")
        self.Send_Command("hi3593_c1_cfg setRx2BitRate  high\r")
        self.Send_Command("hi3593_c1_cfg setTxBitRate high\r")

        if int(self.GetMiddleStr(self.Send_Command("ps | grep -c netlink_u_self.APP"), "self.APP", "[")) < 1:
            self.Send_Command("netlink_u_app &\r", '#', 3)
        c = self.Send_Command("hi429_sendmsg_user_chip0 123 3\r")
        if "0x42910001" not in c:
            self.Test_Fail(u"429 CHIP0 测试失败")

        d = self.Send_Command("hi429_sendmsg_user_chip1 456 3\r")
        if "0x42920001" not in d:
            self.Test_Fail(u"429 CHIP1 测试失败")

