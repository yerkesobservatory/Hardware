# FILTER WHEEL MOVER

This repo contains the code required to remotely move the SBIG AFW-10 filter wheel connected to the Stone Edge 0.5m telescope.  It contains the server side code that runs on an Intel NUC running Windows 10, which controls the filter wheel via a serial port, and the client side code that can be run on any computer which has Python installed on it.  The server side is written in C#, and requires the .NET framework to be installed on the server computer, along with Visual Studio.  This should be all shipped with the NUC, and should work out of the box.  The client and server communicate via TCP/IP.

## Installation

### Server Side
Installation on the server side requires a machine running Windows.  The server also requires the .NET framework to be installed (recommended is 4.7.2).  You must also have the SBIG USB to Filter Wheel driver installed on your server, along with the additional ASCOM software that is required for the driver to run properly.  Beyond that, the server ships with all the necessary dependencies.

Set up for the server is slightly involved as it requires us to create a Windows service and set up the firewall correctly.  The following steps should be followed to set up the server:

- Download the package from GitHub.  Alternatively, download the necessary files from the Google Drive folder in SEO.

- Open the config.ini file in the Server folder and modify it as per your liking (options are given in the section below in this file).  By default, the application will query all network adapters and open a port on 8080 on the outgoing adapter.  If it cannot find the outgoing adapter, it will default to 127.0.0.1 (the loopback address).

- Open a command prompt with administrator privileges.

- In the command prompt, execute the following command:
```
sc.exe create <service name> binPath= "<path to exe>" start= auto
```
Ensure you give the full path name, ending in FWMover_Service.exe.  Close your command prompt after that.

- Go to the start menu and search for "Services".  Open the Services application.  Find the service you just created, right click on it, and select "Properties".  Check in the "General" tab that the "Startup type" is set to "Automatic".  If it is not, change it to "Automatic". 

- Then go to the "Recovery" tab and chose what will happen if the service crashes.  We recommend setting all three options to "Restart the Service", and leaving "Restart Service After" to 1 minute.  Click "Apply" and then "OK".

- Now right click on the service again, and select "Start".  The service should now be running, which you will see in the status column.

- Now go to your advanced firewall settings.  Click on the option to make an inbound rule.  Select the "custom" option. Then when asked to select a program, select "All services".  Then, on the Protocol and Ports page, first select TCP under "Protocol Type", and then select the port on which the socket is to be opened.  If you did not modify the config file, this is 8080.

- On the "Scope" page, in remote IP addresses, switch to "These IP Addresses" and add the address of the client if you only have one client (in the case of SEO, this is Aster's outgoing IP address).  Then click "Next".

- On the "Action" page, select "Allow the connection".  Then click "Next".

- On the "Profile" page, select all three options.  Then click "Next".

- Give the rule a suitable name and close the window.

- Test the program by running the client side code from the computer that was added to the firewall.  If the program does not work, check the log file in the Server folder for any errors.
### Client Side
The client side simply requires python to run.  No additional packages are needed.  
## Server Side
The server side finds the InterNetwork adapter (the adapter which allows communication over a network) and opens a socket on the port specified in the config file (default port is 8080).  If no network adapter is found, it will use the address 127.0.0.1, which is just the default loopback address.  No external computer will be able to communicate with the NUC in this case.  The server will then wait for a connection from a client.  Once a connection is established, the server will wait for a command from the client.  The server will then execute the command, and send a response back to the client, after which, the client is disconnected.  The server will then wait for another connection.  The server will continue to do this until it is closed, either on the NUC directly, or via the client sending the command "server_shutdown" to the server.  The first time the program is run on a new network, Windows Firewall may ask for permission to allow the program to communicate over the network, but after that the program can be set to auto-start on boot.  This means that only for initial set-up a mouse and monitor are required. 

### Server Config
The server has an associated config file called config.ini.  This file has parameters grouped under different headings.

#### Server
- Address: The address the server will listen on.  Default value is the loopback address (127.0.0.1), but the server will only use this address after checking all network adapters for an InterNetwork adapter.  If no InterNetwork adapter is found, the server will use the loopback address.
- Port: The port the server will listen on.  Default value is 8080.
- Check Adapters: If set to true, the server will check all network adapters for an InterNetwork adapter.  If one is found, the server will use the address of that adapter.  If no InterNetwork adapter is found, the server will use the address that is set in the config file.  If this is set to false, the program will automatically use the address set in the config file, and will not check for an InterNetwork adapter.  You should only want to set this to false if you have changed the address in the config file to something other than the loopback address.

#### Other
- Timeout: The amount of time the server will wait for a response from the filter wheel before timing out.  Default value is 60 seconds.
Beware that the filter wheel takes some time to set the correct position, so you should not make this value too low.
- LogFile: The location at which the log file will be generated.  Please use \ when specifying paths.  Eg: LogFile\Path\Here\log.txt
- MaxLines;  The maximum number of lines the log file can have before it is cleared.  Default value is 5000.
- List (optional):  A comma separated list of the names of your filters.  The default config does not have this, but you can add it by adding a line below "Timeout".  If you have 10 filters named a to j, you would add a line that looks like this:
List = a,b,c,d,e,f,g,h,i,j
If you do not provide a list, the server will use the names provided to ASCOM when the wheel was being set up.  If you do provide a list, the server will use the names in the list, and will ignore the names provided to ASCOM.  The names in the list must be comma separated, and must be in the same order as the filters are in the wheel.

## Client Side
The client side code is contained in the file "fw_mover_client.py".  The client side code is a command line program, and can be run from the command line.  

- get: Retrieves the filter wheel position from the server.

- set \<number\>: Sets data on the server. Replace \<number\> with an actual number.

- filter_list: Prints the filter wheel positions and their corresponding filter names.

- help: Prints a list of commands and their descriptions.

- server_shutdown: Shuts down the server.  ONLY USE THIS IF YOU KNOW WHAT YOU'RE DOING.

Usage: 

```bash
python/ python3 fw_mover_client.py \<command\> [\<number\>] [<server_address>] [<server_port>]
```

### Client Config
The client side ships with a config file by default, but it is not required.  The config file should be called fw_mover_client_config.ini, and 
should be in the same directory as the client code.  The config file has parameters grouped under different headings.

#### Server
- Address: The address of the serverm (used when the optional parameter server_address is left blank).  Default value if the config is missing is the loopback address (127.0.0.1).  If the server address is provided as an argument at run-time, the program will use that instead of the address in the config file.
- Port: The port the server is listening on (used when the optional parameter server_port is left blank).  Default value if the config is missing is 8080. If the server port is provided as an argument at run-time, the program will use that instead of the port in the config file.

#### Other
Timeout: The amount of time the client will wait for a response from the server before timing out.  Default value if the config is missing is 60 seconds.