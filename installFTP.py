#!/usr/bin/python
import readline
import commands
import re
import os
import getpass
__author__ = 'python-newbie'

'''
run  command  "python  start.py"  to start install


如果需要自己配置相关文件和目录，请在配置类Config_modle中指定，各个属性说明如下


__ftp_guest_user = "ftpuser"
#虚拟用户宿主用户
__vuser_file_name = "vuser.txt"  
#虚拟用户名称和密码文件
__vuser_encry_file = "userscret.db" 
#虚拟用户名称和密码文件加密文件
__vuser_user_db_file_dir="/etc/vsftpd" 
#虚拟用户名称密码文件和加密后的数据库文件存放目录
__ftp_pam_file = "vsftp.vu"  
#pam认证文件
__vuser_config_dir = "/etc/vsftpd/vuser_config" 
#虚拟用户配置文件目录
__vuser_home_dir = "/var/ftp/vuser1" 
#第一次安装vsftp创建的一个虚拟用户的默认家目录
'''


class Config_modle(object):
    __ftp_guest_user = "vsftpd"
    __vuser_file_name = "vuser.txt"  
    __vuser_encry_file = "vuser.db" 
    __vuser_user_db_file_dir="/etc/vsftpd"
    __ftp_pam_file = "vsftpd.vu"    
    __vuser_config_dir = "/etc/vsftpd/vuser_config" 
    __vuser_home_dir = "/var/ftp/vuser1"

    def get_ftpguestuser(self):
        return self.__ftp_guest_user
    def get_vuserfilename(self):
        return self.__vuser_file_name
    def get_vuserencryfile(self):
        return self.__vuser_encry_file
    def get_vuserdbfiledir(self):
        return self.__vuser_user_db_file_dir
    def get_ftppamfile(self):
        return self.__ftp_pam_file
    def get_vuserconfigdir(self):
        return self.__vuser_config_dir
    def get_vuserhomedir(self):
        return self.__vuser_home_dir

class Delvuser(object):
    def __init__(self,config_modle):
        '''
        self.__vuser_file="user.txt"
        self.__vuser_file_db="user.db"
        self.__vuser_file_db_dir="/work"
        self.__vuser_config_dir="/work/config"
        '''
        self.__vuser_file=config_modle.get_vuserfilename()
        self.__vuser_file_db=config_modle.get_vuserencryfile()
        self.__vuser_file_db_dir=config_modle.get_vuserdbfiledir()
        self.__vuser_config_dir=config_modle.get_vuserconfigdir()
    def __checkuser(self,vusername):
        userfile=self.__vuser_file_db_dir+"/"+self.__vuser_file
        ul=open(userfile)
        vuserlist=[]
        tag=1
        for i in ul:
            vuserlist.append(i)
        ul.close()
        for i in range(1,len(vuserlist)):
            vuserlist[i]=vuserlist[i].replace("\n","")
        for i in vuserlist:
            if tag % 2 != 0:
                if i == vusername:
                    self.__deluser=vusername
                    self.__index=tag
                    return True
            tag=tag+1
        return False
    def __delvirtualuserenv(self):
        userfile=self.__vuser_file_db_dir+"/"+self.__vuser_file
        userlist=[]
        tmp=[]
        with open(userfile) as ul:
            for i in ul:
                userlist.append(i)
                tmp.append(i)
            ul.close()
        un=tmp.pop(self.__index-1)
        userlist.remove(un)
        pwd=tmp.pop(self.__index-1)
        userlist.remove(pwd)
        with open(userfile,"w") as uf:
            str=""
            for i in userlist:
                str=str+i
            uf.write(str)
            uf.close()
        print("the virtual user has been remove from "+self.__vuser_file+"....")
        print("now  recreate the virtual user db file ........")
        if os.system("cd "+self.__vuser_file_db_dir+" && db_load -T -t hash -f "+self.__vuser_file+" "+self.__vuser_file_db) !=0:
            print("run db_load failure . please check your db_load commands!!!")
        print"create virtual user db sucess ........."
        userconf=self.__vuser_config_dir+"/"+self.__deluser
        if os.path.exists(userconf):
            self.__vuser_homedir=commands.getstatusoutput("grep local_root "+userconf+"|awk -F'=' '{print $2}'")[1]
            os.system("rm -f "+self.__vuser_config_dir+"/"+self.__deluser)
            print("the virtual user configure: "+userconf+" has been  remove ..........")
        else:
            print"the virtual user configure file not exist!! "
        if os.path.exists(self.__vuser_homedir):
            os.system("rm -rf "+self.__vuser_homedir)
            print("virtual user home dir: "+self.__vuser_homedir+"  has been   remove........")
        else:
            print("virtual home dir "+self.__vuser_homedir+" not exists!!! ")


    def __delvirtualuser(self,vusername):
        if self.__checkuser(vusername):
            res=raw_input("Do you really want to delete virtual user: "+vusername+" ? (yes/no)")
            if res.strip() == "no":
                print "Exit  Delete  Bye ~~~~"
            elif res.strip() == "yes":
                print"begining to remove this virtaul user........."
                self.__delvirtualuserenv()
            else:
                print("you input error choice!  exit now")
        else:
            print("the virtual user not exists!!!! please check user name ")
    def startdeluser(self,vusername):
        self.__delvirtualuser(vusername)




