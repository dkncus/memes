#Instagram Interface Dependencies
import instabot				#Direct interface with Instagram API

#Reddit Interface Dependencies
import requests				#Handles web requests
import requests.auth 		#Handles authorization requests
import praw					#Python Reddit API Wrapper

#Image Fetching and Processing libraries
import pytesseract			#Extracts text from images
from PIL import Image 		#Dependency of Tesseract
import cv2					#Base image processing library
import urllib.request 		#For downloading images from image list

#Multithreading and Timing dependencies
import time					#Timing Library

#Dictionary of SubReddit pages with likelyhood of selection
subreddit_dict = {'dankmemes' : 0.35, 'memes' : 0.25, 'comedyheaven' : 0.10, 'comics' : 0.10, 'historymemes' : 0.10, 'deepfriedmemes' : 0.10}

#Log in and authenticate to Instagram, returns API object
def login_instagram():
	#Try logging in, if there is a problem, try again.
	try:
		#Instagram Username and Password, insta_keys[0] : Username, insta_keys[1] : Password
		insta_keys = ['username', 'password']
		fp = open(r'.\access_keys\passwords_i.txt', 'r')
		insta_keys[0] = fp.readline().rstrip('\n')
		insta_keys[1] = fp.readline().rstrip('\n')
		print("-Using Login Credentials-\n\tUsername :", insta_keys[0], "\n\tPassword :", insta_keys[1])
		fp.close()

		#Create an bot object and authenticate it to the Instagram platform
		print("Starting Instagram login...")
		instagram_credential = instabot.Bot()
		instagram_credential.login(username = insta_keys[0], password = insta_keys[1])
		print("Instagram login successful.")
		return insta_keys, instagram_credential
	except:
		print("ERROR :::> Instagram Login Failed. Retrying in 10 seconds...")
		time.sleep(10)
		return login_instagram()

#Log in and authenticate to Reddit, returns API object
def login_reddit(authorized = False):
	#Try logging in, if there is a problem, try again.
	try:
		#Load in authentication information
		reddit_keys = ['public', 'secret']
		reddit_login = ['username', 'password']
		#Load Reddit authentication keys
		fp = open(r'.\access_keys\keys_r.txt', 'r')
		reddit_keys[0] = fp.readline().rstrip('\n')
		reddit_keys[1] = fp.readline().rstrip('\n')
		#Load Reddit login information
		fp = open(r'.\access_keys\passwords_r.txt', 'r')
		reddit_login[0] = fp.readline().rstrip('\n')
		reddit_login[1] = fp.readline().rstrip('\n')
		fp.close()

		#Will be filled with Reddit object
		api_r = None

		#Create an API object to authenticate to Reddit
		print("Creating Reddit API object...")
		if authorized == True: #Create an Authorized (READ-ONLY) instance of the API object
			api_r = praw.Reddit(client_id = reddit_keys[0], 
								client_secret = reddit_keys[1], 
								user_agent = "ChangeMeClient/0.1 by " + reddit_login[0],
								username = reddit_login[0],
								password = reddit_login[1])
		else:
			api_r = praw.Reddit(client_id = reddit_keys[0], 
								client_secret = reddit_keys[1], 
								user_agent = "ChangeMeClient/0.1 by " + reddit_login[0])

		print("API Object successfully created.")

		#Return necessary information
		return reddit_login, api_r, reddit_keys
	except:
		print("ERROR :::> Reddit Login Failed. Retrying in 10 seconds...")
		time.sleep(10)
		return login_reddit()

#Posts a given photo to instagram with a specified caption
def post_photo_to_instagram(api_i, photo_path, caption_text):
	#Using instagram API,  
	api_i.upload_photo(photo_path, caption = caption_text)
	return 0

#Fetches the text from a meme
def get_text_from_photo(photo_path):
	image = cv2.imread(photo_path)
	return image

#Get the top hot image links from a given subreddit
def get_links_and_captions(api_r, subreddit, count):
	#Specify given subreddit
	sub = api_r.subreddit(subreddit)

	#Filled with URL's to meme and their respective top comment
	memes = {}

	#Find all memes within a given criteria on the subreddit's current hot page
	for meme in sub.hot(limit=30):
		img = meme.url
		#Check if the image is a .png or .jpg image and whether it is NSFW marked
		if (".jpg" in img) and not (meme.over_18):
			#Pair meme and top comment together in dict object
			memes[img] = meme.comments[0].body

	return memes

#Download a given list of memes
def download_list(meme_list):
	#For each meme in the list
	for i, meme in enumerate(meme_list):
		#Create unique title for each meme
		title = r"./meme_queue/" + str(i) + ".jpg"
		#Download the meme into the meme queue folder
		urllib.request.urlretrieve(meme, title)
	return 0

if __name__ == '__main__':
	#Authenticate to Instagram
	login_i, api_i = login_instagram()

	#Authenticate to Reddit and create/connect API object
	login_r, api_r, keys_r = login_reddit(authorized = True)

	memes_links = get_links_and_captions(api_r, 'dankmemes', 30)

	download_list(memes_links)