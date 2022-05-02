# Speckle Server - Plugin Library

Speckle is open source which is amazing. However, what if I want to extend the functionality or play with my data a little bit? Many desired functionalities are user-specific and don't warrent being pulled into the master github repo. Not to mention that forking the repo and spinning up a local server can be difficult and intimidating for people who aren't programmers (aka most of speckle's target userbase). This is where plugins come in. Plugins (add-ons, extensions, etc.) are an extremely important functionality that make OSS more useable and accessable which is the reason that it is hard to find an OSS that hasn't implemented a plugin system.

Plugins are also a way that many people monetize their OSS. The library could be developed into more of a 'market place' where user could add their plugins for free or for a price, and Speckle would take a percentage of each sale. 

I think this is really important so I created the bones of a plugin system for Speckle. This is just for demo and not how this would be done in production. The script currently searchs the npm registry for any script with the tag 'speckle-plugin' of which there is currently only one (mine). You can then download it and run the javascript inside the 'dist' folder.

Here is a demo of a plugin that I made to show data from my custom FEM mesh objects.

![pluginDemo](https://user-images.githubusercontent.com/43247197/166297122-db82a74e-fa39-4e2c-99a8-a38221de0922.gif)
