using System;
using System.Net.Sockets;
using System.Text;

class Client
{
    //Global variables
    NetworkStream stream;
    TcpClient client;
    int initSocket()
    {
        /* This method initializes a client socket that can connect to the socket on the server
	     *  side and send it commands.
	     *  Args:
	     *  None
	     *  Returns:
	     *  int: 0 if success, 1 if failure
	     */
        //Define the server address.  TODO: Add a config file to specify port number and IP Address
        string serverIP = "127.0.0.1";
        int serverPort = 12345;

        try
        {
            // Create a TCP client and connect to the server
            client = new TcpClient(serverIP, serverPort);
            Console.WriteLine("Connected to server.");
        }
        catch (Exception ex)
        {
            Console.WriteLine("Error while connecting to the server: " + ex.Message);
            return 1;
        }

        try
        {
            // Get the network stream for reading and writing
            stream = client.GetStream();
        }
        catch (Exception ex)
        {
            Console.WriteLine("Error getting the network stream: " + ex.Message);
            return 1;
        }
        return 0;
    }

    int sendAndReceive()
    {
        /*This method sends get and set commands to the server.
        * It prints received messages to the terminal.
        * Read the README.md for command syntax.
        * Args:
        * None
        * Returns:
        * int: 0 if success, 1 if failure
        */

        while (true)
        {
            Console.WriteLine("Enter a string to send (or 'quit' to quit): ");
            string message = Console.ReadLine();

            if (message == "quit")
                break; //End program- server will automatically close its socket too

            try
            {
                //Send the string to the server
                byte[] data = Encoding.UTF8.GetBytes(message);
                stream.Write(data, 0, data.Length);

                // Receive data from the server
                data = new byte[1024];
                int bytesRead = stream.Read(data, 0, data.Length);
                string response = Encoding.UTF8.GetString(data, 0, bytesRead);
                Console.WriteLine("Received: " + response);
            }
            catch (Exception ex)
            {
                Console.WriteLine("Error while sending/ receiving data: " + ex.Message);
                return 1;
            }
        }

        // Close the connection and stream
        stream.Close();
        client.Close();
        Console.WriteLine("Connection closed.");
        return 0;
    }

    static void Main(string[] args)
    {
        /* Main method to drive initialization of socket and then send and receive messages
	     * Args:
	     * None
	     * Returns:
	     * int: 0 for success, 1 for failure
	     */

        int ret_val = 0;
        Client client= new Client();
        //Initialize the socket
        ret_val = client.initSocket();
        if (ret_val == 1)
        {
            //Socket did not initialize properly
            Environment.Exit(1);
        }
        //Send commands and receive strings
        ret_val = client.sendAndReceive();
        if (ret_val == 1)
        {
            //Something went wrong in sendAndReceive()
            Environment.Exit(1);
        }
    }
}