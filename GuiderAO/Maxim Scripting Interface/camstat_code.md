# MaxIm.CCDCamera.Status Output Codes

---

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