from thread import start_new_thread
import subprocess
import time
import urllib2


def server_loop():
    while True:
        subprocess.call(['python main.py'], shell=True)
        print "Restart"


def request_loop():
    time.sleep(10)
    while True:
        print "Request"
        response = urllib2.urlopen("http://127.0.0.1:8080/request/flower")
        print "Response " + str(response.code)
        time.sleep(900)

if __name__ == '__main__':
    start_new_thread(request_loop, ())
    server_loop()