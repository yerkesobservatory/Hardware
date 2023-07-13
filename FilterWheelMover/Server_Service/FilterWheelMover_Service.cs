using ASCOM.Common.DeviceInterfaces;
using System.IO;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System.ServiceProcess;
using IniParser;
using IniParser.Model;
using System;
using System.Diagnostics;
using System.Linq;

partial class FilterWheelMoverServerService : ServiceBase
{
    //Global variables for this class
    private static StreamWriter logFile;
    IFilterWheelV2 m_FilterWheel;
    Socket socket;
    IniData configuration;
    int MAX_LINES = 5000; // Assigned dummy value that can be changed from logFile
    int logLineCount = 0;  // Assigned default value that can be changed if log file is present
    string logFileName = null;

    private void Log(string message)
    {
        /* A simple logging function that takes a message and adds it to the log file (and prints to console too).
         * Effectively just an alias for logFile.WriteLine() and Console.WriteLine()
         * Args:
         * string message:  message to be added to the log file
         * Returns:
         * None
         */
        Console.WriteLine(message);
        logFile.WriteLine(message);
        logFile.Flush();
        // Increment Log file counter and check if length is exceeded
        logLineCount++;
        CheckLogFileLineCount();
    }

    private void LogError(string message)
    {
        /* A method that causes errors to be highlighted better in the log file. 
         * Args:
         * string message:  message to be added to the log file
         * Returns:
         * None
         */
        string errorPrefix = "[ERROR] ";
        Console.WriteLine(message);
        logFile.WriteLine(errorPrefix + message);
        logFile.Flush();
        // Increment Log file counter and check if length is exceeded
        logLineCount++;
        CheckLogFileLineCount();
    }

    private void CheckLogFileLineCount()
    {
        /* Simple function that allows for easy checking of length of log file
         * to determine if it needs to be refreshed.
         * Args:
         * None
         * Returns: 
         * None
         */
        if (logLineCount >= MAX_LINES)
        {
            RefreshLogFile();
        }
    }

