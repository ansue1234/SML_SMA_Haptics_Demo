import requests
import pandas as pd
from pynput.keyboard import Key, Listener

class Client:
    def __init__(self, url_1, url_2=None, record_file='commands.csv', record=False):
        self.url_1 = url_1
        self.url_2 = url_2
        self.record_file = record_file
        self.record = record
        self.record_df = pd.DataFrame(columns=['TimeStamp', 'Command', 'Response'])

    def send_post(self, data):
        try:
            current_time = pd.Timestamp.now()
            response_1 = requests.post(self.url_1, data={'data': data})
            print(f'Successfully sent {data} device 1. Server response: {response_1.text}')
            if self.url_2:
                response_2 = requests.post(self.url_2, data={'data': data})
                print(f'Successfully sent {data} device 2. Server response: {response_2.text}')
            if self.record:
                self.record_df[len(self.record_df)] = [current_time, data, response_1.text]
                self.record_df.to_csv(self.record_file, index=False) 
        except requests.exceptions.RequestException as e:
            print(f'Request failed: {e}')

    def on_press(self, key):
        if key == Key.esc:
            # Stop listener
            return False
        elif hasattr(key, 'char'):  # Check if the key press is a character
            if key.char == 'w':
                self.send_post('w')
            elif key.char == 'a':
                self.send_post('a')
            elif key.char == 's':
                self.send_post('s')
            elif key.char == 'd':
                self.send_post('d')
            elif key.char == 'j':
                self.send_post('j') # rotate counter-clockwise
            elif key.char == 'k':
                self.send_post('k') # rotate clockwise
            elif key.char == 'r':
                self.send_post('r') # orthogonal stop

    def start_listener(self):
        with Listener(on_press=self.on_press) as listener:
            listener.join()