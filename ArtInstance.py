import requests
from collections import defaultdict
import json
import os


class Art:
    def __init__(self):
        # https://stackoverflow.com/questions/19189274/nested-defaultdict-of-defaultdict
        #  gives infinite default dictionaries
        def rec_dd():
            # use defaultdict because it creates any items even if the key doesnt exist
            # base dict will give a key error if you try to get a value for which a key doesnt already exist
            return defaultdict(rec_dd)
        self.data = rec_dd()

    # appends tweet info into a dictionary
    def add_art(self, author_id, tweet_id, media_keys, media_urls, media_types, tweet_url, username):
        self.media_urls = media_urls
        self.media_keys = media_keys
        self.media_types = media_types

        self.data[author_id]['tweet_id'][tweet_id] = {
            'media_keys': media_keys,
            'media_urls': media_urls,
            'media_types': media_types,
            'tweet_url': tweet_url,
            'username': username
        }

    def print_data(self):
        print(self.data)

    # checks if a folder exists, if not it makes one
    def check_folder_exists(self, out_folder):
        if not os.path.exists(out_folder):
            os.makedirs(out_folder)
    
    # convert already made dict into a nested default dict
    def defaultify(self, d):
        if not isinstance(d, dict):
            return d
        return defaultdict(lambda: defaultdict(dict), {k: self.defaultify(v) for k, v in d.items()})

    def save_to_json(self):
        self.check_folder_exists('./data/')
        with open('./data/fan_art_data.json', 'a+') as json_file:
            try:
                # load the existing data into a dict
                file_data = json.load(json_file)
                file_data = self.defaultify(file_data)
                # update file with the api data
                for author_id, tweets in self.data.items():
                    for tweet_ids in tweets.values():
                        for tweet_id, values in tweet_ids.items():
                            file_data[f'{author_id}']['tweet_id'][f'{tweet_id}'] = values

                # moves file pointer to the beginning
                json_file.seek(0)
            except json.decoder.JSONDecodeError as err:
                print(f'Json is empty: {err}')
                print(f'Creating new json file')
                # convert to json
                json.dump(self.data, json_file, indent=4)
            else:
                # convert to json
                json.dump(file_data, json_file, indent=4)

            finally:
                print('Json saved')
                json_file.close()

    def save_imgs_by_user(self, imgs_info, id):

        for key, img in imgs_info.items():

            with open(f'./images/{id}/{key}.jpg', 'wb') as handler:
                handler.write(img)
                handler.close()
            print(f'Img: {key} saved')

    def save_all_users_media(self):
        # loop through tweet data
        for id, tweets in self.data.items():
            for tweet in tweets['tweet_id'].values():
                try:
                    # convert urls to content
                    imgs_data = [requests.get(
                        url).content for url in tweet['media_urls']]

                # as of 4/22/22 videos don't have media so their urls are returned as none
                # requests.get(none) return an err
                except requests.exceptions.MissingSchema as e:
                    print(
                        f"media key:{tweet['media_keys']}, {tweet['tweet_url']} is a video: {e}")
                    continue

                else:
                    imgs_info = dict(zip(tweet['media_keys'], imgs_data))

                    # create folder
                    self.check_folder_exists(f'./images/{id}')

                    # saving image
                    self.save_imgs_by_user(imgs_info, id)
