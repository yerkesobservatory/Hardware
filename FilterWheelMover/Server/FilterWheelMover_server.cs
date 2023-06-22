// See https://aka.ms/new-console-template for more information
// Console.WriteLine("Hello, World!");

using ASCOM.Common.DeviceInterfaces;
using System;
using System.Net;
using System.Net.Sockets;
using System.Text;

class FilterWheelMover_server
{
    //Global variables for this class
    IFilterWheelV2 m_FilterWheel;
    Socket socket;

    int initFW()
    {
        /* This function finds the filter wheel, which is plugged in via the USB-FW adapter, and initializes it to be used.
         *  Args:
         *  None
         *  Returns:
         *  int: 0 for success, 1 for failure
         */

         var prog_id = "ASCOM.SBIG.USB_FW.FilterWheel";

         try
         {
            // Use in-built ASCOM functionality to connect to the camera
            var chooser = new ASCOM.Com.Chooser();
            chooser.DeviceType = ASCOM.Common.DeviceTypes.FilterWheel;
            prog_id = chooser.Choose("ASCOM.SBIG.USB_FW.FilterWheel");
         }
         catch (InvalidOperationException e)
         {
            Console.WriteLine("Accessing remotely, defaulting to SBIG.USB_FW");
            return 1;
         }

         // Connect to the filter wheel
         m_FilterWheel = new ASCOM.Com.DriverAccess.FilterWheel(prog_id);
         m_FilterWheel.Connected = true;

         //Wait for filter wheel to start up, 8 seconds
         Thread.Sleep(8000);
         return 0;
    }

    int setFilterWheel(short pos)
    {
        /* Sets Filter Wheel to given position
         *  Args:
         *  int input: Position from 0-9 that has been pre-checked
         *  Returns:
         *  int: 0 for success, no other exceptions currently handled
         */

        const int FILTER_WHEEL_TIME_OUT = 10; //Fix a time out value in case of any errors
        DateTime StartTime;
        m_FilterWheel.Position = pos;
        StartTime = DateTime.Now;
        Console.Write("Setting filter wheel to position " + pos.ToString() + "...");

        do
        {
            Thread.Sleep(100);
            Console.WriteLine("Waiting...");
        } while (!(
        (m_FilterWheel.Position == pos) |
        (DateTime.Now.Subtract(StartTime).TotalSeconds > FILTER_WHEEL_TIME_OUT)));

        if (m_FilterWheel.Position != pos)
        {
            //Error setting filter wheel
            return 1;
        }
        Console.Write("\n");
        Console.WriteLine("Set position to: " + pos.ToString());
        return 0;
    }

    string parseInput(string line)
    {
        /*
         *   This function receives a line from the server side and checks for get or set command.
         *   It then sends the necessary input to the correct method.
         *   TODO: In config file, we would want to give names to position 0-9 so that get position prints out
         *   the filter name.
         *   Args:
         *   string line: String received from the server
         *   Returns:
         *   string rtn : String that will be printed on the client screen
         */
         if (line == "get")
         {
            // Get the position of the filter wheel.
            int pos = m_FilterWheel.Position;
            string rtn = "Filter Wheel Position is " + pos.ToString();
            return rtn;
         }
         else
         {
             //Parse string using space as the delimiter
             string[] words = line.Split(' ');

             //Check first token is "set"
             if (words[0] != "set")
             {
                string rtn = "Invalid input";
                return rtn;
             }
             else
             {
                string rtn;
                //Parse the number and send it to setFilterWheel()
                short pos;
                bool success = short.TryParse(words[1], out pos);
                if (success == false)
                {
                    //Not given a number
                    rtn = "Input was not a number";
                    return rtn;
                }
                if (pos > 9 || pos < 0)
                {
                    //Given an invalid number
                    rtn = "Enter a valid filter position (0-9)";
                    return rtn;
                }
                int ret_val = setFilterWheel(pos);
                if (ret_val == 1)
                {
                    string err = "Error setting filter wheel to position " + pos.ToString();
                    return err;
                }
                rtn = "Filter wheel set to position " + pos.ToString();
                return rtn;
             }
         }
    }

