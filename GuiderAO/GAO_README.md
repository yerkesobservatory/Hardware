# Guider/AO Software Package

## Overview
This package contains 2 separate software packages: a server/client implementation to operate MaximDL so that we can guide and use adaptive optics, and a translator that takes commands from the guider and adaptive optics and sends them to the mount.  The server/client implementation is in the GuiderService subfolder, and the translator that sends commands to the mount is in the GuiderTranslator subfolder.  Documentation for both is provided in this document.  Use the table of contents below to navigate to the section you are interested in.

## Table of Contents

## Guider Service

The server and client are present in 2 separate folders in the GuiderService subfolder.  The server must be run on a Windows computer with MaxIm DL Pro involved (lower versions of MaxIm DL may work but the program has not been tested with them).  Additionally, the server requires at least Python 3.10 to run to take advantage of Python's match case functionality.

### List of Commands

| CmdName    | Parameters                      | Returns                   | Description               |
|------------|---------------------------------|---------------------------|---------------------------|
| set        | None                            | connected camera object   |                       
| sever      | camera object                   | None                      |
| expose     | camera object, duration (float) | identified guide star     |
| calibrate  | camera object, duration (float) | calibrated camera object  |
| calcode    | camera object                   | calibration code          |
| stop       | camera object                   | camera to idle position   |
| status     | camera object                   | camera status code        |
| track      | camera object, duration (float) | camera tracking guidestar |
| starcoords | camera object                   | guide star coordinates    |
| list       | None                            | list of operable commands |
| quit       | None                            | None                      | 


### MaxIm.CCDCamera.Status Output Codes

| EventCode(#) | EventTitle           |EventDescription                                      |
|--------------|----------------------|------------------------------------------------------|
| 1            | csError              | Camera is reporting an error                         |
| 2            | csIdle               | Camera is connected but inactive                     |
| 3            | csExposing           | Camera is exposing a light image                     |
| 4            | csReading            | Camera is reading an image from the sensor array     |
| 5            | csDownloading        | Camera is downloading an image to the computer       |
| 6            | csFlushing           | Camera is flushing the sensor array                  |
| 7            | csWaitTrigger        | Camera is waiting for a trigger signal               |
| 8            | csWaiting            | Camera Control Window is waiting for MaxIm DL        |
| 9            | csDelay              | Camera Control is waiting to acquire next image      |
| 10           | csExposingAutoDark   | Camera is exposing a dark needed by Simple Auto Dark |
| 11           | csExposingBias       | Camera is exposing a bias frame                      |
| 12           | csExposingDark       | Camera is exposing a dark frame                      |
| 13           | csExposingFlat       | Camera is exposing a flat frame                      |
| 15           | csFilterWheelMoving  | Camera Control Window is waiting for filter wheel    |
| 28           | csGuidingSuspended   | Autoguiding is suspended while main camera downloads |
| 29           | csWaitingForDownload | Guide camera waiting for main camera to end download |

## Guider Translator

The Guider translator was written using the ASCOM alpyca in