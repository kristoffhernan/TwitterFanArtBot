import requests
from collections import defaultdict
import json
import os

'''
Class to perform actions on the data (adding, removing, saving)
'''


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
    # https://stackoverflow.com/questions/50013768/how-can-i-convert-nested-dictionary-to-defaultdict
    def defaultify(self, d):
        if not isinstance(d, dict):
            return d
        return defaultdict(lambda: defaultdict(dict), {k: self.defaultify(v) for k, v in d.items()})

    def save_to_json(self):
        json_folder_aws = '../../tmp/data/json'
        json_folder_wind = './tmp/data/json'
        json_filename = 'fan_art_data.json'

        self.check_folder_exists(json_folder_aws)
        with open(os.path.join(json_folder_aws, json_filename), 'a+') as json_file:
            try:
                # load the existing data into a dict and conver tot defaultdict
                file_data = json.load(json_file)
                file_data = self.defaultify(file_data)

                # update json with the api data
                for author_id, tweets in self.data.items():
                    for tweet_ids in tweets.values():
                        for tweet_id, values in tweet_ids.items():
                            file_data[f'{author_id}']['tweet_id'][f'{tweet_id}'] = values

                # moves file pointer to the beginning
                json_file.seek(0)

            # loading an empty json will prod err
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

    # save images in a tweet
    def save_imgs_by_user(self, imgs_info, author_id):
        author_folder_aws = f'../../tmp/data/images/{author_id}'
        author_folder_wind = f'./tmp/data/images/{author_id}'

        for key, img in imgs_info.items():
            key_filename = f'{key}.jpg'
            with open(os.path.join(author_folder_aws, key_filename), 'wb') as handler:
                handler.write(img)
                handler.close()
            print(f'Img: {key} saved')

    # save all user images
    def save_all_users_media(self):
        # loop through tweet data
        for author_id, tweets in self.data.items():
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
                    # continue to next tweet
                    continue

                else:
                    imgs_info = dict(zip(tweet['media_keys'], imgs_data))

                    # create folder
                    author_folder_aws = f'../../tmp/data/images/{author_id}'
                    author_folder_wind = f'./tmp/data/images/{author_id}'
                    self.check_folder_exists(author_folder_aws)

                    # saving images by author
                    self.save_imgs_by_user(imgs_info, author_id)
