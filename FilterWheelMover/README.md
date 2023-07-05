# FILTER WHEEL MOVER

This repo contains the code required to remotely move the SBIG AFW-10 filter wheel connected to the Stone Edge 0.5m telescope.  It contains the server side code that runs on an Intel NUC running Windows 10, which controls the filter wheel via a serial port, and the client side code that can be run on any computer which has Python installed on it.  The server side is written in C#, and requires the .NET framework to be installed on the server computer, along with Visual Studio.  This should be all shipped with the NUC, and should work out of the box.  The client and server communicate via TCP/IP.

## Installation

### Server Side
Installation on the server side requires a machine running Windows.  The server also requires the .NET framework to be installed (recommended is 4.8.0).  You must also have the SBIG USB to Filter Wheel driver installed on your server, along with the additional ASCOM software that is required for the driver to run properly.  Beyond that, the server ships with all necessary .dll files to work out of the box.

### Client Side
The client side simply requires python to run.  No additional packages are needed.  We recommend a fresh environment in anaconda, which can be created by running the following command in the anaconda prompt:
```
conda create -n <env_name> 
```
Followed by:
```
conda activate <env_name>
```
## Server Side
The server side finds the InterNetwork adapter (the adapter which allows communication over a network) and opens a socket on the port specified in the config file (default port is 8080).  If no network adapter is found, it will use the address 127.0.0.1, which is just the default loopback address.  No external computer will be able to communicate with the NUC in this case.  The server will then wait for a connection from a client.  Once a connection is established, the server will wait for a command from the client.  The server will then execute the command, and send a response back to the client, after which, the client is disconnected.  The server will then wait for another connection.  The server will continue to do this until it is closed, either on the NUC directly, or via the client sending the command "server_shutdown" to the server.

### Server Config
The server has an associated config file called config.ini.  This file has parameters grouped under different headings.

#### Server
- Address: The address the server will listen on.  Default value is the loopback address (127.0.0.1), but the server will only use this address after checking all network adapters for an InterNetwork adapter.  If no InterNetwork adapter is found, the server will use the loopback address.
- Port: The port the server will listen on.  Default value is 8080.
- Check Adapters: If set to true, the server will check all network adapters for an InterNetwork adapter.  If one is found, the server will use the address of that adapter.  If no InterNetwork adapter is found, the server will use the address that is set in the config file.  If this is set to false, the program will automatically use the address set in the config file, and will not check for an InterNetwork adapter.  You should only want to set this to false if you have changed the address in the config file to something other than the loopback address.

#### Other
- Timeout: The amount of time the server will wait for a response from the filter wheel before timing out.  Default value is 60 seconds.
Beware that the filter wheel takes some time to set the correct position, so you should not make this value too low.
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
```
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