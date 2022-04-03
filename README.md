# credentials
Access and manage the credentials for system/user from a repository
in the user's HOME/.credentials.json file.

**credentials**`(system: str, username: str=None, interactive: bool = False) -> tuple`  

returns the credentials for system/username.
When called with interactive=True, prompts to allow the user to create the repository, add or update credentials
in the repository.
