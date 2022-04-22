import tweepy
import config
import json
import requests
import os


class Art:
    def __init__(self):
        self.data = {}

    def add_art(self, author_id, tweet_id, media_keys, media_urls, media_types, tweet_url, username):
        self.media_urls = media_urls
        self.media_keys = media_keys
        self.media_types = media_types

        self.data[author_id] = {
            'tweet_id': {
                tweet_id: {
                    'media_keys': media_keys,
                    'media_urls': media_urls,
                    'media_types': media_types,
                    'tweet_url': tweet_url,
                    'username': username
                },
            },
        }

    def print_data(self):
        print(self.data)

    def save_to_json(self):
        with open('trash_taste_fan_art.json', 'w') as json_file:
            json.dump(self.data, json_file)

            json_file.close()

    def save_medias(self):
        # loop through dictionary
        for tweet in self.data.values():
            for info in tweet['tweet_id'].values():
                # videos don't have media urls and thus return none
                if info['media_urls']:
                    imgs_data = [requests.get(
                        url).content for url in info['media_urls']]
                    imgs_info = dict(zip(info['media_keys'], imgs_data))

                    # create folder
                    if not os.path.exists('fan_art'):
                        os.makedirs('fan_art')

                    # saving image
                    for key, img in imgs_info.items():
                        with open(f'./fan_art/{key}.jpg', 'wb') as handler:
                            handler.write(img)
                            handler.close()


trash_art = Art()

client = tweepy.Client(
    bearer_token=config.BEARER_TOKEN,
    consumer_key=config.API_KEY,
    consumer_secret=config.API_SECRET,
    access_token=config.ACCESS_TOKEN,
    access_token_secret=config.TOKEN_SECRET,
    wait_on_rate_limit=True,
)

query = "(@TrashTastePod OR #TrashTaste) (#trashtasteart OR #art OR #fanart OR #digitalart OR #illustration OR #drawing) -is:retweet has:media"

tweets = client.search_recent_tweets(query=query, tweet_fields=['entities'],
                                     media_fields=['url'], expansions=['attachments.media_keys', 'author_id'],
                                     max_results=10)


media = {m.media_key: m for m in tweets.includes['media']}
users = {user.id: user.username for user in tweets.includes['users']}

try:
    for tweet in tweets.data:
        # print(tweet['type'])
        media_keys = tweet.attachments['media_keys']
        media_urls = [media[key].url for key in media_keys]
        media_types = [media[key]['type'] for key in media_keys]

        author_id = tweet.author_id
        username = users[author_id]
        tweet_id = tweet.id
        tweet_url = tweet.entities['urls'][0]['display_url']

        trash_art.add_art(author_id=author_id, tweet_id=tweet_id,
                          media_keys=media_keys, media_urls=media_urls, media_types=media_types, tweet_url=tweet_url, username=username)

        # client.like(tweet.id)
        # client.retweet(tweet.id)
        pass

except TypeError as e:
    print(f'There are no recent fan arts, try again in 7 days: {e}')
else:
    print('Task complete')


# saving tweets at end so the api doesnt stay open for no reason
trash_art.save_medias()
# trash_art.save_to_json()
