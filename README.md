## Twitch Widget App
### Objective: 
To create a scrolling event ticker that included not just one type of stream event, but all types of stream events.
### Solution:
After some searching, the conclusion I came to was it would be easier and faster to write the widget myself.
### Why Python?
Because it's the language I am the most comfortable with at the moment and is what I plan on continuing to learn.

### What does this do exactly?
Given an easy to modify config.json file, it will use the Stream Elements API to get your personal channels event data. It will then parse that data and output a text file for you to use as and OBS text source. Apply a background color and a text color and boom, you have yourself an event ticker that scroll all events within the configs range limit. There is also a nice little tray icon so you can click to close the app down. Give it a moment to finish its job and it will close.

### How to use?
Make sure that you set your Stream Elements JWT token and Stream Elements channel id in the config.json console.
Run the twitch-widget-app.py script and it will start doing what it does.
In OBS create a new text source and use read from file.
Locate the file specified in the config.json 'label-file' which uses relative path to the script.
Select that label file and add a scroll to it with OBS Text Source properties.
Now you have a scrolling ticker of events that have recently happened.

### Why not directly use the Twitch API
To be honest, I'm new to APIs and the twitch API documentation was hard for me to follow and get setup. I do still plan on moving over to that API as well as include popular streamer API such as StreamLabs as well.
Stream Elements gave me the clearest cleanest API docs, so I used them.

### Event Messages
Event messages can be customized within the config.json file. The data retrieved and saved per event are 'name', and 'createdAt', also 'amount' depending on the event.
Use '%name' for the username of the user who triggered the event
Use '%amount' for the amount of the event the triggering user included.

The following events use %amount:
| Event | Amount meaning |
| :--- | :--- |
| subscribe | how many months the user has subscribed |
| host | how many users are watching from host |
| cheer | how many bits a user cheered |
| tip | how much the user tipped the streamer through Stream Elements |
| raid | how many users the raider has sent into your stream |
| superchat | how much user paid for superchat |
| charity | how much user donated to charity via Stream Elements |

** I do not currently have other sources aside from Twitch worked into this as I don't understand those platforms completely because I stream on Twitch.

** Technically my script also adds a 'type' to each of these, but currently aside from parsing the data there is no use case for this.

### TODO LIST
- [] I would like to add the output file as an optional HTML file, this would allow for some custom divs and behaviors using OBS Browser source
- [] event messages could be included within the templates
- [] Currently the event-checks listed in the config does nothing. event checks are hardcoded. Creating a more customizable setup would be awesome.
- [] Additional functionality of other APIs, youtube, twitch, streamlabs, pally.gg (when they have a public endpoint accessable)
