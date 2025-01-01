from wifi import connect_wifi, setup_ap_mode, sync_time
from sensor import read_sensor
from control import periodic_read
from webserver import start_webserver
from machine import Timer

# Program Utama
if __name__ == "__main__":
    if not connect_wifi():
        setup_ap_mode()
    else:
        sync_time()

    timer = Timer(-1)
    timer.init(period=100000, mode=Timer.PERIODIC, callback=periodic_read)
    start_webserver()