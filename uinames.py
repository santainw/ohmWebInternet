import requests

def SampleRecord():
    r = requests.get("http://uinames.com/api?ext&region=United%20States", timeout=2.0)

    return "My name is {} {} and the PIN on my card is {} ".format(r.json()['name'], r.json()['surname'], r.json()['credit_card']['pin'])

if __name__=='__main__':
    print(SampleRecord())