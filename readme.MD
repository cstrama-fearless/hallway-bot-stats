### Hallway Bot Stats

This is a Python 3 command line application to get the stats of the Hallway bot. This will get the users that have participated in Hallway conversations and how many times. It will also identify the most and least participated in conversations.

#### Requirements

Update the SLACK_API_TOKEN variable with your slack API token. Update the HALLWAY_BOT_ID and HALLWAY_USER_ID with the appropriate values for the Hallway Bot.

If using a legacy token, no action is needed. If using a Slack app token, the app needs the following permissions:

* channels:history
* channels:read
* identity
* users:read

#### Usage

On the command line:

$ python slack-conversations.py club-watercooler

### Output

A simple table:

UserId UserName Count<br/>
.<br/>
.<br/>
.<br/>

Total Hallway Participants:             count<br/>
Total Hallway Conversations:            count<br/>
Most participants in Conversation:      count<br/>
Most participated in Conversation:      datetime<br/>
Least participants in Conversation:     count<br/>
Least participated in Conversation:     datetime<br/>
