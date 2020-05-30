# generosity #
**this project is only for educational purpose**

"reverse_shell.py" script is a **reverse shell** which is meant to be executed from victim's machine
once executed the reverse shell then tries to connect to our server, which is implemented in **the_server.py** script,
even if the reverse shell fails to connect to the server, it will retry to connect every 10sec.
Once executed the reverse shell copies itself to multiple loactions in the victim's system.

If our reverse shell establishes a connection with our server successfully, we can execute mulitple commands in the victim's machine
e.g: execute shell commands, take screenshots, download and upload files from victim's machines etc.

**we can also run a keylogger and get the log in our machine**
