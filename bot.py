import tweepy
import os, time, json
import planet
from datetime import datetime, timedelta


def load_data(path) :
    file_data = "";
    with open(path, 'r') as file :
        file_data = file.read()
    return file_data    


def save_json(path, data) :
    data = json.dumps(data);
    with open(path, 'w+') as file :
        file.write(data)


def load_json(path) :
    data = load_data(path)
    data = json.loads(data)
    return data

def format_time(my_time) :
    return time.strftime('%d-%m-%Y %H:%M:%S', time.localtime(my_time))

class bot() :
    def __init__(self) :
        try:
            self.keys = load_json(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'keys.json'))
            self.auth = tweepy.OAuthHandler(self.keys['consumer_key'], self.keys['consumer_secret'])
            self.auth.secure = True
            self.auth.set_access_token(self.keys['access_token'], self.keys['access_token_secret'])    

            self.api = tweepy.API(self.auth)  
            print('>>   log info:', self.api.me().name, self.api.me().id)
            print('++   connection established')
            now = datetime.now()
            last_midnight = time.mktime(now.replace(hour=0, minute=0, second=0, microsecond=0).timetuple())
            seconds_since_midnight = (time.time() - last_midnight)

            #### SETUP AREA ####
            self.sleep_time = 60                #how long to sleep since last call
            start_time = 14 * 60 + 22 * 60 * 60 # what time of day to start
            ####

            expected_start = last_midnight + start_time
            self.next_wake = expected_start if expected_start + 60 > time.time() else expected_start + 24 * 60 * 60
            print(">>   start scheduled on", str(format_time(self.next_wake)))

        except BaseException as e:
            print('--   error while connecting', e)


    def media_tweet(self, name) :
        status_text = "planet {}".format(name[:-4])
        print(">>   tweeting: ", status_text)
        path = os.path.join(os.path.dirname(os.path.realpath(__file__)), name)
        print(">>   file path: ", path)
        try :
            self.api.update_with_media(path, status=status_text)
            print("++   planet", name, "tweeted")
        except :
            print('--   error while tweetng, try to debug...')

        os.remove(path)



    def create_image(self) :
        print(">>   creating planet values")
        my_planet = planet.random_planet()
        print("++   planet", my_planet)
        print(">>   creating scene")
        my_scene = planet.scene()
        print("++   scene", my_scene)
        print(">>   generating name")
        name = planet.planet_to_hex(my_planet)
        print(">>   creating planet image")
        planet.planet(my_planet, my_scene, name)
        print("++   planet", name, "created")
        return name + ".png"

    def rutine(self) :
        while True :
            print("++   we are awake and it's", str(format_time(time.time())), "- time to tweet!")
            file_name = self.create_image()
            self.media_tweet(file_name)
            self.next_wake += self.sleep_time
            print(">>   setting alarm on",  str(format_time(self.next_wake)))
            time.sleep(self.next_wake - time.time())




planet_dreamer = bot()
planet_dreamer.rutine()