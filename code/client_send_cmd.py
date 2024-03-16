from client import Client

client = Client(url_1='http://192.168.43.176:80/receiveData', record_file='./command_record/command_out.csv', record=True)
if __name__ == '__main__':
    print('Starting keyboard listener ...')
    client.start_listener()