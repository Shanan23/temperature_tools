import ujson
import usocket
# import ussl
import time

class FIREBASE_GLOBAL_VAR:
    GLOBAL_URL = None
    GLOBAL_URL_ADINFO = None
    SLIST = {}

class INTERNAL:
    def connect(id):
        LOCAL_ADINFO = usocket.getaddrinfo(FIREBASE_GLOBAL_VAR.GLOBAL_URL_ADINFO["host"], FIREBASE_GLOBAL_VAR.GLOBAL_URL_ADINFO["port"], 0, usocket.SOCK_STREAM)[0]
        FIREBASE_GLOBAL_VAR.SLIST["S" + id] = usocket.socket(LOCAL_ADINFO[0], LOCAL_ADINFO[1], LOCAL_ADINFO[2])
        FIREBASE_GLOBAL_VAR.SLIST["S" + id].connect(LOCAL_ADINFO[-1])
        if FIREBASE_GLOBAL_VAR.GLOBAL_URL_ADINFO["proto"] == "https:":
            print("Warning: SSL is not supported. Using HTTP instead.")
        FIREBASE_GLOBAL_VAR.SLIST["SS" + id] = FIREBASE_GLOBAL_VAR.SLIST["S" + id]  # Use HTTP instead of SSL
        # Removed unnecessary else statement

    def disconnect(id):
        FIREBASE_GLOBAL_VAR.SLIST["SS" + id].close()
        FIREBASE_GLOBAL_VAR.SLIST["SS" + id] = None
        FIREBASE_GLOBAL_VAR.SLIST["S" + id] = None

    def put(PATH, DATA, id, cb):
        INTERNAL.connect(id)
        LOCAL_SS = FIREBASE_GLOBAL_VAR.SLIST["SS" + id]
        LOCAL_SS.write(b"PUT /" + PATH + b".json HTTP/1.0\r\n")
        response = LOCAL_SS.read()  # Read the response from Firebase
        LOCAL_SS.write(b"Host: " + FIREBASE_GLOBAL_VAR.GLOBAL_URL_ADINFO["host"] + b"\r\n")
        LOCAL_SS.write(b"Content-Length: " + str(len(DATA)) + b"\r\n\r\n")
        LOCAL_SS.write(DATA)
        response = LOCAL_SS.read()  # Read the response from Firebase
        print(f"Response from Firebase (PUT): {response}")  # Print the response
        LOCAL_DUMMY = response
        del LOCAL_DUMMY
        INTERNAL.disconnect(id)
        if cb:
            cb()

    def patch(PATH, DATATAG, id, cb):
        INTERNAL.connect(id)
        LOCAL_SS = FIREBASE_GLOBAL_VAR.SLIST["SS" + id]
        LOCAL_SS.write(b"PATCH /" + PATH + b".json HTTP/1.0\r\n")
        response = LOCAL_SS.read()  # Read the response from Firebase
        LOCAL_SS.write(b"Host: " + FIREBASE_GLOBAL_VAR.GLOBAL_URL_ADINFO["host"] + b"\r\n")
        LOCAL_SS.write(b"Content-Length: " + str(len(DATATAG)) + b"\r\n\r\n")
        LOCAL_SS.write(DATATAG)
        response = LOCAL_SS.read()  # Read the response from Firebase
        print(f"Response from Firebase (PATCH): {response}")  # Print the response
        LOCAL_DUMMY = response
        del LOCAL_DUMMY
        INTERNAL.disconnect(id)
        if cb:
            cb()

    def get(PATH, DUMP, id, cb, limit):
        INTERNAL.connect(id)
        LOCAL_SS = FIREBASE_GLOBAL_VAR.SLIST["SS" + id]
        LOCAL_SS.write(b"GET /" + PATH + b".json?shallow=" + ujson.dumps(limit) + b" HTTP/1.0\r\n")
        LOCAL_SS.write(b"Host: " + FIREBASE_GLOBAL_VAR.GLOBAL_URL_ADINFO["host"] + b"\r\n\r\n")
        response = LOCAL_SS.read()  # Read the response from Firebase
        print(f"Response from Firebase (GET): {response}")  # Print the response
        LOCAL_OUTPUT = ujson.loads(response.splitlines()[-1])
        INTERNAL.disconnect(id)
        globals()[DUMP] = LOCAL_OUTPUT
        if cb:
            cb()

def setURL(url):
    FIREBASE_GLOBAL_VAR.GLOBAL_URL = url
    try:
        proto, dummy, host, path = url.split("/", 3)
    except ValueError:
        proto, dummy, host = url.split("/", 2)
        path = ""
    if proto == "http:":
        port = 80
    elif proto == "https:":
        port = 443
    else:
        raise ValueError("Unsupported protocol: " + proto)

    if ":" in host:
        host, port = host.split(":", 1)
        port = int(port)

    FIREBASE_GLOBAL_VAR.GLOBAL_URL_ADINFO = {"proto": proto, "host": host, "port": port}

def put(PATH, DATA, id=0, cb=None):
    INTERNAL.put(PATH, ujson.dumps(DATA), str(id), cb)

def patch(PATH, DATATAG, id=0, cb=None):
    INTERNAL.patch(PATH, ujson.dumps(DATATAG), str(id), cb)

def get(PATH, DUMP, id=0, cb=None, limit=False):
    INTERNAL.get(PATH, DUMP, str(id), cb, limit)

def delete(PATH, id=0, cb=None):
    INTERNAL.delete(PATH, str(id), cb)

def addto(PATH, DATA, DUMP=None, id=0, cb=None):
    INTERNAL.addto(PATH, ujson.dumps(DATA), DUMP, str(id), cb)
