import threading
import time
from motion_sensor import motion_detection
from web_server import run_flask

try:
    motion_thread = threading.Thread(target=motion_detection)
    motion_thread.daemon = True # ensure thread exits when main program does
    motion_thread.start()

    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    while True:
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Exiting program.")
finally:
    from motion_sensor import stop_all
    stop_all()
    print("Program exited.")