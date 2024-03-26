import requests
from pynput.keyboard import Key, Listener

# The URL where you want to send the POST requests
# ip = '192.168.43.176'
ip = '172.20.10.7'
# ip = '192.168.43.42'
url = 'http://' + ip + ':80/receiveData'
# url ='http://localhost:80'

# This function sends the HTTP POST request with the specified data
def send_post(data):
    try:
        response = requests.post(url, data={'data': data})
        print(f'Successfully sent {data}. Server response: {response.text}')
    except requests.exceptions.RequestException as e:
        print(f'Request failed: {e}')

# This function maps keyboard keys to the specific data you want to send
def on_press(key):
    if key == Key.esc:
        # Stop listener
        return False
    elif hasattr(key, 'char'):  # Check if the key press is a character
        if key.char == 'w':
            send_post('w')
        elif key.char == 'a':
            send_post('a')
        elif key.char == 's':
            send_post('s')
        elif key.char == 'd':
            send_post('d')
        elif key.char == 'j':
            send_post('j') # rotate counter-clockwise
        elif key.char == 'k':
            send_post('k') # rotate clockwise
        elif key.char == 'r':
            send_post('r') # orthogonal stop

# Starting the listener to monitor keyboard presses
print('Starting keyboard listener ...')
with Listener(on_press=on_press) as listener:
    listener.join()
