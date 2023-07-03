"""
Usage: python fw_mover_client.py <command> [<number>] [<server_address>] [<server_port>]

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

    - server_shutdown: Shuts down the server.  ONLY USE THIS IF YOU KNOW WHAT YOU'RE DOING.
"""
import logging
import socket
import sys

# Configure logging 
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("fw_mover_client.log"),  # Log file handler
        logging.StreamHandler()  # Console handler
    ]
)
logger = logging.getLogger(__name__)
def send_message(server_address, server_port, message):
    # Create a socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Set the timeout to 1 minute
    sock.settimeout(60)
    try:
        # Connect to the server
        sock.connect((server_address, server_port))

        # Send the message to the server
        sock.sendall(message.encode('utf-8'))
        logger.info(f"Sent command: {message}")  # Log the command

        # Set the timeout to 1 minute
        sock.settimeout(60)

        # Receive and print the server's response
        response = sock.recv(1024)
        logger.info(f"Server response: {response.decode('utf-8')}")

        # Keep the program running until a response is received or timeout occurs
        while not response:
            try:
                response = sock.recv(1024)
            except socket.timeout:
                logger.warning("Timeout occurred. No response received.")
                break

    except Exception as ex:
        logger.error(f"Error: {str(ex)}")

    finally:
        # Close the socket
        sock.close()

def print_help():
    print("Available commands:")
    print("get - Gets the current filter wheel position.")
    print("set <number> - Sets the filter wheel position to the given number.  Replace <number> with an actual number.")
    print("server_shutdown - Shuts down the server.")
    print("\nUsage: python fw_mover_client.py <command> [<number>] [<server_address>] [<server_port>]")

# Get the server address, port, and message from the command line arguments
if len(sys.argv) < 2 or sys.argv[1] == "help":
    print_help()
    sys.exit(0)

MESSAGE = sys.argv[1]
NUMBER = None

# Set default values for server address and port
SERVER_ADDRESS = 'localhost'
SERVER_PORT = 8080

# Deal with the set command first, then all others due to the extra parameter
if MESSAGE == "set":

    if len(sys.argv) < 3: 
        # You need at least 3 arguments- fw_mover_client.py, set, and a number
        logger.error("Too few arguments provided.")
        logger.info("Usage: python fw_mover_client.py set <number> [<server_address>] [<server_port>]")
        sys.exit(1)

    try:
        NUMBER = int(sys.argv[2])
    except ValueError:
        # You need the last argument to be a number in this case
        logger.error("Invalid number provided with 'set' command.")
        sys.exit(1)
    
    if len(sys.argv) == 3:
        # Use the default server address and server port values
        send_message(SERVER_ADDRESS, SERVER_PORT, f"{MESSAGE} {NUMBER}")

    if len(sys.argv) == 4:
        # Use the default port values but change the address to what has been provided
        SERVER_ADDRESS = sys.argv[3]
        send_message(SERVER_ADDRESS, SERVER_PORT, f"{MESSAGE} {NUMBER}")

    if len(sys.argv) == 5:
        # Use the custom port and address values
        SERVER_ADDRESS = sys.argv[3]
        SERVER_PORT = int(sys.argv[4])
        send_message(SERVER_ADDRESS, SERVER_PORT, f"{MESSAGE} {NUMBER}")

    if len(sys.argv) > 5:
        logger.error("Too many arguments provided.")
        logger.info("Usage: python fw_mover_client.py set <number> [<server_address>] [<server_port>]")
        sys.exit(1)
    
# Deal with all other commands
else:

    if len(sys.argv) < 2:
        # You only need 2 arguments if the argument is not 'set"
        logger.error("Too few arguments provided.")
        logger.info("Usage: python fw_mover_client.py <command> [<server_address>] [<server_port>]")
        sys.exit(1)

    if len(sys.argv) == 2:
        # Use the default server address and port
        send_message(SERVER_ADDRESS, SERVER_PORT, MESSAGE)

    if len(sys.argv) == 3:
        # Use the default port but change the address
        SERVER_ADDRESS = sys.argv[2]
        send_message(SERVER_ADDRESS, SERVER_PORT, MESSAGE)

    if len(sys.argv) == 4:
        # Change both the port and the address
        SERVER_ADDRESS = sys.argv[2]
        SERVER_PORT = int(sys.argv[3])
        send_message(SERVER_ADDRESS, SERVER_PORT, MESSAGE)

    if len(sys.argv) > 4:
        logger.error("Too many arguments provided.")
        logger.info("Usage: python fw_mover_client.py <command> [<server_address>] [<server_port>]")
        sys.exit(1)