class SystemInfo(object):
    def __init__(self):
        self._version=commands.getoutput("awk '{print $3}' /etc/redhat-release|awk -F'.' '{print $1}'")
        self._os=commands.getoutput("awk '{print $1}' /etc/redhat-release")
        self._arch=commands.getoutput("uname -r|awk -F'_' '{print $2}'")
    def getarch(self):
        return self._arch
    def getos(self):
        return self._os
    def getversion(self):
        return self._version


class InstallRepo(object):
    def __init__(self,systeminfo):
        self._version=systeminfo.getversion()
        self._os=systeminfo.getos()
        self._arch=systeminfo.getarch()

    def __getepel(self):
        os.system("wget http://mirrors.sohu.com/fedora-epel/epel-release-latest-"+self._version+".noarch.rpm"+" &>/dev/null")
        if not os.path.exists("epel-release-latest-"+self._version+".noarch.rpm"):
            print("\nget epel rpm failure.....")
            return False
        return True
    def __installepel(self):
        if self.__getepel():
            epel_name="epel-release-latest-"+self._version+".noarch.rpm"
            if commands.getstatusoutput("rpm -qa|grep epel")[0] == 0:
                #os.system("rpm -qa|grep epel|xargs rpm -e ")
                return
            status=commands.getstatusoutput("rpm -ivh "+epel_name)
            os.system("yum clean all &>/dev/null")
            os.system("yum makecache &>/dev/null")
            if status[0] != 0:
                print("install epel failure......")
                exit(1)
            os.system("rm -rf "+epel_name)
            print("install epel success......")

    def start(self):
        self.__installepel()



