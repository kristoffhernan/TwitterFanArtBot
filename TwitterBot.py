import tweepy
import config
from ArtInstance import Art
import SendEmail
import os
from datetime import date, timedelta


'''
The main python file of the twitter bot. Autheticates, grab tweets, query them,
save img data, and sends imgs through email.
'''


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


# search for tweets based on the query field
def search_tweets():
    client = auth_client()

    query = "(@TrashTastePod OR #TrashTaste) (#trashtasteart OR #art OR #fanart OR #digitalart OR #illustration OR #drawing) -is:retweet has:media"

    # with Essential access, can only search through past 7 days of tweets, max of 100
    tweets = client.search_recent_tweets(query=query, tweet_fields=['entities'],
                                         media_fields=['url'], expansions=['attachments.media_keys', 'author_id'],
                                         max_results=100)
    return tweets


# loop through tweets, saving necessary data, liking and retweeting
def query_tweets(tweets, client, art_class):
    media = {m.media_key: m for m in tweets.includes['media']}
    users = {user.id: user.username for user in tweets.includes['users']}

    try:
        # query tweets
        for tweet in tweets.data:
            media_keys = tweet.attachments['media_keys']
            media_urls = [media[key].url for key in media_keys]
            media_types = [media[key]['type'] for key in media_keys]

            author_id = tweet.author_id
            username = users[author_id]
            tweet_id = tweet.id
            tweet_url = tweet.entities['urls'][0]['display_url']

            # add data to dict
            art_class.add_art(author_id=author_id, tweet_id=tweet_id,
                              media_keys=media_keys, media_urls=media_urls, media_types=media_types, tweet_url=tweet_url, username=username)

            # liking and retweeting
            client.like(tweet.id, user_auth=True)
            client.retweet(tweet.id, user_auth=True)

    # if dict is empty, will return err
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

    # directory variables
    cwd = os.getcwd()
    tmp_folder = os.path.join(cwd, 'tmp')
    data_folder = os.path.join(tmp_folder, 'data')
    zip_folder = os.path.join(tmp_folder, 'zip')

    # compress data dir as zip file
    today = date.today()
    last_week = date.today() - timedelta(days=7)
    zip_filename = f'TT-Data-{last_week}-{today}.zip'

    SendEmail.check_folder_exists(zip_folder)
    SendEmail.zip_dir(data_folder, zip_folder, zip_filename)

    SendEmail.send_email(zip_folder, zip_filename,
                         config.EMAIL_ADDRESS, config.GMAIL_APP_PASS, config.CC_EMAIL_ADDRESS)

    SendEmail.remove_folder_contents(data_folder)
    SendEmail.remove_folder_contents(zip_folder)


if __name__ == '__main__':
    main()
