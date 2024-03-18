# SMA Haptic Demo

This repository contains all the code necessary for the two demostration for the SMA Haptics project--Painting Alignment and Object Detection.

## Setup 

### Hardware Required
- 1x 3.7V Lipo Battery
- 1x 3.3V USB to TTL Converter (i.e. DSDTECH SH-U09C5) 
- 1x LAN, could be from a router, could be from a phone hot spot 

### Software
#### Python Scripts
1. Get [Anaconda](https://www.anaconda.com/download) for your system
2. Make sure to install [Git](https://git-scm.com/download/win)(This is for Windows)
3. Open Anaconda Prompt
4. If you haven't done so, find a place fitting to download this repository and do `git clone https://github.com/ansue1234/SML_SMA_Haptics_Demo.git`
5. Navigate to the location of this repository, e.g. `cd SML_SMA_Haptics_Demo`
6. `conda env create -f environment.yml`

### Arduino
#### IDE Setup
1. Make sure you install the VCP driver for your USB to TTL converter. For DSDTECH SH-U09C5, install FTDI VCP driver from [here](https://ftdichip.com/drivers/vcp-drivers/)
2. Get the suite of ESP32 boards from the Arduino IDE. In the IDE:
   1. Tools -> Boards -> Board Manager -> Search for esp32 by Espressif Systems -> Install
3. Get ESPAsyncWebSrv library:
   1. Tools -> Manage Libraries -> Search for ESPAsyncWebSrv by dvarrel -> Install
4. Open `code.ino`, located in the `code` directory in this repository in the Arduino IDE
5. Turn on your phone hot spot or start your router
6. On line 7 and 8 of `code.ino` under the comments `//Network Setup`, fill in your network credientials
7. Upload code to the board

#### Upload Code to Board
1. Power up the board, either through battery or power supply at 4.2V
2. In the Arduino IDE, select the `ESP32-WROOM-DA Module` as the board and leave everything else as default, then select the right port. 
3. Turn on the Serial Monitor and set the baud rate to 115200
4. Connect the Ground, TX and RX Wires to the GND TX RX labeled headers on the board. 
   - Note: Due to mistake in labeling, connect TX Header to TX wire of the USB to TTL Converter and RX header to the RX Wire. Don't connect it following the TX->RX and RX->TX convention
5. Short the pads that says `EN` to reset, if all goes well, you should see a message with "Power boot" or something similar in the Serial Monitor
    - Note: Make sure to disconnect all peripherals connected to the board when the board is resetting or uploading code, otherwise peripherals can potientially be damaged.  
6. While shorting the `EN` pads, short the `PRG` Pads to put the ESP 32 Chip into programming mode, you should see "Waiting for download" in the Serial Monitor, you can then release the `EN` pads
7. While shorting the `PRG` Pads, press upload on the Arduino IDE:
   - Try to short the `PRG` pads until upload is finished with the message "Hardware Reset"
8. Short `EN` pads again to reset board.
   - After waiting for a few seconds after the board is finished setting up
9. In the Serial montor, if the board connects to wifi, it would output the board's **IP Address**. Take note of it.
    
#### Comments:
- The green LED denotes whether the board is powered. It turns on if the board is powered.
- The red LED denotes whether the battery needs to be exchanged or not. If the red LED is on, please change the battery

## Running the Painting Alignment Demo
1. Navigate to `painting_alignment`
2. On line 11 of `alignment.py` change the `ip` variable to the ip address of the board
3. On line 12 of `alignment.py` change the `camera` variable to 0 if you are using the laptop's internal camera or 1 for an externally connected camera.
4. `python alignment.py` in Anaconda Prompt
5. Once you see the view of the web cam, you can hold and drag LMB (left mouse button) to draw the desired position of the painting.
6. Press d to start painting detection and then press s to start sending computed command to the haptic device
7. Press q to quit and end the program
   
## Running the Object Detection Demo
1. Navigate to `object_detection`
2. On line 11 of `detect.py` change the `ip` variable to the ip address of the board
3. On line 12 of `detect.py` change the `camera` variable to 0 if you are using the laptop's internal camera or 1 for an externally connected camera.
4. `python detect.py` in Anaconda Prompt
   - All commands are automatically recorded in the `object_detection/command_record` 
5. Ctrl +  to quit

## Other Useful scripts
- `client_send_cmd.py`
  - `cd code`
  - Change IP address (line 3)
  - `python client_send_cmd.py`
  - This is to control the haptic via keyboard control
    - WASD (up, left, down, right)
    - JKR (Counter Clockwise, clockwise, orthogonal)
  - The script automatically logs the command you sent and the time the certain command is sent
    - Saves in `code/command_record`
- `send_record.py`
  - `cd code`
  - Change IP and filename location of the record (line 5 and 7)
  - `python send_record.py`
  - The script replays the recorded commands to the haptic. 
 