class autovsftp(object):
     def __init__(self,config_modle):
        self._arch=commands.getoutput("uname -r|awk -F'_' '{print $2}'")
        self.__ftp_guest_user = config_modle.get_ftpguestuser()
        self.__vuser_file_name = config_modle.get_vuserfilename()
        self.__vuser_file_dir = config_modle.get_vuserdbfiledir()
        self.__vuser_encry_file = config_modle.get_vuserencryfile()
        self.__vuser_encry_file_dir = config_modle.get_vuserdbfiledir()
        self.__ftp_pam_file = config_modle.get_ftppamfile()
        self.__vuser_config_dir = config_modle.get_vuserconfigdir()
        self.__vuser_home_dir = config_modle.get_vuserhomedir()
     def __installftp(self):
        if commands.getstatusoutput('yum install lftp vsftpd -y &>/dev/null')[0] != 0:
            print("\ninstall vsftpd failure!!!!!!!!! please check your system repo")
            exit(1)
     def __modificonfig(self):
        if os.path.exists("/etc/vsftpd/vsftpd.conf"):
            os.system("mv /etc/vsftpd/vsftpd.conf /etc/vsftpd/vsftpd.conf.bak")
        config_anon = "anonymous_enable=NO\n"
        config_ftpsys = "ascii_upload_enable=YES\nascii_download_enable=YES\nlisten=YES\nasync_abor_enable=YES\nmax_clients=100\nmax_per_ip=50\nls_recurse_enable=NO\nxferlog_enable=YES\nxferlog_std_format=YES\nconnect_from_port_20=YES\ndirmessage_enable=YES\nftpd_banner=Welcome use Ftp Server\n"
        config_localuser = "local_enable=YES\nlocal_max_rate=1000000\n"
        config_guest = "guest_enable=YES\nguest_username="+self.__ftp_guest_user+"\npam_service_name="+self.__ftp_pam_file+"\nuser_config_dir="+self.__vuser_config_dir+"\n"
        content = config_anon+config_ftpsys+config_guest+config_localuser
        ftp_config_file=open("/etc/vsftpd/vsftpd.conf","w")
        ftp_config_file.write(content)
        ftp_config_file.close()
     def __addftpuser(self):
        if commands.getstatusoutput("grep "+self.__ftp_guest_user+" /etc/passwd")[0] != 0:
            os.system("useradd "+self.__ftp_guest_user+" -s /sbin/nologin")
        else:
            print("\nyou have add ftp user !!!!!!")
     def __generate_pamfile(self):
        arch=""
        if "x86_64" in commands.getoutput("lscpu|head -1|awk '{print $2}'"):
            arch = "64"
        else:
            arch = ""
        content = "auth required /lib"+arch+"/security/pam_userdb.so db="+self.__vuser_encry_file_dir+"/"+self.__vuser_encry_file.split(".")[0]+"\n"
        content+="account required /lib"+arch+"/security/pam_userdb.so db="+self.__vuser_encry_file_dir+"/"+self.__vuser_encry_file.split(".")[0]+"\n"
        pamfile=open("/etc/pam.d/"+self.__ftp_pam_file,"w")
        pamfile.write(content)
        pamfile.close()
     def __generate_vuser_file(self):
        contents = "user\n123123\n"
        vfile = self.__vuser_file_dir+"/"+self.__vuser_file_name
        if not os.path.exists(self.__vuser_file_dir):
            os.system("mkdir "+self.__vuser_file_dir)
            if os.path.exists(vfile):
                os.system("mv "+vfile+" "+vfile+".bak")
        vf = open(vfile,"w")
        vf.write(contents)
        vf.close()
     def __generate_vuser_home_dir(self):
        if not os.path.exists(self.__vuser_home_dir):
            os.system("mkdir -p "+self.__vuser_home_dir)
            pos=self.__vuser_home_dir.rfind('/')
            p_dir=self.__vuser_home_dir[:pos]
            os.system("chmod 777 %s" %p_dir)
     def __getvuser4config(self):
        vfile = self.__vuser_file_dir+'/'+self.__vuser_file_name
        num = 0
        user_list = []
        tmp = []
        f = open(vfile)
        for i in f:
            user_list.append(i)
            num = num+1
        f.close()
        if int(num)%2 != 0:
            print("your vuser file error !! please check it rows !!!")
            exit(1)
        user_list=user_list[0::2]
        for i in user_list:
            tmp.append(i.replace("\n",""))
        if tmp and len(tmp)%2 == 0:
            print("get user from vuser file failure !! please check code")
            exit(1)
        return tmp
     def __generate_vuser_config(self):
        content="write_enable=YES\nanon_world_readable_only=NO\nanon_upload_enable=YES\nanon_mkdir_write_enable=YES\nanon_other_write_enable=YES\nlocal_root="+self.__vuser_home_dir
        if not os.path.exists(self.__vuser_config_dir):
            os.system("mkdir "+self.__vuser_config_dir)
        if not os.path.exists(self.__vuser_file_dir+"/"+self.__vuser_file_name):
            print('\nthere is not virtual user and password file...  please check it !')
            exit(1)
        vuser = self.__getvuser4config()
        if len(vuser) == 0:
            print("\nthis is no user in virtual user file!!!")
            exit(1)
        for i in vuser:
            print(i)
            f = open(self.__vuser_config_dir+"/"+i, "w")
            f.write(content)
            f.close()
     def __dbload_userfile(self):
        vfiles = self.__vuser_file_dir + "/" + self.__vuser_file_name
        vfile_db = self.__vuser_encry_file_dir+"/"+self.__vuser_encry_file
        if not os.path.exists(vfiles):
             print("\nyour virtual user file not exists!!!")
             exit(1)
        if commands.getstatusoutput("which db_load")[0] != 0:
             os.system("yum install db4-utils &>/dev/null")
        if commands.getstatusoutput("db_load -T -t hash -f "+vfiles+" "+vfile_db)[0] != 0:
             print("\ngenerate  virtual user db file failure!!!!!!!  please check your commands!")
             exit()
     def __modifi_file_auth(self):
        os.system("chmod 700 "+ self.__vuser_encry_file_dir+"/"+self.__vuser_encry_file)
        os.system("chown -R "+ self.__ftp_guest_user+"."+self.__ftp_guest_user+" "+self.__vuser_home_dir)
        os.system("chmod 755 " + self.__vuser_home_dir)
     def start_ftpinstall(self):
        self.__installftp()
        self.__addftpuser()
        self.__modificonfig()
        self.__generate_vuser_file()
        self.__dbload_userfile()
        self.__generate_pamfile()
        self.__generate_vuser_home_dir()
        self.__generate_vuser_config()
        self.__modifi_file_auth()
        print"\nFTP Server install Success!!!  "
        print"\nvirtaul username: user  , virtual userpassword: 123123  "
        print "\nplease run commands : lftp user@localhost login in ."
        os.system("service vsftpd start &>/dev/null")