    private void RefreshLogFile()
    {
        /* Function to delete the old log file and start anew if the log file crosses the max amount of lines 
         * Args:
         * None
         * Returns:
         * None
         */
        // Delete the log file if it exists
        if(File.Exists(logFileName))
        {
            File.Delete(logFileName);
        }
        CreateLogFile();
        logLineCount = 0;
        Log("Log File has been refreshed");
    }
    private void CreateLogFile()
    {
        /* Method that creates a log file using the location specified in the config file, defaulting to root if necessary.
         * Also updates the max lines value, defaulting to 5000 if necessary.
         * Args:
         * None
         * Returns:
         * None
         */

        try
        {
            // Try to create a log file at the specified location before defaulting to root
            logFileName = configuration["Other"]["LogFile"];
            // Parse the logfile location
            string dir = logFileName.Substring(0, logFileName.LastIndexOf('\\'));
            //Create directory if necessary
            if (!Directory.Exists(dir))
            {
                Directory.CreateDirectory(dir);
            }
            logFile = new StreamWriter(logFileName, append: false);
        }
        catch (Exception ex)
        {
            // No valid name specified for log file
            Console.WriteLine(ex.Message);
            Console.WriteLine("Invalid Log File Name.  Log file will be created in root folder.");
        }
        if (logFileName == null)
        {
            // For some reason this has to be dealt with separately
            string rootFolderPath = AppDomain.CurrentDomain.BaseDirectory;
            logFileName = rootFolderPath+"\\server_log.txt";
            logFile = new StreamWriter(logFileName, append: false);
        }
        try
        {
            /* Block to get the max number of lines for log file.  
             * Encapsulated in try block to make sure input is valid
             */

            MAX_LINES = int.Parse(configuration["Other"]["MaxLines"]);
        }
        catch (Exception ex)
        {
            //Invalid max lines value
            Console.WriteLine(ex.Message);
            Console.WriteLine("Invalid Max Lines. Set to 5000");
            MAX_LINES = 5000;
        }
    }
    public static IniData LoadConfiguration()
    {
        /* This method loads the config file with address, port, and timeout values.
         * If there is none present, it creates one with some dummy vlues.
         * Args:
         * None
         * Returns:
         * IniData fileParser:  A parser that lets you read in values in other methods
         */
        // Set the config path to the root directory of the program + config.ini
        string rootFolderPath = AppDomain.CurrentDomain.BaseDirectory;
        string configFilePath = rootFolderPath + "\\config.ini";
        if (!File.Exists(configFilePath))
        {
            // Create a new config file with default values
            IniData defaultConfig = new IniData();
            defaultConfig["Server"]["Address"] = "127.0.0.1";
            defaultConfig["Server"]["Port"] = "8080";
            defaultConfig["Server"]["Check Adapters"] = "True";
            defaultConfig["Other"]["Timeout"] = "60";
            defaultConfig["Other"]["LogFile"] = rootFolderPath+"\\server_log.txt"; //Make the default location the root directory
            defaultConfig["Other"]["MaxLines"] = "5000";
            // Save the default config to the file
            var parser = new FileIniDataParser();
            parser.WriteFile(configFilePath, defaultConfig);

            Console.WriteLine($"Config file created: {configFilePath}");
        }

        // Load the configuration
        var fileParser = new FileIniDataParser();
        return fileParser.ReadFile(configFilePath);
    }

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
            // Use in-built ASCOM functionality to connect to the filter wheel
            prog_id = "ASCOM.SBIG.USB_FW.FilterWheel";
        }
        catch (InvalidOperationException e)
        {
            Log("Accessing remotely, defaulting to SBIG.USB_FW");
            return 1;
        }

        try
        {
            // Connect to the filter wheel
            m_FilterWheel = new ASCOM.Com.DriverAccess.FilterWheel(prog_id);
            m_FilterWheel.Connected = true;
        }
        catch(Exception ex)
        {
            Log(ex.Message);
            Log(ex.StackTrace);
            Log("Filter wheel not connected.");
            return 1;
        }
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

        int FILTER_WHEEL_TIME_OUT = int.Parse(configuration["Other"]["Timeout"]); //Pull timeout from config file
        DateTime StartTime;
        m_FilterWheel.Position = pos;
        StartTime = DateTime.Now;
        Log("Setting filter wheel to position " + pos.ToString() + "...");

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
        Log("\n");
        Log("Set position to: " + pos.ToString());
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

        string[] FILTER_LIST = null;
        // Pull the number of filters from the ASCOM interface
        int FILTER_NUMBER = m_FilterWheel.Names.Length;
        // Make a stringbuilder for the help and list commands
        StringBuilder sb = new StringBuilder();
        try
        {
            /* Get the filter list from the config file.  
             * If it does not exist, log that as a warning.
             */
            FILTER_LIST = configuration["Other"]["List"].Split(',');
        }
        catch (Exception e)
        {
            //Get the ASCOM List instead
            Log("WARNING: No Filter List Provided");
            FILTER_LIST = m_FilterWheel.Names;
        }
        if (line == "help")
        {
            /* Build a string that prints the list of commands */
            sb.AppendLine("\n");
            sb.AppendLine("Available commands:");
            sb.AppendLine("get - Gets the current filter wheel position.");
            sb.AppendLine("set <number> - Sets the filter wheel position to the given number.  Replace <number> with an actual number.");
            sb.AppendLine("server_shutdown - Shuts down the server.");
            sb.AppendLine("filter_list - Prints the filter wheel positions and their corresponding filter names.");
            sb.AppendLine("help - Prints this help message.");

            // Convert sb to string and log and return
            string rtn;
            rtn = sb.ToString();
            Log(rtn);
            return rtn;

        }
        if (line == "filter_list")
        {
            /* Print the filter list with the numbers 0 to FILTER_NUMBER/ List Length 
             * (whichever is smaller) with prefixing.
             * Each Filter is on a new line 
             */
            string rtn;
            int len = Math.Min(FILTER_NUMBER, FILTER_LIST.Length);
            sb.AppendLine("\n");
            for (int i = 0; i < len; i++)
            {
                sb.AppendLine($"{i}: {FILTER_LIST[i]}");
            }
            rtn = sb.ToString();
            Log(rtn);
            return rtn;
        }
        if (line == "get")
        {
            // Get the position of the filter wheel.
            int pos = m_FilterWheel.Position;
            string rtn;
            try
            {
                /* Try to print the filter name out.  If index out of bounds, warn and just give pos.
                 * This is only a problem if the list in config is too short
                 */
                rtn = "Filter Wheel Position is " + pos.ToString() + ". This is the " + FILTER_LIST[pos] + " filter.";
                Log(rtn);
                return rtn;
            }
            catch (Exception e)
            {
                Log("WARNING: No corresponding list value was found.  This normally means your list in config is too short.");
                rtn = "Filter Wheel Position is " + pos.ToString();
                Log(rtn);
                return rtn;
            }
        }
        else
        {
            //Parse string using space as the delimiter
            string[] words = line.Split(' ');

            //Check first token is "set"
            if (words[0] != "set")
            {
                string rtn = "Invalid input";
                LogError(rtn);
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
                    LogError(rtn);
                    return rtn;
                }
                if (pos > FILTER_NUMBER - 1 || pos < 0)
                {
                    //Given an invalid number
                    rtn = "Enter a valid filter position (0-" + (FILTER_NUMBER - 1) + ")";
                    LogError(rtn);
                    return rtn;
                }
                int ret_val = setFilterWheel(pos);
                if (ret_val == 1)
                {
                    string err = "Error setting filter wheel to position " + pos.ToString();
                    LogError(err);
                    return err;
                }
                try
                {
                    /* Try to print the filter name out.  If index out of bounds, warn and just give pos.
                     * This is only a problem if the list in config is too short
                     */
                    rtn = "Filter Wheel set to position " + pos.ToString() + ". This is the " + FILTER_LIST[pos] + " filter.";
                    Log(rtn);
                    return rtn;
                }
                catch (Exception e)
                {
                    Log("WARNING: No corresponding list value was found.  This normally means your list is too short.");
                    rtn = "Filter Wheel set to position " + pos.ToString();
                    return rtn;
                }
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

        // Use the config to get the port and the address in case we do not find an adapter
        string SERVER_ADDRESS = configuration["Server"]["Address"];
        int SERVER_PORT = int.Parse(configuration["Server"]["Port"]);
        socket = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.Tcp);
        IPEndPoint endPoint;
        /* Check the config file for if we want to check all the network adapters before
         * going to the address specified in the config file or not
         */
        bool CHECK_ADAPTERS;
        bool result = bool.TryParse(configuration["Server"]["Check Adapters"], out CHECK_ADAPTERS);
        if (result == false)
        {
            Log("There was an error in your config file.  Please fix this error or delete the file for autofix.");
            return 1;
        }
        try
        {
            if (CHECK_ADAPTERS == true)
            {   // Check all the adapters first then go to fall back
                var host = Dns.GetHostEntry(Dns.GetHostName());
                foreach (var ip in host.AddressList)
                {
                    if (ip.AddressFamily == AddressFamily.InterNetwork)
                    {
                        // Bind the socket to an endpoint
                        endPoint = new IPEndPoint(ip, SERVER_PORT);
                        socket.Bind(endPoint);

                        //Print the IP Address for any clients to use
                        Log("IP Address: " + ip.ToString());
                        Log("Port: " + SERVER_PORT.ToString());
                        // Start listening for incoming connections
                        socket.Listen(10);
                        Log("Waiting for a connection...");
                        return 0;
                    }
                }

                // Use the default values to open a socket
                Log("No network adapters with an IPv4 address in the system.  Using default values provided in config file");

                IPAddress ipAddress = IPAddress.Parse(SERVER_ADDRESS);
                endPoint = new IPEndPoint(ipAddress, SERVER_PORT);
                socket.Bind(endPoint);

                //Print the IP Address for any clients to use
                Log("IP Address: " + SERVER_ADDRESS.ToString());
                Log("Port: " + SERVER_PORT.ToString());
                // Start listening for incoming connections
                socket.Listen(10);
                Log("Waiting for a connection...");
                return 0;
            }
            else
            {
                // Use the default values to open a socket
                IPAddress ipAddress = IPAddress.Parse(SERVER_ADDRESS);
                endPoint = new IPEndPoint(ipAddress, SERVER_PORT);
                socket.Bind(endPoint);

                //Print the IP Address for any clients to use
                Log("IP Address: " + SERVER_ADDRESS.ToString());
                Log("Port: " + SERVER_PORT.ToString());
                // Start listening for incoming connections
                socket.Listen(10);
                Log("Waiting for a connection...");
                return 0;
            }
        }
        catch (Exception e)
        {
            LogError("Error initializing socket.  Exiting");
            return 1;
        }
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

            Log("Client Connected!");

            while (clientSocket.Connected)
            {
                //Receive data from the client
                byte[] buffer = new byte[4096];
                int bytesRead = clientSocket.Receive(buffer);

                //If we get 0 bytes, connection has been closed
                if (bytesRead == 0)
                {// Close the client socket to exit gracefully
                    Log("Client Disconnected: Waiting for New Client");
                    break;
                }
                string dataReceived = System.Text.Encoding.ASCII.GetString(buffer, 0, bytesRead);
                Log("Data Received: " + dataReceived);

                //If data received tells us to quit server, quit here and close
                if (dataReceived == "server_shutdown")
                {
                    //Tell the socket that the server is shutting down
                    string toSend = "Shutting down server...";
                    Log(toSend);
                    //Send Data back to the client
                    byte[] d2s = System.Text.Encoding.ASCII.GetBytes(toSend);
                    clientSocket.Send(d2s);

                    //Close the client Socket
                    clientSocket.Shutdown(SocketShutdown.Both);
                    clientSocket.Close();
                    // Close the server socket
                    socket.Close();
                    Log("Server has been shut succesfully");
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

            LogError("An error occurred: " + ex.Message);
            return 1;
        }

        // Start waiting again if client closed
        int ret_val = 2;
        return ret_val;
    }
    void receiveAndSendWrapper()
    {
        /* Very simple wrapper method for the receiveAndSend method
         * Required because program is now written as a service, 
         * and not as a client executable.
         * Args:
         * None
         * Returns:
         * None
         */
        int ret_val = 2;
        while (ret_val != 0) 
        {
            ret_val = receiveAndSend();
        }
    }
    protected override async void OnStart(string[] args)
    {
        /* Initializes socket and filter wheel, then receives and sends input, then closes and cleans up.
        *  Args:
        *  string[] args: (ignore my little rant) omg I thought I was done with you nobody knows what you do 
        *  Returns:
        *  0 for success, 1 for failure.
        */

        // Obtain a service controller to force quit the service if required
        ServiceController serviceController = new ServiceController();

        //Load in the config file
        configuration = LoadConfiguration();
        logFileName = configuration["Other"]["LogFile"];

        //Create a new logFile as needed.  Otherwise use the existing one.
        if (File.Exists(logFileName))
        {
            //Get the number of lines present
            logLineCount = File.ReadLines(logFileName).Count();
            logFile = new StreamWriter(logFileName, append: true);
        }
        else
        {
            CreateLogFile();
        }
        using (logFile)
        {
            //Initialize the Filter Wheel
            int ret_val = 0;
            ret_val = initFW();
            if (ret_val == 1)
            {
                //An error occurred during Filter Wheel initialization
                Log("Terminating");
                serviceController.Stop();
                return;
            }

            //Initialize socket
            ret_val = initSocket();
            if (ret_val == 1)
            {
                //An error occurred during socket initialization
                Log("Terminating");
                serviceController.Stop();
                return;
            }

            if (ret_val == 0)
            {
                //Receive and Send from/to client. Start this in another thread to allow server state to transition.
                Task task = Task.Run(() => receiveAndSendWrapper());

                //Wait for the task to complete (aka all running of program)
                await task;
            }
            Log("Terminating");
            serviceController.Stop();
            return;
        }
    }

    private void Process_OutputDataReceived(object sender, DataReceivedEventArgs e)
    {
        throw new NotImplementedException();
    }

    protected override void OnStop()
    {
        //No clean up required.  Everything is handled cleanly by the main function anyways.
        using(logFile)
        {
            Log("Terminating Service");
            base.OnStop();
        }
    }
}
class Program
{
    // Simple class with only a main method to run the OnStart method.  Required because this is now a service.
    static void Main(string[] args)
    {
        // Execution of program starts here.  Serves to hand over execution to the service.
        ServiceBase[] servicesToRun;
        servicesToRun = new ServiceBase[]
        {
            new FilterWheelMoverServerService()
        };
        ServiceBase.Run(servicesToRun);
    }
}