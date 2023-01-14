#
# mylib.py Copyright (C) 2019 Dennis Risen, Case Western Reserve University
# refactored from mylib.py
"""
Library of utilities including credentials manager, error logging, and time conversions in home_zone
"""

import calendar
from datetime import datetime
import json
import os
import platform
from pytz import timezone
import re
import sys
import time
from typing import Iterable, Union
home_zone = timezone('US/Eastern')		# All str date input/output in this timezone
ts_format = '%y-%m-%dT%H:%M:%S'         # timestamp format used by logErr


def anyToSecs(t, offset: float = 0.0) -> float:
    """Convert milliseconds:int, seconds:float, or ISO datetime:str to seconds:float.
    Parameters:
        t (object):			epoch milliseconds:int, epoch seconds:float, or ISO datetime:str
        offset (float):		epoch_msecs/1000 + offset = epoch_seconds
    Returns:
        (float):			epoch seconds
    """
    if isinstance(t, int):				# epochMillis: int msec?
        return t/1000.0 + offset		# Yes.
    elif isinstance(t, float):			# epochSeconds: float time.time()?
        return t						# no conversion necessary
    elif isinstance(t, str):			# ISO text datetime?
        return strpSecs(t)
    else:
        raise TypeError


def buckets(lst: list, lows: Iterable) -> list:
    """Summarize the lst of values into a histogram with breakpoints in lows.
    Side-effect: sorts lst into ascending order

    :param lst: 	[val, ...] to enter into histogram
    :param lows: 	[breakpoint, ...] in ascending order
    :return: 		[[breakpoint, count], ...]
    """
    lst.sort()
    result = []
    low = lst[0] if len(lst) > 0 else 0  # additional low breakpoint, if necessary
    i = 0  # index into bucket breakpoints
    cnt = 0
    for nxt in lows:                    # for each breakpoint
        while i < len(lst):
            if lst[i] < nxt:            # value < breakpoint?
                cnt += 1                # add to count
                i += 1
            else:
                break                   # done with this bucket
        result.append((low, cnt))
        low = nxt                       # advance to next bucket breakpoint
        cnt = 0
    result.append((low, len(lst) - 1))  # add count of vals >= top breakpoint
    return result


def credentials(system: str, username: Union[str, None] = None,
                interactive: bool = False) -> (str, Union[str, None]):
    """Lookup your (username, password) for username on system.
    Username defaults to the first username defined for system.

    Parameters:
        system (str):		system name. E.g. ncs01.case.edu
        username (str):		username on system. Default is 1st username for system
        interactive (str):	True to prompt for information when missing
    Returns:
        (tuple):			(username , password)
    """
    # ~/.credentials.json, which has the form:
    # {domain_name_or_ip_address: {user_name: password, ...}, ...}}
    try:
        with open(os.path.join(os.path.expanduser('~'), '.credentials.json'),
                'r') as cred_file:
            creds = json.loads(cred_file.read())
    except FileNotFoundError as e:
        if not interactive:
            raise e
        print(f"You do not have a ~/.credentials.json file")
        while True:
            yn = input('Do you want to create one? (Y/N): ').upper()
            if len(yn) > 0 and yn[0] in {'Y', 'N'}:
                break
        creds = {}
        if yn[0] == 'Y':
            with open(os.path.join(os.path.expanduser('~'), '.credentials.json'),
                      'w') as cred_file:
                json.dump(creds, cred_file)
    entry = creds.get(system, None)
    if entry is None:					# No user credentials for this system?
        if not interactive:
            raise KeyError(f"No credentials for {system}")  # Yes. KeyError
        print(f"No credentials found for {system}")
        while True:
            if username is None:
                username = input(f"Enter your default username for {system}: ")
            password = input(f"Enter password for {username} on {system}: ")
            entry = {username: password}
            yn = input("Add these credentials to ~/.credentials.json? (Y/N)").upper()
            if len(yn) > 0 and yn[0] in {'Y', 'N'}:
                creds[system] = entry
                if yn[0] == 'Y':
                    with open(os.path.join(os.path.expanduser('~'), '.credentials.json'),
                              'w') as cred_file:
                        json.dump(creds, cred_file)
                break
    if isinstance(entry, dict) and len(entry) > 0:  # valid entry?
        if username is None: 			# Yes. 1st username is OK?
            return entry.popitem() 		# return the first (username, password)
        return username, entry.get(username, None) 	# tuple for specific user
    raise KeyError(f"Credentials entry for {system} must be a dict")  # No password for this user


def fromTimeStamp(t: float) -> datetime:
    """datetime.datetime(t) with home time zone"""
    return datetime.fromtimestamp(t, home_zone)


if platform.system() == 'Linux': 		# Running on Linux platform?
    import getpass
    import socket
    import subprocess

    def logErr(*s, start: str = '\n', end: str = '', **kwargs):
        """log timestamp + join(s) via email (Linux) or print(**kwargs) (Windows)

        settable attributes:

        - logErr.logSubject is <email subject>; default is program name
        - logErr.logToAddr is <email addresses>; default is <user>@<host>

        :param s:       message strings to merge as in print()
        :param start:   prefix str
        :param end:     suffix str
        :param kwargs:  ignored in linux; passed to print() in windows
        :return:
        """
        print(f"{start}{strfTime(time.time(), ts_format)} ERROR", *s, end=end, **kwargs)
        message = ' '.join(str(x) for x in s)  # join the parameters, like print
        try:
            params = [r'/usr/bin/mailx', '-s', logErr.logSubject]+logErr.logToAddr
            subprocess.run(params,
                check=True, input=message.encode())
        except subprocess.CalledProcessError as e:
            print(f"mailx failed: {e}")
    # Default Subject of logError() email messages
    logErr.logSubject = os.path.basename(sys.argv[1]
        if re.search('python', sys.argv[0]) else sys.argv[0])
    # Default list of addressees to receive logError() messages
    logErr.logToAddr = [getpass.getuser() + '@'
        + '.'.join(socket.getfqdn().split('.')[-2:])]
