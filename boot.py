# boot.py -- run on boot-up

# Add a mechanism to handle the stopScript command
stop_script = False  # Flag to control the script execution

def handle_stop_script():
    global stop_script
    stop_script = True  # Set the flag to stop the script
