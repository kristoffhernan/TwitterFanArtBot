#### [Website](https://twitter.com/TTArtBot)

#### Description: 
[Trash Taste](https://www.youtube.com/c/TrashTaste/videos) is a highly anticipated anime podcast exploring anime, manga, and otaku culture with top anime YouTubers Joey from the The Anime Man, Garnt from Gigguk, and Connor from Cdawgva and occasionally special guests.

Each year, the podcast hosts an award ceremony to showcase highlights, guests, memes and more. During the 2021 ceremony, there was a section displaying various fan illustrations.

My idea was to create a twitter account that would like and retweet fan art related to Trash Taste. This would provide a space for fans to view all illustrations in one place. I also wanted to save the art in a folder so admins wouldn't have to manually scroll through hundreds of photos and save each image to then display on a website, poll or video.

#### Automation:
Because I have the "Elevated Access" twitter API, I only have access to data from 7 days previous. However, using AWS or Windows Task Scheduler you can run the script once every 7 days. 

For AWS:
1. Create a lambda function
2. Import [lambda.zip](lambda.zip) as the source code
3. Add a trigger, 'EventBridge (CloudWatch Events)
4. Set a cron trigger to run once a week e.g. (cron(30 15 ? * 2 *) to run at 1530 GMT every Monday)


#### Before Using:
- Change the environment variables for the `API_KEY`, `API_SECRET`, `BEARER_TOKEN`, `ACCESS_TOKEN`, `TOKEN_SECRET`, `GMAIL_APP_PASS`, `EMAIL_ADDRESS`, `CC_EMAIL_ADDRESS`

- Set up a [Google App Password](https://support.google.com/accounts/answer/185833?hl=en)


#### Change Query:
If you want to change the search [query](https://github.com/kristoffhernan/TwitterFanArtBot/blob/f5675f01f4950222fdc7bb8f12f67c3bc56413f1/TwitterBot.py#L32) for a different creator, subject or hashtags look into this github [page](https://github.com/twitterdev/getting-started-with-the-twitter-api-v2-for-academic-research/blob/main/modules/5-how-to-write-search-queries.md)