    int initSocket()
    {
        /*
         * Initializes socket to listen for commands.  Binds the socket to port #8080.
         * TODO: Add config file where we can specify port and IP address.
         * Args:
         * None
         * Returns:
         * int: 0 for success, 1 for failure
         */
        socket = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.Tcp);
        try
        {   
            var host = Dns.GetHostEntry(Dns.GetHostName());
            foreach (var ip in host.AddressList)
            {
                if (ip.AddressFamily == AddressFamily.InterNetwork)
                {
                    // Bind the socket to a local endpoint
                    int port = 12345;
                    IPEndPoint localEndPoint = new IPEndPoint(ip, port);
                    socket.Bind(localEndPoint);

                    //Print the IP Address for any clients to use
                    Console.WriteLine("IP Address: " + ip.ToString());
                    Console.WriteLine("Port: " + port.ToString());
                    // Start listening for incoming connections
                    socket.Listen(10);
                    Console.WriteLine("Waiting for a connection...");
                    return 0;
                }
            }
            Console.WriteLine("No network adapters with an IPv4 address in the system.  Exiting");
        }
        catch (Exception e)
        {
            Console.WriteLine("Error initializing socket.  Exiting");
            return 1;
        }
        return 0;
    }

    int receiveAndSend()
    {
        /* This method accepts incoming connections and listens for incoming strings.  Upon receiving a string, it passes the input to
         *  the parseInput() method, which runs necessary checks on it. parseInput() sends back a string that is sent to the client.
         *  Args:
         *  None
         *  Returns:
         *  int: 0 for success, 1 for failure
         */
        try
        {
            //Accept an incoming connection
            Socket clientSocket = socket.Accept();

            Console.WriteLine("Client Connected!");

            while(clientSocket.Connected)
            {
                //Receive data from the client
                byte[] buffer = new byte[4096];
                int bytesRead = clientSocket.Receive(buffer);

                //If we get 0 bytes, connection has been closed
                if (bytesRead == 0)
                {// Close the client socket to exit gracefully
                    Console.WriteLine("Client Disconnected: Waiting for New Client");
                    break;
                }
                string dataReceived = System.Text.Encoding.ASCII.GetString(buffer, 0, bytesRead);
                Console.WriteLine("Data Received: " + dataReceived);

                //If data received tells us to quit server, quit here and close
                if (dataReceived == "server_shutdown")
                {
                    //Tell the socket that the server is shutting down
                    string toSend = "Shutting down server...";

                    //Send Data back to the client
                    byte[] d2s = System.Text.Encoding.ASCII.GetBytes(toSend);
                    clientSocket.Send(d2s);

                    //Close the client Socket
                    clientSocket.Shutdown(SocketShutdown.Both);
                    clientSocket.Close();
                    // Close the server socket
                    socket.Close();
                    return 0;
                }
                //Send off input and do things with it
                string rtn = parseInput(dataReceived);

                //Send Data back to the client
                byte[] dataToSend = System.Text.Encoding.ASCII.GetBytes(rtn);
                clientSocket.Send(dataToSend);

            }
            //Close the client Socket
            clientSocket.Shutdown(SocketShutdown.Both);
            clientSocket.Close();
        }
        catch (Exception ex)
        {

            Console.WriteLine("An error occurred: " + ex.Message);
            return 1;
        }

        // Start waiting again if client closed
        int ret_val = receiveAndSend();
        return ret_val;
    }
    
    static void Main(string[] args)
    {
        /* Main method to start execution.  Initializes socket and filter wheel, then receives and sends input, then closes and cleans up.
         *  Args:
         *  string[] args: (ignore my little rant) omg I thought I was done with you nobody knows what you do 
         *  Returns:
         *  0 for success, 1 for failure.
         */
        int ret_val = 0;

        FilterWheelMover_server server = new FilterWheelMover_server();
        //Initialize Filter Wheel
        ret_val = server.initFW();
        if (ret_val == 1)
        {
            //An error occurred during Filter Wheel initialization
            Environment.Exit(1);
        }

        //Initialize socket
        ret_val = server.initSocket();
        if (ret_val == 1)
        {
            //An error occurred during socket initialization
            Environment.Exit(1);
        }

        //Receive and Send from/to  client
        ret_val = server.receiveAndSend();
        if (ret_val == 1)
        {
            //An error occurred during the receive and send process
            Environment.Exit(1);
        }
        else if (ret_val == 2)
        {
            //Wait again for connection

        }
    }
}





