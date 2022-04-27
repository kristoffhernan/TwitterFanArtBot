import tweepy
import config
from ArtInstance import Art


def auth_client():
    # authentification
    client = tweepy.Client(
        bearer_token=config.BEARER_TOKEN,
        consumer_key=config.API_KEY,
        consumer_secret=config.API_SECRET,
        access_token=config.ACCESS_TOKEN,
        access_token_secret=config.TOKEN_SECRET,
        wait_on_rate_limit=True,
    )
    return client


def search_tweets():
    client = auth_client()

    query = "(@TrashTastePod OR #TrashTaste) (#trashtasteart OR #art OR #fanart OR #digitalart OR #illustration OR #drawing) -is:retweet has:media"
    # query = "from:Herna_Kay has:media"

    tweets = client.search_recent_tweets(query=query, tweet_fields=['entities'],
                                         media_fields=['url'], expansions=['attachments.media_keys', 'author_id'],
                                         max_results=20)
    return tweets


def query_tweets(tweets, client, art_class):
    media = {m.media_key: m for m in tweets.includes['media']}
    users = {user.id: user.username for user in tweets.includes['users']}

    try:
        for tweet in tweets.data:
            media_keys = tweet.attachments['media_keys']
            media_urls = [media[key].url for key in media_keys]
            media_types = [media[key]['type'] for key in media_keys]

            author_id = tweet.author_id
            username = users[author_id]
            tweet_id = tweet.id
            tweet_url = tweet.entities['urls'][0]['display_url']

            art_class.add_art(author_id=author_id, tweet_id=tweet_id,
                              media_keys=media_keys, media_urls=media_urls, media_types=media_types, tweet_url=tweet_url, username=username)

            # client.like(tweet.id)
            # client.retweet(tweet.id)

    except TypeError as e:
        print(f'There are no recent fan arts, try again in 7 days: {e}')
    else:
        print('Query complete')


def save_tweet_media(art_class):
    # saves the images into a folder
    # saving images at end so the api doesnt stay open for long periods
    art_class.save_all_users_media()

    # saves author_id, tweet_id, media_keys, media_urls, media_types, tweet_url, username to a json
    art_class.save_to_json()


def main():
    # instance
    trash_taste_art = Art()
    client = auth_client()
    tweets = search_tweets()
    query_tweets(tweets, client, trash_taste_art)
    save_tweet_media(trash_taste_art)


if __name__ == '__main__':
    main()
