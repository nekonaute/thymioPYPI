import sys

def log(message,info):
    sys.stdout.write("\r" + message + ": " + info)
    sys.stdout.flush()