class add_vitualuser(object):
    def __init__(self,configmodel):
        tmp=configmodel.get_vuserdbfiledir()+"/"
        self.__vuser_file_db=tmp+configmodel.get_vuserencryfile()
        self.__vuser_file=tmp+configmodel.get_vuserfilename()
        self.__vuser_config_dir=configmodel.get_vuserconfigdir()
        self.__guest_user=configmodel.get_ftpguestuser()
    def __check_allfile(self):
        if not os.path.exists(self.__vuser_file):
            print(self.__vuser_file+" file not exists!!  please check it !!!")
            exit(1)
        if not os.path.exists(self.__vuser_file_db):
            print(self.__vuser_file_db+" file not exists!! please check it !!!")
            exit(1)
        if not os.path.exists(self.__vuser_config_dir):
            print(self.__vuser_config_dir+" dir not exists please check it !!")
            exit(1)
    def __checkusername(self,username):
        f=open(self.__vuser_file)
        userlist=[]
        tmp=[]
        for i in f:
            userlist.append(i)
        userlist=userlist[0::2]
        for i in userlist:
            tmp.append(i.replace("\n",""))
        for u in tmp:
            if username == u:
                return False
            continue
        return True
    def __checkuserdir(self,path):
        if os.path.exists(path):
            return 1
        res=re.match(r'^/.*',path)
        if res:
            return 0
        else:
            return 2
    def __checkpass(self,old,new):
        if old == new:
            return True
        else:
            return False
    def __modifi_userconf(self):
        conf_content="anonymous_enable=NO\nwrite_enable=YES\nanon_other_write_enable=YES\nanon_upload_enable=YES\nanon_mkdir_write_enable=YES\nlocal_root="+self.__userdir
        vc=self.__vuser_config_dir+"/"+self.__username
        if os.path.exists(vc):
            print("the file "+vc+" has been existing ! ")
            exit(1)
        c=open(self.__vuser_config_dir+"/"+self.__username,"w")
        c.write(conf_content)
        c.close()
        content=self.__username+"\n"+self.__userpass+"\n"
        f=open(self.__vuser_file,'a')
        f.write(content)
        f.close()
        pathlist=self.__vuser_file.split("/")
        filedbname=self.__vuser_file_db.split("/")
        filedbname=''.join(filedbname[len(filedbname)-1:])
        filename=''.join(pathlist[len(pathlist)-1:])
        path="/".join(pathlist[0:len(pathlist)-1])
        if commands.getstatusoutput("cd "+path+"&& db_load -T -t hash -f  "+filename+"  "+filedbname)[0] != 0:
            print("db_load commands run failure!!! ")
            exit(1)
        if commands.getstatusoutput("mkdir -p "+self.__userdir)[0] !=0:
            print("create user home dir failure !! please check it!!")
            exit(1)
        os.system("chown -R "+self.__guest_user+"."+self.__guest_user+" "+self.__userdir)
        os.system("chmod 755 "+self.__userdir)
    def __inputuserinfo(self):
        while True:
            username=raw_input("please input your virtual user name: ")
            if self.__checkusername(username):
                self.__username=username
                break
            else:
                print("input username has been existing!")
        while True:
            oldpass=getpass.getpass("please input your virtual user password: ")
            newpass=getpass.getpass("please input your virutal user password agin: ")
            if self.__checkpass(oldpass,newpass):
                self.__userpass=oldpass
                break
            else:
                print("input password different!!  please retype !!")
        while True:
            path=raw_input("please input your virtual home dir name: ")
            if self.__checkuserdir(path) == 0:
                verrify=raw_input("are you sure use this dir : " + path + " as User: " + self.__username + " Home Dir ? (yes/no)")
                if verrify == "no":
                    continue
                self.__userdir=path
                break
            elif self.__checkuserdir(path) == 1:
                print("the directory has been existing!! please retype ")
                continue
            else:
                print("the directory name is illegal !!! please retype ")
    def startaddvuser(self):
        self.__check_allfile()
        self.__inputuserinfo()
        self.__modifi_userconf()
        os.system("service vsftpd restart &>/dev/null")

