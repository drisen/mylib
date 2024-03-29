# mylib
Library of utilities for managing credentials, logging errors, and time conversions in a home_zone

- **credentials**`(system: str, username: str=None, interactive: bool = False) -> tuple`  
    returns the credentials for system/username.
    When called with interactive=True, prompts to allow the user to create the repository, add or update credentials
    in the repository.
- **buckets**`(lst: list, lows: Iterable) -> list:`
    Summarize the lst of values into a histogram with breakpoints in lows.
    Side-effect: sorts lst into ascending order
- **Logging**
    - **logErr**`(*s, start:str='\n', end:str='', **kwargs)`  
      log join(timestamp and s) via email (unix) or print(**kwargs) (Windows)  
      -`logErr.logSubject = {the subject}`  
      -`logErr.logToAddr = [email addresses]`
    - **printIf** `(verbose: int, *s, start: str = '\n', end: str = '', **kwargs)`
      if Verbose>0, print timestamped *s
- **Time conversion** functions for handling various time formats presented in the
enterprise's home time zone
    - **anyToSecs**`(t, offset:float=0.0) -> float`  
      Converts milliseconds:int, seconds:float, or ISO datetime:str to seconds:float.
    - **fromTimeStamp**`(t: float) -> datetime:`
      datetime.datetime(t) with home time zone
    - **millisToSecs**`(millis:int, timeDelta:float=0) -> float`
      Convert epochMillis:int to float + timeDelta
    - **secsToMillis**`(t:float, timeDelta:float=0.0) -> int`  
      Convert to/from epochMilliseconds on foreign system from/to epochSeconds on local system
      with adjustment for local time ahead of foreign time by timeDelta seconds
    - **strfTime**`(t: object, fmt: str = '%Y-%m-%dT%H:%M:%S', millis: bool = False) -> str`  
      Format epochMillis:int or epochSeconds:float to configured **home_zone** 
      timezone, or pass-through a string.
    - **strpSecs**`(s:str) -> float ` 
      Parse ISO time text to UTC epochSeconds:float.
