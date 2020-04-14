# Spotify Remix Remover
Removes remix tracks from any Spotify generated playlist such as Recent Releases or Discover Weekly.
You can also specify additional keywords to filter out songs. 

## Why?
Sometimes the spotify generated playlists contain a large amount of remixes that I'm not really interested in hearing.
Also Spotify is aware that many people want the feature but did not implement it for a while and it doesnt look like
it's gonna happen anytime soon. 
See [here](https://community.spotify.com/t5/Closed-Ideas/All-Platforms-Discover-Filter-Remixes-amp-Covers/idi-p/4675160)
and [here](https://community.spotify.com/t5/Closed-Ideas/Release-Radar-Exclude-Remixes-amp-Covers-from-Release-Radar/idi-p/3888745)

## How to use it
0. Install dependencies (pip install -r requirements.txt)
1. register as a developer for spotify and register an application 
2. rename sample_remover_params.conf to remover_params.conf and fill in the fields
3. run python remove_remixes.py (You only need to authorize the app once)
4. repeat as desired or setup a cron job for once a week(or whatever the update cycle of your playlist type is) 


## Possible Improvements
1. print statistics e.g. How many songs where removed etc.
2. Make the script usable for non developers e.g set up flask plus a small frontend etc. and host it somewhere 