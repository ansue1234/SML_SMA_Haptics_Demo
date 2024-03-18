from client import Client

ip = '192.168.43.176'
client = Client(url_1='http://' + ip + ':80/receiveData', record_file='./command_record/command_out.csv', record=True)
# client = Client(url_1='http://localhost:80', record_file='./command_record/command_out.csv', record=True)

if __name__ == '__main__':
    print('Starting keyboard listener ...')
    client.start_listener()