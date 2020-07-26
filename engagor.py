#Instagram Interface Dependencies
from instapy import InstaPy			#Direct interface with Instagram API

#Utilities
import random
import time

access_keys_i_loc = r'.\access_keys\passwords_i.txt'

class Engagor:
	#Initialization Function
	#	INSTA KEYS and API_I must be passed to the method if CREATE_API is set to False
	def __init__(self, access_keys_i_loc, create_api = True, insta_keys = [], api_i = None):
		self.access_keys_i_loc = access_keys_i_loc
		if create_api:
			#Create a new API object to use
			self.insta_keys, self.api_i = self.login_instagram()
		else:
			#Require that create_api be set to true, or pass insta_keys and api_i to the method
			assert api_i != None, "API must either be created by setting 'create_api' to True, or passing 'insta_keys' and 'api_i' to the __init__ method"
			assert len(insta_keys) != 0, "API must either be created by setting 'create_api' to True, or passing 'insta_keys' and 'api_i' to the __init__ method"

			self.insta_keys = insta_keys
			self.api_i = api_i

	#Return the Instagram Authentication and API object
	def login_instagram(self):
		#Instagram Username and Password, insta_keys[0] : Username, insta_keys[1] : Password
		insta_keys = ['username', 'password']
		fp = open(self.access_keys_i_loc, 'r')
		insta_keys[0] = fp.readline().rstrip('\n')
		insta_keys[1] = fp.readline().rstrip('\n')
		print("-Using Login Credentials-\n\tUsername :", insta_keys[0], "\n\tPassword :", insta_keys[1])
		fp.close()

		#Create an bot object and authenticate it to the Instagram platform
		print("Starting Instagram login...")
		instagram_credential = InstaPy(username = insta_keys[0], password = insta_keys[1], headless_browser = True)
		print("Instagram login successful.")
		return insta_keys, instagram_credential

	#Search for a given tag
	def search_tags(self, tag):
		return 0

if __name__ == '__main__':
	engagor = Engagor(access_keys_i_loc)
	page_to_follow = 'memes'

	engagor.api_i.set_do_like(enabled = True, percentage = 70)
	engagor.api_i.set_smart_hashtags(['meme', 'memes'], limit = 5, sort = 'random', log_tags = True)

	engagor.api_i.like_by_tags(amount = 25, use_smart_hashtags = True)