else:									# No, just print

    def logErr(*s, start: str = '\n', end: str = '', **kwargs):
        """log timestamp + join(s) via email (Linux) or print(**kwargs) (Windows)

        settable attributes:

        - logErr.logSubject is <email subject>; default is program name
        - logErr.logToAddr is <email addresses>; default is <user>@<host>

        :param s:       message strings to merge as in print()
        :param start:   prefix str
        :param end:     suffix str
        :param kwargs:  ignored in linux; passed to print() in windows
        :return:
        """

        params = [r'/usr/bin/mailx', '-s', logErr.logSubject] + logErr.logToAddr
        print(f"unix would call subprocess({params}, check=True, input=message=<see below>)")
        print(f"{start}{strfTime(time.time(), ts_format)} ERROR", *s, end=end, **kwargs)
    # Default Subject of logError() email messages
    logErr.logSubject = os.path.basename(sys.argv[1]
        if re.search('python', sys.argv[0]) else sys.argv[0])
    # Default list of addressees to receive logError() messages
    logErr.logToAddr = ["default"]


def millisToSecs(millis: int, time_delta: float = 0) -> float:
    """Convert CPI server's epochMillis:int to my time.time() equivalent"""
    return millis / 1000.0 + time_delta


def printIf(verbose: int, *s, start: str = '\n', end: str = '', **kwargs):
    """if verbose>0, print timestamped *s

    :param verbose:     >0 to print
    :param s:           strings to join with ' '
    :param start:       prefix string
    :param end:         passed to print(end=end)
    :param kwargs:      optionals passed to print()
    :return:
    """
    if verbose > 0:
        print(f"{start}{strfTime(time.time())}", *s, end=end, **kwargs)


def secsToMillis(t: float, time_delta: float = 0.0) -> int:
    """Convert my time.time():float to CPI server's epochMillis:int."""
    if not isinstance(t, float):
        raise ValueError
    return int((t - time_delta) * 1000.0)


def strfTime(t: Union[float, int, str], fmt: str = '%Y-%m-%dT%H:%M:%S', millis: bool = False) -> str:
    """Format epochMillis:int or epochSeconds:float to home timezone. Pass through str

    Parameters:
        t:		epoch milliseconds: int, epoch seconds: float, or date str
        fmt:	strftime format string. Default='%Y-%m-%dT%H:%M:%S'
        millis:	True to include 3-digit milliseconds
    Returns:
        (str):	home time zone time string
    """
    try:
        if isinstance(t, float):		# epoch seconds from time.time()?
            dt = datetime.fromtimestamp(t, home_zone)
        elif isinstance(t, int):		# epoch msec from server
            dt = datetime.fromtimestamp(millisToSecs(t), home_zone)
        elif isinstance(t, str):
            try:
                secs = strpSecs(t)		# try to convert to UTC seconds
                dt = datetime.fromtimestamp(secs, home_zone)
            except ValueError:			# No. Unsuccessful
                return t				# just return the string
        else:
            return str(t)
        s = dt.strftime(fmt)
        if millis:						# output milliseconds too?
            return s + f"{dt.microsecond/1000000.0:.3f}"[-4:]
        else:
            return s
    except OSError:						# fromtimestamp didn't like argument
        return str(t)


def strpSecs(s: str) -> float:
    """Parse ISO-like datetime text to UTC epochSecond

    Recognizes 'Z' Zulu zone as 0000. About 6x faster than dateutil.parser
    :param s:   ISO datetime text
    :return:    float epoch seconds
    """
    m = re.fullmatch(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})(\.[0-9]+)(.*)', s)
    if m is not None:					# an ISO-like date?
        try:
            zone = m.group(3)
            z = re.fullmatch(r'[+-][0-9]{4}', zone)
            if zone[0] == 'Z':			# Zone is Military Zulu?
                offset = 0				# *.strptime don't understand Zulu
            elif z is not None:			# Zone is +/-HHMM:
                offset = (-60 if zone[0] == '+' else 60)*(int(zone[1:3])*60+int(zone[3:5]))
            else:						# not prepared to parse some other format
                raise ValueError('Zone not military or Zulu')
            # time.strptime doesn't understand zones or fractional seconds
            secs = calendar.timegm(time.strptime(m.group(1), '%Y-%m-%dT%H:%M:%S'))
            if len(m.group(2)) > 0:		# optional fractional seconds?
                secs += float(m.group(2)) 	# Yes. works for any number of digits
            return secs+offset
        except ValueError:				# can't think of any specific error
            raise ValueError
    raise ValueError('s does not match ISO format')


def strpTime(date_string: str, fmt: str) -> float:
    """datetime.strptime localized from home time zone"""
    return home_zone.localize(datetime.strptime(date_string, fmt)).timestamp()


def verbose_1(verbose: int):
    """Return verbosity level minus 1. E.g. for lower layer
    Parameter:
        verbose (int/bool)	bool or integer verbosity level
    Returns:
        bool input or verbose-1
    """
    if isinstance(verbose, bool): 		# bool
        return 1 if verbose else 0 		# convert to int
    elif isinstance(verbose, int): 		# int is decremented
        return verbose-1 if verbose > 0 else 0
    else:								# other input
        raise ValueError(f"type={type(verbose)}")
