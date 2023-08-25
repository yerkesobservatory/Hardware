# MaxIm DL Scripting Interface
---
## List of Commands
| CmdName    | Parameters                      | Returns                   |
|------------|---------------------------------|---------------------------|
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