"""
Usage: python client.py <command> [<number>] [<server_address>] [<server_port>]

This script connects to the intel NUC which controls the filter wheel 
and sends commands along with optional arguments.

Arguments:
    <command>: The command to be executed on the server.
        Available commands: get, set, quit, server shutdown

    <number>: (Optional) Only applicable to the 'set' command.  Sets the filter wheel to the specified number.

    <server_address>: (Optional) The IP address or hostname of the server. Default is 10.150.150.84, which is 
    the IP address of the intel NUC when this script was being written in the MIELab.

    <server_port>: (Optional) The port number of the server. Default is 12345.

Commands:
    - get: Retrieves the filter wheel position from the server.

    - filters: Prints the filter wheel positions and their corresponding filter names.

    - set <number>: Sets data on the server. Replace <number> with an actual number.

    - server shutdown: Shuts down the server.  ONLY USE THIS IF YOU KNOW WHAT YOU'RE DOING.
"""

import socket
import sys

def send_message(server_address, server_port, message):
    # Create a socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # Connect to the server
        sock.connect((server_address, server_port))

        # Send the message to the server
        sock.sendall(message.encode('utf-8'))

        # Set the timeout to 1 minute
        sock.settimeout(60)

        # Receive and print the server's response
        response = sock.recv(1024)
        print(f"Server response: {response.decode('utf-8')}")

        # Keep the program running until a response is received or timeout occurs
        while not response:
            try:
                response = sock.recv(1024)
            except socket.timeout:
                print("Timeout occurred. No response received.")
                break

    except Exception as ex:
        print(f"Error: {str(ex)}")

    finally:
        # Close the socket
        sock.close()

def print_help():
    print("Available commands:")
    print("get - Gets the current filter wheel position.")
    print("set <number> - Sets the filter wheel position to the given number.  Replace <number> with an actual number.")
    print("server shutdown - Shuts down the server.")
    print("\nUsage: python client.py <command> [<number>] [<server_address>] [<server_port>]")

# Get the server address, port, and message from the command line arguments
if len(sys.argv) < 2 or sys.argv[1] == "help":
    print_help()
    sys.exit(0)

MESSAGE = sys.argv[1]
NUMBER = None

# Ensure number is provided for "set" command
if MESSAGE == "set":
    if len(sys.argv) < 3:
        print("Usage: python client.py set <number> [<server_address>] [<server_port>]")
        sys.exit(1)

    try:
        NUMBER = int(sys.argv[2])
    except ValueError:
        print("Invalid number provided with 'set' command.")
        sys.exit(1)

# Set default values for server address and port
SERVER_ADDRESS = 'localhost'
SERVER_PORT = 8080

# Override default values if provided as command line arguments
if len(sys.argv) > 3:
    SERVER_ADDRESS = sys.argv[3]
if len(sys.argv) > 4:
    SERVER_PORT = int(sys.argv[4])

# Send the message to the server
send_message(SERVER_ADDRESS, SERVER_PORT, MESSAGE)
