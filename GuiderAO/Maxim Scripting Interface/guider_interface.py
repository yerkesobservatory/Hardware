"""
SBIG Guider SC-3 Command Line Interface
    To be used when operating the guider remotely through MaxIm DL

Included in the imports is the maxim_menu.py file which holds a library of python func's...
...built around the MaxIm DL proprietary scripting methods.

Using match/case (!!!a feature of Python 3.10 and later!!!) we can simulate a user...
...interface by continuously prompting the operator to execute a command. Until the...
...user has declined to execute another command, the session will be ongoing and the...
...MaxIm.Application Object will still be open.

Commands:
1. 'set' :establishes connection with the guider camera by initializing a ccd camera Object.

2. 'sever' :disconnects the guider camera by de-initializing the ccd camera Object.

3. 'expose' :takes a light exposure with the guider camera; how guide stars are found.
    - Takes a float value for duration as a parameter.

4. 'calibrate' :begins the calibration process in MaxIm DL. Should be done on device startup.
    - Takes a float value for duration (of each exposure) as a parameter.

5. 'calcode' :returns the present calibration code for the guider Object.
    - Decoding table can be found in the scripting manual.

6. 'stop' :instantaneously quits the guider's current task and returns the status to idle.

7. 'status' :returns the present status code for the ccd camera Object.
    - Decoding table can be found in scripting manual.

8. 'track' :begins the guide star tracking process in MaxIm DL. Guide star must alr be found.
    - The 'calibrate' and 'expose' commands must be done successfully before 'track'.
    - Takes a float value for duration (of each exposure) as a parameter.

9. 'starcoords' :returns the current coordinates of the acquired guide star.
    - If no guide star has been acquired, this shall return (0.0,0.0).

10. 'list' :prints the current list of operable commands to CLI

11. 'quit' :closes the interface as well as MaxIm DL by letting the loop complete.
"""
import comtypes.client # windows package for COM connection
import maxim_menu # the python library of operable commands

options = ['set', 'sever', 'expose', 'calibrate', 'calcode', 'stop', 'status', 'track', \
           'starcoords', 'list', 'quit']

session = 1 # 1 means interface open, 0 means interface closed
Object = None
#the application Object is initialized, opening MaxIm DL
app = comtypes.client.CreateObject("MaxIm.Application")

#the session loop
while session == 1:

    command_string = input('Command?\n:') #must be typed lower case as one word
    match command_string:
        case "set": #establishes a maxim.ccdcamera Object
            Object = maxim_menu.guider_connect()
            session = 1
            continue
        case "sever": #quits the camera Object, unsure if quits both
            maxim_menu.guider_disconnect(Object)
            session = 1
            continue
        case "expose": #takes a guider exposure, will change when add normal expose
            duration = input('Duration in s? (float)\n:') #respond in float value
            duration = float(duration)
            maxim_menu.guider_expose(duration, Object)
            session = 1
            continue
        case "calibrate": #calibrates guider, dont think we'll have to add ccdcal
            duration = input('Duration in s? (float)\n:') #respond in float value
            duration = float(duration)
            maxim_menu.guider_calibrate(Object, duration)
            session = 1
            continue
        case "calcode": #returns the calibration code of the guider
            maxim_menu.guider_calstate(Object) # refer to manual for codes 
            session = 1
            continue
        case "starcoords": #returns coords of guide star in photo
            maxim_menu.guidestar_coords(Object)
            session = 1
            continue
        case "track": #tracks the currently selected guidestar
            duration = input('Duration in s? (float)\n:') # respond in float value
            duration = float(duration)
            maxim_menu.guider_track(Object, duration)
            session = 1
            continue
        case "stop": #stops guider tracking, returns cam to idle
            maxim_menu.guider_stop(Object)
            session = 1
            continue
        case "status": #checks status of the ccd camera
            maxim_menu.cam_status(Object)
            session = 1
            continue
        case "list": #returns list of operable commands to the command line
            print(options)
            session = 1
            continue
        case "quit": #quits the current session
            confirm_bool = input('Are you sure? Are all devices warm/shutdown? (y/n)\n:')
            match confirm_bool:
                case 'y':
                    session = 0
                    break
                case 'n':
                    session = 1
                    continue
