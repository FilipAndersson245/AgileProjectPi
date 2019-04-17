import requests

def clientsidePost():
    payload = 'Testing bitch'
    r = requests.post('http://127.0.0.1:60006', data=payload)
    print('Post send:\n')
    print(r.text)

#clientsidePost()
