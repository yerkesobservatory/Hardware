import comtypes.client
import time

def guider_connect(): # creates the MaxIm.CCDCamera object
    object = comtypes.client.CreateObject("MaxIm.CCDCamera")
    time.sleep(.5) #extra time to be safe
    object.LinkEnabled = True
    time.sleep(.5) #rohan's magical fix to making GuiderExpose work
    #check link
    if object.LinkEnabled != True:
        print('Guider not connected, check if plugged in')
        object.Quit()
        return
    else:
        print('Guider connected')
    return object # has to return it so that it can be used by other commands

def guider_disconnect(object): # disconnects the MaxIm.CCDCamera object
    object.Quit()
    print("Guider disconnected. No object returned.")
    return # does not return an object because its been disconnected

def guider_expose(duration, object, auto_select = True): # takes autoguider exposure
    # this method is what initializes a guide star position
    #remember to calibrate first

    #check link
    if object.LinkEnabled != True:
        print('Guider not connected. Check if plugged in.')
        object.Quit()
        return
    else:
        pass
    #check moving
    while object.GuiderMoving == True or object.GuiderRunning == True:
        time.sleep(1)
        continue
    time.sleep(.5) # rohan's magical fix to make GuiderExpose work

    # will pick the brightest star in the sky, will normally be true
    if auto_select == False:
        object.AutoSelectStar = False
        print('AutoSelect Guide Star is turned off, so no star will be chosen.')
    else:
        pass
    
    print(f'Guider connected, exposing for {duration}s')
    object.GuiderExpose(duration)
    while object.GuiderMoving == True or object.GuiderRunning == True:
        time.sleep(1)
        continue
    time.sleep(.5)

    #also will print the chosen guide star (if one is found)
    #when the coords are (0.0,0.0) you can assume that no star was found
    if auto_select == True:
        print('Checking for guide star...')
        x = object.GuiderXStarPosition # x position in image
        y = object.GuiderYStarPosition # y position in image
        time.sleep(0.5)
        print(f'Guide star coords: ({x},{y})')
        return object
    else:
        return object
    
def guider_calibrate(object, duration): # calibrates the guider
    #check link
    if object.LinkEnabled != True:
        print('Guider not connected, check if plugged in')
        object.Quit()
        return
    else:
        pass
    #check calcode
    calcode = object.GuiderCalState
    match calcode: # checking that calcode is appropriate, could be clunky / unnecesary
        case 0: # needs calibration
            print(f'Guider preparing to calibrate: {duration}s exposures')
            object.GuiderCalibrate(duration)
            while object.GuiderMoving == True or object.GuiderRunning == True:
                time.sleep(1)
                continue
            time.sleep(5)
            calcode_new = object.GuiderCalState
            match calcode_new:
                case 2:
                    print('Guider Calibrated Successfully')
                    return object
                case 3:
                    print('Guider calibration failed')
                    return object
                case _:
                    print('Unknown error raised')
                    return object
        case 1: # is calibrating, dont know why this would be raised
            print('Guider currently calibrating')
            while object.GuiderMoving == True or object.GuiderRunning == True:
                time.sleep(1)
                continue
            time.sleep(5)
            calcode_new = object.GuiderCalState
            match calcode_new:
                case 2:
                    print('Guider Calibrated Successfully')
                    return object
                case 3:
                    print('Guider calibration failed')
                    return object
                case _:
                    print('Unknown error raised')
                    return object
        case 2: # already calibrated
            print('Guider Calibrated Successfully')
            return object
        case 3: #tried to and failed
                    print('Guider calibration failed')
                    return object
        case _: # no code that can be interpreted, just a precaution
            print('Unknown error raised')
            return object

def guider_calstate(object): #just checks calibration code, should be used on initial startup
    #check link
    if object.LinkEnabled != True:
        print('Guider not connected, check if plugged in')
        object.Quit()
        return
    else:
        calcode = object.GuiderCalState
        print(f'Guider calibration code: {calcode}')
    return object
    
def guider_stop(object): #stops guider from completing current task
    #check link
    if object.LinkEnabled != True:
        print('Guider not connected, check if plugged in')
        object.Quit()
        return
    else:
        pass
    
    #check moving
    if object.GuiderMoving == True or object.GuiderRunning == True:
        print('Stopping guider exposure/tracking')
        object.GuiderStop()
        return object
    else:
        print('Guider idle, awaiting further commands')
        return object

def cam_status(object): #gets status code for camera, decode table in scripting manual
    #check link
    if object.LinkEnabled != True:
        print('Guider not connected, check if plugged in')
        object.Quit()
        return
    else:
        pass
    #check guider moving
    while object.GuiderMoving == True or object.GuiderRunning == True:
        time.sleep(1)
        continue

    #check camera 1 status if it applies to the situation
    status = object.CameraStatus
    print(f'Camera 1 Status Code: {status}')
    return object

def guider_track(object, duration): # initializes guidance of star w/ input expose duration
    #check link
    if object.LinkEnabled != True:
        print('Guider not connected, check if plugged in')
        object.Quit()
        return
    else:
        pass
    #check moving
    while object.GuiderMoving == True or object.GuiderRunning == True:
        time.sleep(1)
        continue
    
    x = object.GuiderXStarPosition # x position in image
    y = object.GuiderYStarPosition # y position in image
    print('Beginning guidestar tracking')
    print(f'Guidestar coords: ({x}, {y})')

    object.GuiderTrack(duration)
    #check moving
    return object

def guidestar_coords(object): #just prints the guidestar coords in case one is curious
    #check link
    if object.LinkEnabled != True:
        print('Guider not connected, check if plugged in')
        object.Quit()
        return
    else:
        pass
    #check moving
    while object.GuiderMoving == True or object.GuiderRunning == True:
        time.sleep(1)
        continue
    time.sleep(0.5)
    x = object.GuiderXStarPosition # x position in image
    y = object.GuiderYStarPosition # y position in image
    time.sleep(0.5)
    print(f'Guide star coords: ({x},{y})')
    return object