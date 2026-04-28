# Assembly
A basic Python-based Discord bot including functionality for NationStates regions looking to provide WA information to their residents, including IFV allocation and submission, and various other tools.

This bot does *not* support multiple servers using the same instance! You **must** self host your own instance for your server only. To that end, it is recommended that you remove the ability for other users to invite your bot to their own servers.

# Installation
## Downloading
### Development
To access the latest development builds, clone the repository.
`git clone https://github.com/HippoProgrammer/assembly.git`
### Stable
There are no stable releases currently.

## Configuration
Configuration files must be provided in `./conf`.
### Akari
No user configuration of Akari is required. Do not edit `./conf/akari/akari.conf` unless *you know what you are doing.*
Editing `akari.conf` can lead to incorrect behaviour of all SSE-backed functionality.
### Secrets
You must provide the relevant secrets in `.conf` files within `./conf/secrets`:
- You must have a Discord bot token.
  - Provide it in `token.conf`.
- You must also generate passwords for the database.
  - You can do this using the `openssl` utility on Unix-based systems (or using Git Bash on Windows):
    - `openssl rand -hex [num] > [conf-file]`
    - `[num]` should be a reasonable number of characters - 16 or more is recommended
    - `[conf-file]` should be the path to the correct `.conf` file
  - You can also do this using any other method of generating random alphanumeric strings.
  - Provide a random string in `appdb.conf`.
  - Provide a different random string in `akaridb.conf`.
  - Provide another different random string in `sudodb.conf`.

## Execution
Once the correct configuration is supplied, you may run the bot.
### Docker Compose (recommended)
Running using the included Docker Compose file is the easiest and quickest way to set up the bot.
Simply run
`docker compose up -d`
### Docker
You may also use the included `Dockerfile` to run the app standalone as a Docker container. 
However, you will need to provide the correct environment variables and your own Postgres and Akari instances in the relevant locations.
Methods to do this are beyond the scope of this guide.
### Python (unsupported)
You may also run the app direct from source using your system's Python interpreter. 
`python3 ./src`
However, this method is not supported. You will need to supply the correct environment variables, as well as your own Postgres and Akari instances.

## Usage
Upon the bot first being invited to your server, you must first run the following slash commands from a user with administrator permissions.
`/admin [admin-role]`
Sets the role that is allowed to perform administrative actions on the bot. 
`/user [user-role]` 
Sets the role that is allowed to use the bot.
`/thread [thread-channel]`
Sets the channel that the bot will create threads in.
`/fetch`
Manually performs an initial fetch of the proposal queue.

You will not need to run these commands again unless your database is lost.

