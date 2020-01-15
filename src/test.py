import socket
import sys
from proto import updater_pb2

def connect_to_server():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((socket.gethostbyname('updater'), 6684))
    return client

def print_message():
    print('Printing message structure')
    message = updater_pb2.FChunxMessage()
    message.MessageType = 1
    message.Version.VersionString = "1.2.3"
    print(message)
    message.MessageType = 2
    message.UpdateBinary.RomChunk = b'0x00'
    print(message)

def request_version():
    print('Printing latest version')
    message = updater_pb2.FChunxMessage()
    message.MessageType = 1
    client = connect_to_server()
    data = bytearray(message.SerializeToString())
    data = bytes([len(data)]) + data
    client.sendall(data)
    print('Waiting for reply...')
    size = int.from_bytes(client.recv(1), 'big')
    if size == 0:
        print('No data received')
        return
    else:
        print('Parsing %d bytes' % size)
    message.ParseFromString(client.recv(size))
    print('Received version %s' % message.Version.VersionString)
    client.close()

def request_rom():
    message = updater_pb2.FChunxMessage()
    message.MessageType = 2
    client = connect_to_server()
    data = bytearray(message.SerializeToString())
    data = bytes([len(data)]) + data
    client.sendall(data)
    print('Waiting for reply...')
    while True:
        size = int.from_bytes(client.recv(1), 'big')
        if size == 0:
            print('No data received')
            break
        message.ParseFromString(client.recv(size))
        sys.stdout.write("\rGot chunk %i/%i" % (message.UpdateBinary.ChunkId, message.UpdateBinary.ChunkMax))
        sys.stdout.flush()
        if message.UpdateBinary.ChunkId == message.UpdateBinary.ChunkMax:
            break
    print ('')
    print ('done')
    client.close()

print_message()
request_version()
request_rom()