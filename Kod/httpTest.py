import socket
import requests
                                                                                                                                                                      
def serversideSocket():
    sockS = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
    sockS.bind(('127.0.0.1', 60006))
    sockS.listen(1)

    print('Listening...\n')
    (sockC, addr) = sockS.accept()
    print('Connection from {}' .format(addr))

    clientData = sockC.recv(1024)
    clientDataDecoded = clientData.decode('ascii')
    print(clientDataDecoded)

    #payload = requests.

    sockC.sendall(bytearray("HTTP/1.1 200 ok\n", "ASCII"))
    sockC.sendall(bytearray("\n", "ASCII"))
    sockC.sendall(bytearray("200\n", "ASCII"))


    #r = requests.post('http://{}:{}' .format(addr[0], addr[1]) , data=payload)
    sockC.close()



serversideSocket()
