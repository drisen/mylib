#
# credentials.py
# Copyright (C) 2019 Dennis Risen, Case Western Reserve University
#
import json
import os
from typing import Union


def credentials(system: str, username: str = None,
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
