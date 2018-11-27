import random
import requests
import socket

def test_connect():
    print("\nTesting connecting to the server")
    try:
        s = socket.socket()
        s.connect(("localhost", 9000))
        print("Connection attempt succeeded.")
        return None
    except socket.error:
        return "Server didn't answer on localhost port 9000. Is it running?"

def test_GET():
    print("Testing GET request.")
    uri = "http://localhost:9000/"
    try:
        r = requests.get(uri)
    except requests.RequestException as e:
        return ("Couldn't communicate with the server, {{}}\n If it's running, take a look at its output.").format(e)
    if r.status_code == 501:
        return (
            "The server returned status code 501 Not Implemented.\n This means it doesn't know how to handle a GET request.\n(is the correct server code running?)")
    elif r.status_code != 200:
        return ("The server returned status code {} instead of a 200 OK").format(r.status_code)
    elif not (str(r.headers['Content-type'])).startswith('text/html'):
        return (
            "The server didn't return Content-type: text/html.")
    elif '<title>Message Board</title>' not in r.text:
        return ("The server didn't return the form text I expected.")
    else:
        print("GET request succeeded.")
        return None

def test_POST():
    print("Testing POST request.")
    mesg = random.choice(["Hi there!", "Hello!", "Greetings!"])
    uri = "http://localhost:9000/"
    try:
        r = requests.post(uri, data={'message': mesg})
    except requests.RequestException as e:
        return ("Couldn't communicate with the server, {{}}\n If it's running, take a look at its output.").format(e)
    if r.status_code == 501:
        return (
            "The server returned status code 501 Not Implemented.\n This means it doesn't know how to handle a POST request.\n(is the correct server code running?)")
    elif r.status_code != 200:
        return ("The server returned status code {} instead of a 200 OK").format(r.status_code)
    elif r.text != mesg:
        return (
            "The server sent a 200 OK response, but the content differed.\n I expected '{}' but it sent '{}'").format(
            mesg, r.text)
    else:
        print("POST request succeeded.")
        return None

def test_POST_303():
    print("Testing POST request, looking for redirect")
    mesg = random.choice(["Hi there!", "Hello!", "Greetings!"])
    uri = "http://localhost:9000/"
    try:
        r = requests.post(uri, data={'message': mesg}, allow_redirects=False)
    except requests.RequestException as e:
        return ("Couldn't communicate with the server, {{}}\n If it's running, take a look at its output.").format(e)
    if r.status_code == 501:
        return (
            "The server returned status code 501 Not Implemented.\n This means it doesn't know how to handle a POST request.\n(is the correct server code running?)")
    elif r.status_code != 303:
        return ("The server returned status code {} instead of a 200 OK").format(r.status_code)
    elif r.headers['location']!='/':
        return (
            "The server sent a 303 redirect to the wrong location.\n I expected '/' but it sent '{}'").format(
            r.headers['location'])
    else:
        print("POST request succeeded.")
        return None

def test_memory():
    print('Testing whether messageboard saves messages')
    uri = "http://localhost:9000"
    mesg = random.choice(["Remember me!", "Don't forget", "You know me."])
    r = requests.post(uri, data={'message': mesg})
    if r.status_code != 200:
         return ("Got status oode {} instread of 200 on Post-Redirect-Get").format(r.status_code)
    elif mesg not in r.text:
         return ("I posted a message but it didn't show up.\n Expected '{}' to appear, but got this output instead\n '{}'").format(mesg, r.text)
    else:
         print("Post-Redirect-Get succeeded and I saw my message!")

if __name__ == '__main__':
    tests = [test_connect, test_POST_303, test_GET, test_memory]
    for test in tests:
        problem = test()
        if problem is not None:
            print(problem)
            break
    if not problem:
        print("All test succeeded!")
