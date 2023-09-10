# Hermes Ticket Manager

# What is Hermes?

It's a discord bot that helps assistants to logs, keep a trace a ticket status, and other tools for managing tickets. It
also provides trace tickets when student want to report something the staff team.

# Installation

Use the docker-compose file to run the bot.
Database uses postgresql to store the data.

```yaml
version: "3"
services:
  hermes_ticket1:
    image: ghcr.io/renaud-dov/hermes:main
    container_name: hermes
    volumes:
      - /path/to/your/config:/app/config:ro
    restart: unless-stopped
    environment:
      - DISCORD_TOKEN=YOUR_DISCORD_TOKEN # discord token
      - BITLY_TOKEN=OPTIONAL # for shortening links in google search
      - DB_HOST=$DB_HOST # database host
      - DB_DATABASE=$DB_DATABASE # database name
      - DB_USERNAME=$DB_USERNAME # database username
      - DB_PASSWORD=$DB_PASSWORD # database password
      - DB_PORT=$DB_PORT # database port
```

# Configuration

The configuration file is in the config folder.
The file is in yaml format.

You can use the schema.json file to validate your configuration file with your
IDE: [https://raw.githubusercontent.com/Renaud-Dov/Hermes/main/schema.json](https://raw.githubusercontent.com/Renaud-Dov/Hermes/main/schema.json)

```yaml
groups: # discord roles id
  - &ASSISTANT 123456789012345678

users: # discord user id
  - &userME 123456789012345678

tags: # discord forum tags
  - &TPS1 1038739269008764958 # S1 TP C#

managers: # set the managers of the bot that can use the special commands
  - category: "Assistant"
    message: Ticket has been closed by an assistant.
    roles: # allowed roles
      - *ASSISTANT
    users: # allowed users
      - *userME
forums:
  - prog:
      id: 1019955558851289208 # forum id
      end_tag: "Closed" # tag to add when the ticket is closed
      webhook_channel: 1039665019090124900 # channel where the logs are sent
      practicals_tags: # used to add automatically the tag to the ticket when missing
        - id: *TPS1
          from: "2023-02-13 10:42:00" # date from when the tag is added, must be in the format: "YYYY-MM-DD HH:MM:SS"
          to: "2023-02-20 10:41:59"

tickets:
  EXAM:
    open_tag: false # if true, users can use this tag to open trace tickets
    groups:
      - *ASSISTANT
    category_channel: 1040023558535000084 # category where the tickets are created
    webhook_channel: 1040188840557682740 # channel where the logs are sent

extra_commands:
  - name: git
    description: "Link to the git tutorial."


    message: # [optional]
    embeds: # max of 10 embeds
      - title: "Git tutorial"
        description: "My git tutorial"

```

To set up properly the discord forum, you should:

- Create a tag that will be used to mark the tickets as closed (only forum moderators should be able to use this tag)
- You should turn on the option `Require people to select tags when posting` in the forum settings.

Commands are available by everyone, so you must set up the permissions of the bot in the discord server.
See https://support.discord.com/hc/en-us/articles/10952702911639-Command-Permissions-Lockout for more information.

# Commands

## For students and assistants

### Ticket creation

For students, basic tickets commands are directly triggered by the bot when a new discord post is created.
If practical tag is missing from the ticket, the bot will add it automatically.
Each ticket has an unique id, that is used to identify the ticket.

### /trace

Student can open new trace tickets using /trace command, followed by the tag provided by the assistants.
If the tag is incorrect or user doesn't have the permission to use the specified tag, the bot will send an error
message, listing the available tags.

### Extras

#### /google

Just a troll command that use letmegooglethat.com to search on google.
You'll need a bitly token to use this command, in order to shorten the link.

## For assistants

Assistants can use the following commands to manage the tickets, and trace tickets.

### /close

Inside a ticket thread, assistants can use the /close command to close the ticket.
When closed, thread is locked, so no one can post in it anymore. However, creator of the ticket can reopen it from bot
DM.
There are few optional options to use with this command:

- type:
    - `Resolve` (default): the ticket is marked as resolved
    - `Duplicate`: the ticket is marked as duplicate, and warn the user that he should read the other tickets before
      opening a new one.
    - `Delete`: the ticket is deleted (a copy of all messages is sent to the assistant in the logs channel)
    - `ForceResolve`: the ticket is marked as resolved, but user won't be able to reopen it.
- reason: the reason why the ticket is closed.

### /rename

Inside a ticket thread, assistants can use the /rename command to rename the ticket, instead of going to the thread
settings.
It's also useful because the bot will keep the ticket id in the title.

### /close_all

Close all the tickets of a specific tag.
> Tag parameter must be tag ID.

If not tag is specified, then it lists all the tags ids.

### /close_trace

Inside a trace ticket channel, assistants can use the /close_trace command to close the ticket.
When closed, channel is deleted, so no one can post in it anymore.
All messages are saved in the logs channel.

### /link

Generate a link to the ticket, knowing the ticket id.
Works from any discord channel.

# Development

## Requirements

See requirements.txt for more information.
You also need a postgresql database running on your machine.

## Run

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python3 src/main.py
```

# License

```
Copyright 2023, Dov {BugBear} Devers

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

```
