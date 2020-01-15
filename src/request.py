import socketserver
import binascii
from proto import updater_pb2

from os import listdir
from os.path import isfile, join

def chunked(size, source):
    for i in range(0, len(source), size):
        yield source[i:i+size]

class RequestHandler(socketserver.BaseRequestHandler):
    def __init__(self, request, client_address, server):
        self.client_address = client_address
        print('Handling new request from %s' % self.client_address[0])
        super().__init__(request, client_address, server)

    def read_data(self, how_much):
        data = self.request.recv(how_much)
        if data == b'':
            print("socket connection with %s broken" % self.client_address[0])
            return False
        return data

    def send_message(self, message):
        data = message.SerializeToString()
        data = bytes([len(data)]) + data
        self.request.sendall(data)

    def get_latest_rom(self):
        roms = [f for f in listdir('/binaries/') if isfile(join('/binaries/', f))]
        roms.sort(key=lambda s: list(map(int, s.replace('.bin', '').split('.'))))
        if len(roms) > 0:
            return roms[-1]
        else:
            return None

    def get_rom_chunks(self, rom):
        chunks = []
        with open(join('/binaries/', rom), 'rb') as f:
            ba = bytearray(f.read())
            chunks = list(chunked(64, ba))
        return chunks

    def handle(self):
        packet_size_data = self.read_data(1)
        if not packet_size_data:
            return

        packet_size = int.from_bytes(packet_size_data, 'big')
        print ('parsing %d bytes long payload' % packet_size)
        payload = self.read_data(packet_size)
        print ('received %s' % payload)

        if not payload:
            return

        chunx_message = updater_pb2.FChunxMessage()
        chunx_message.ParseFromString(payload)


        if chunx_message.MessageType == 1:
            print ('version request')
            rom = self.get_latest_rom()
            if rom == None:
                chunx_message.Version.VersionString = ''
            else:
                chunx_message.Version.VersionString = rom.replace('.bin', '')
            self.send_message(chunx_message)
        if chunx_message.MessageType == 2:
            print ('updated rom request')
            rom = self.get_latest_rom()
            if rom == None:
                print ('No rom available')
            else:
                chunks = self.get_rom_chunks(rom)
                num_chunks = len(chunks)
                current_chunk_id = 1
                for chunk in chunks:
                    chunx_message.UpdateBinary.RomChunk = bytes(chunk)
                    chunx_message.UpdateBinary.ChunkId = current_chunk_id
                    chunx_message.UpdateBinary.ChunkMax = num_chunks
                    self.send_message(chunx_message)
                    current_chunk_id = current_chunk_id + 1
            #chunx_message.UpdateBinary.Rom = b'SomeTrashData'
        
    def finish(self):
        self.request.close()