import comtypes.client
import time

def guider_connect(): # creates the MaxIm.CCDCamera Object
    Object = comtypes.client.CreateObject("MaxIm.CCDCamera")
    time.sleep(.5) #extra time to be safe
    Object.LinkEnabled = True
    time.sleep(.5) #rohan's magical fix to making GuiderExpose work
    #check link
    if Object.LinkEnabled != True:
        print('Guider not connected, check if plugged in')
        Object.Quit()
        return
    else:
        print('Guider connected')
    return Object # has to return it so that it can be used by other commands

def guider_disconnect(Object): # disconnects the MaxIm.CCDCamera Object
    Object.Quit()
    print("Guider disconnected. No Object returned.")
    return # does not return an Object because its been disconnected

def guider_expose(duration, Object, auto_select = True): # takes autoguider exposure
    # this method is what initializes a guide star position
    #remember to calibrate first

    #check link
    if Object.LinkEnabled != True:
        print('Guider not connected. Check if plugged in.')
        Object.Quit()
        return
    else:
        pass
    #check moving
    while Object.GuiderMoving == True or Object.GuiderRunning == True:
        time.sleep(1)
        continue
    time.sleep(.5) # rohan's magical fix to make GuiderExpose work

    # will pick the brightest star in the sky, will normally be true
    if auto_select == False:
        Object.AutoSelectStar = False
        print('AutoSelect Guide Star is turned off, so no star will be chosen.')
    else:
        pass
    
    print(f'Guider connected, exposing for {duration}s')
    Object.GuiderExpose(duration)
    while Object.GuiderMoving == True or Object.GuiderRunning == True:
        time.sleep(1)
        continue
    time.sleep(.5)

    #also will print the chosen guide star (if one is found)
    #when the coords are (0.0,0.0) you can assume that no star was found
    if auto_select == True:
        print('Checking for guide star...')
        x = Object.GuiderXStarPosition # x position in image
        y = Object.GuiderYStarPosition # y position in image
        time.sleep(0.5)
        print(f'Guide star coords: ({x},{y})')
        return Object
    else:
        return Object
    
def guider_calibrate(Object, duration): # calibrates the guider
    #check link
    if Object.LinkEnabled != True:
        print('Guider not connected, check if plugged in')
        Object.Quit()
        return
    else:
        pass
    #check calcode
    calcode = Object.GuiderCalState
    match calcode: # checking that calcode is appropriate, could be clunky / unnecesary
        case 0: # needs calibration
            print(f'Guider preparing to calibrate: {duration}s exposures')
            Object.GuiderCalibrate(duration)
            while Object.GuiderMoving == True or Object.GuiderRunning == True:
                time.sleep(1)
                continue
            time.sleep(5)
            calcode_new = Object.GuiderCalState
            match calcode_new:
                case 2:
                    print('Guider Calibrated Successfully')
                    return Object
                case 3:
                    print('Guider calibration failed')
                    return Object
                case _:
                    print('Unknown error raised')
                    return Object
        case 1: # is calibrating, dont know why this would be raised
            print('Guider currently calibrating')
            while Object.GuiderMoving == True or Object.GuiderRunning == True:
                time.sleep(1)
                continue
            time.sleep(5)
            calcode_new = Object.GuiderCalState
            match calcode_new:
                case 2:
                    print('Guider Calibrated Successfully')
                    return Object
                case 3:
                    print('Guider calibration failed')
                    return Object
                case _:
                    print('Unknown error raised')
                    return Object
        case 2: # already calibrated
            print('Guider Calibrated Successfully')
            return Object
        case 3: #tried to and failed
                    print('Guider calibration failed')
                    return Object
        case _: # no code that can be interpreted, just a precaution
            print('Unknown error raised')
            return Object

def guider_calstate(Object): #just checks calibration code, should be used on initial startup
    #check link
    if Object.LinkEnabled != True:
        print('Guider not connected, check if plugged in')
        Object.Quit()
        return
    else:
        calcode = Object.GuiderCalState
        print(f'Guider calibration code: {calcode}')
    return Object
    
def guider_stop(Object): #stops guider from completing current task
    #check link
    if Object.LinkEnabled != True:
        print('Guider not connected, check if plugged in')
        Object.Quit()
        return
    else:
        pass

    #Object.GuiderStop()
    time.sleep(0.5)

    #check moving
    if Object.GuiderRunning == True or Object.GuiderMoving == True:
        print("Error: Guider still operating")
        return Object
    else:
        print("Guider stopped, now idle")
        return Object

def cam_status(Object): #gets status code for camera, decode table in scripting manual
    #check link
    if Object.LinkEnabled != True:
        print('Guider not connected, check if plugged in')
        Object.Quit()
        return
    else:
        pass
    #check guider moving
    while Object.GuiderMoving == True or Object.GuiderRunning == True:
        time.sleep(1)
        continue

    #check camera 1 status if it applies to the situation
    status = Object.CameraStatus
    print(f'Camera 1 Status Code: {status}')
    return Object

def guider_track(Object, duration): # initializes guidance of star w/ input expose duration
    #check link
    if Object.LinkEnabled != True:
        print('Guider not connected, check if plugged in')
        Object.Quit()
        return
    else:
        pass
    #check moving
    while Object.GuiderMoving == True or Object.GuiderRunning == True:
        time.sleep(1)
        continue
    
    x = Object.GuiderXStarPosition # x position in image
    y = Object.GuiderYStarPosition # y position in image
    print('Beginning guidestar tracking')
    print(f'Guidestar coords: ({x}, {y})')

    Object.GuiderTrack(duration)
    #check moving
    return Object

def guidestar_coords(Object): #just prints the guidestar coords in case one is curious
    #check link
    if Object.LinkEnabled != True:
        print('Guider not connected, check if plugged in')
        Object.Quit()
        return
    else:
        pass
    #check moving
    while Object.GuiderMoving == True or Object.GuiderRunning == True:
        time.sleep(1)
        continue
    time.sleep(0.5)
    x = Object.GuiderXStarPosition # x position in image
    y = Object.GuiderYStarPosition # y position in image
    time.sleep(0.5)
    print(f'Guide star coords: ({x},{y})')
    return Object