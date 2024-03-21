import pandas as pd
from client import Client
import time

ip = '192.168.43.176'
url = 'http://' + ip + ':80/receiveData'
fname = '../painting_alignment/command_record/commands_ painting.csv'
# url = 'http://localhost:80'
client = Client(url)

df_command = pd.read_csv(fname)
df_command['TimeStamp'] = pd.to_datetime(df_command['TimeStamp']).fillna(0)
time_diff = (df_command['TimeStamp'].diff().dt.total_seconds() * 10**3).fillna(0)
time_diff = pd.concat([time_diff, pd.Series([0])], ignore_index=True).to_numpy()
df_command['TimeDiff'] = time_diff[1:]
print(df_command[['TimeDiff', 'Command']])

for index, row in df_command.iterrows():
    client.send_post(row['Command'])
    print(f'Sent command {row["Command"]}, waiting for {row["TimeDiff"]/1000} seconds ...')
    time.sleep(row['TimeDiff']/1000)