if __name__ == "__main__":
    while True:
        print("     **************************************************")
        print("     -------------------------------------------------")
        print("     |      i:  install vsftpd  server                | ")
        print("     |      a:  add a virtual user for ftp server     | ")
        print("     |      d:  delete a virtual user for ftp server  | ")
        print("     |      e:  exit                                  |")
        print("     -------------------------------------------------")
        num=raw_input("( i/ a/ d / e)  : ")
        if num.strip() == "i":
           install_repo=InstallRepo(SystemInfo())
           install_repo.start()
           if os.system("rpm -qa|grep vsftpd &>/dev/null") == 0:
               print(" you have beening install vsftpd .......\n")
               continue
           installs=autovsftp(Config_modle())
           print("begining to install vsftpd .......\n")
           installs.start_ftpinstall()
           os.system("yum install sl -y &>/dev/null")
           os.system("sl ")
           break
        elif num.strip() == "a":
           if os.system("rpm -qa|grep vsftpd &>/dev/null") != 0:
               print("you havn't install the vsftpd server!!!  please install vsftpd \n")
           else:
               adduser=add_vitualuser(Config_modle())
               adduser.startaddvuser()
               print("virtual user have created !!!\n")
        elif num.strip() == "d":
            deluser=Delvuser(Config_modle())
            vusername=raw_input("please input virtual user name : ")
            deluser.startdeluser(vusername)
        elif num.strip() == "e":
            exit()
        else:
            print("you input error choice \n")
