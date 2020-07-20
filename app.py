#Instagram Interface Dependencies
import instabot				#Direct interface with Instagram API

#Reddit Interface Dependencies
import requests				#Handles web requests
import requests.auth 		#Handles authorization requests
import praw					#Python Reddit API Wrapper

#Image Fetching, Processing, and Text Extraction libraries
import pytesseract			#Extracts text from images
from PIL import Image 		#Dependency of Tesseract / Image Processing for Watermarks
from PIL import ImageDraw	#Watermarking
from PIL import ImageFont	#Watermarking
import cv2					#Base image processing library
import urllib.request 		#For downloading images from image list

#Multithreading and Timing dependencies
import time					#Timing Library
from datetime import datetime, timedelta #For timing next meme post
import threading 			#Threading for timing until next post

#File management dependencies
import os					#Basic file management system
from os import listdir		
from os.path import isfile	
from os.path import join	
import shutil				#For moving files to new file locations

#CONSTANTS AND SHARED DATA
#Dictionary of SubReddit pages with likelyhood of selection
subreddit_dict = {'dankmemes' : 0.35, 'memes' : 0.25, 'comedyheaven' : 0.10, 'comics' : 0.10, 'historymemes' : 0.10, 'deepfriedmemes' : 0.10}

#Key phrases and words to avoid when harvesting memes
keyphrases = [	'reddit', 'mods', 'mod', 
				'u/', 'u\\', 'r/', 'r\\', 
				'instagram', 'normie', 'insta', 
				'awards', 'award', 'karma', 
				'mematic', 'upvote', 'arrow', 
				'updoot', 'orange', 'redditor', 'downvote']

#Pytesseract (Text Extraction) necessary files
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract' #Setup for Pytesseract program files

#Location where meme images and already posted images are stored
image_queue_loc = r'.\meme_queue'
posted_loc = r'.\posted_photos'

#Posting Times (For Threading)
posting_times = {0 : [6, 10, 22], 	#Monday
				 1 : [2, 4, 9], 	#Tuesday
				 2 : [7, 8, 23], 	#Wednesday
				 3 : [9, 12, 19], 	#Thursday
				 4 : [5, 13, 15], 	#Friday
				 5 : [11, 19, 20], 	#Saturday
				 6 : [7, 8, 16]} 	#Sunday

#THREADING METHODS
#====================================================================
#Creates a post
def create_post(api_r, api_i, download_count = 30, subreddit = 'memes', timed = False):
	#Get links to current most popular meme from dankmemes and download to file location
	memes_links = get_links_and_captions(api_r, subreddit, download_count)
	image_captions = download_list(memes_links, image_queue_loc)

	#Watermark each image in the directory
	dirs = os.listdir(image_queue_loc)
	for img in dirs:
		watermark_image(image_queue_loc + '\\' + img, login_i[0])

	#Filter memes for keyword phrases and duplicated
	filter_memes_keywords_aspectratio(keyphrases, image_queue_loc)

	#Post the first non-duplicate meme in the file directory with appropriate caption
	dirs = os.listdir(image_queue_loc)
	post_photo_to_instagram(api_i, image_queue_loc + '\\' + dirs[0], caption_map[dirs[0]] + " - dave")

	clear_meme_queue(image_queue_loc)

	#Wait until next time slot, and then post again
	time = get_time_until_next_post()
	threading.Timer(time, create_post, [api_r, api_i, download_count, subreddit, True]).start()

#Gets the time until the next post in seconds
def get_time_until_next_post():
	#Get the current time and day, and create a tomorrow object
	today = datetime.today() #YYYY-MM-DD HH:MM:SS.UUUUUU
	weekday = today.weekday()
	tomorrow = today + timedelta(days = 1)
	w_tomorrow = tomorrow.weekday()

	#Get posting times for today's day of the week
	timeset = posting_times[weekday]

	#Convert all posting times into a datetime object, incl. the first posting time of the next morning
	possible_future_times = []
	for hour in timeset:
		update = datetime(today.year, today.month, today.day, hour, 0, 0)
		possible_future_times.append(update)
	#	incl. the first posting time of the next morning
	hour = posting_times[w_tomorrow][0]
	tomorrow_first = datetime(tomorrow.year, tomorrow.month, tomorrow.day, hour, 0, 0)
	possible_future_times.append(tomorrow_first)

	#find closest time to current time for next post
	today = datetime.today()
	timeslot = -1
	for i, time in enumerate(possible_future_times):
		if time > today:
			print("Next post in", time - today)
			timeslot = i
			break

	#Time until the next future timeslot
	time_until_next = possible_future_times[timeslot] - datetime.now()
	print("Time until next timeslot -", time_until_next)
	return time_until_next.seconds
#====================================================================

#LOGIN/SETUP METHODS
#====================================================================
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
#====================================================================

#INSTAGRAM/REDDIT INTERACTION METHODS
#====================================================================
#Posts a given photo to instagram with a specified caption
def post_photo_to_instagram(api_i, photo_path, caption_text):
	#Using instagram API,  
	api_i.upload_photo(photo_path, caption = caption_text)
	return 0

#Get the top hot image links from a given subreddit
def get_links_and_captions(api_r, subreddit, count):
	print("Downloading images from Reddit...")
	#Specify given subreddit
	sub = api_r.subreddit(subreddit)

	#Filled with URL's to meme and their respective top comment
	memes = {}

	#Find all memes within a given criteria on the subreddit's current hot page
	for meme in sub.hot(limit = count):
		img = meme.url
		#Check if the image is a .png or .jpg image and whether it is NSFW marked
		if (".jpg" in img) and not (meme.over_18) and meme.num_comments > 0:
			#Pair meme and top comment together in dict object
			memes[img] = meme.comments[0].body

	return memes
#====================================================================

#MEME FILTERING METHODS
#====================================================================
#Filters out memes with a certain keyphrase in the image or outside of a specific range of aspect ratios
def filter_memes_keywords_aspectratio(keyword_list, queue_location, ar_limit = 1.3):
	print("Filtering images for keyphrases and aspect ratios")

	#Get file list from the queue location
	dirs = os.listdir(queue_location)

	#For each image listed in the directory
	for image in dirs:
		image_loc = queue_location + '\\'+ image
		#Get the body text of the meme
		body_text = read_meme(image_loc).lower()
		#Fetch the aspect ratio of the image
		aspect_ratio = get_aspect_ratio(image_loc)
		
		if aspect_ratio <= ar_limit:
			for keyword in keyword_list:
				#Check if any keyword appears in that body text, if so, remove it
				if keyword in body_text:
					os.remove(image_loc)
					#shutil.move(image_loc, (r'.\eliminated' + r'\\' + image )) #For checking which images were eliminated
					break
		else:
			os.remove(image_loc)
			#shutil.move(image_loc, (r'.\eliminated' + r'\\' + image ))

#Filter out memes that are duplicates of already posted photos or duplicates of photos already in the meme queue
def filter_memes_duplicates(queue_location):
	return 0
	#>>>>>>>>>>>>>>>>>>>>TODO<<<<<<<<<<<<<<<<<<<<<<<<<
#====================================================================

#UTILITIES
#====================================================================
#Fetches the text from a meme
def read_meme(photo_path):
	#Return pytesseract read text from meme
	return pytesseract.image_to_string(Image.open(photo_path), lang = 'eng')
	
#Download a given list of memes
def download_list(meme_list, folder_loc):
	caption_map = {}
	#For each meme in the list
	for i, meme in enumerate(meme_list):
		#Create unique title for each meme
		title = folder_loc + "\\" + str(i) + ".jpg"

		#Download the meme into the meme queue folder
		urllib.request.urlretrieve(meme, title)

		#Save the caption
		caption_map[title] = meme_list[meme]

	print("Downloaded images successfully.")
	return caption_map

#Return the aspect ratio of a given image file
def get_aspect_ratio(file):
	image = Image.open(file)
	width, height = image.size

	aspect_ratio = width / height

	if aspect_ratio < 1:
		aspect_ratio = height / width

	return aspect_ratio

#Watermark a given image - base code from https://medium.com/better-programming/add-copyright-or-watermark-to-photos-using-python-a3773c71d431
def watermark_image(file, account_name):
	image = Image.open(file)
	width, height = image.size
	
	drawing = ImageDraw.Draw(image)

	font_size = width // 30

	font = ImageFont.truetype("cmunss.ttf", font_size)

	text = "@" + account_name
	text_w, text_h = drawing.textsize(text, font)
	pos = width - text_w - 20, (height - text_h) - 20

	c_text = Image.new('RGB', (text_w, text_h))
	drawing = ImageDraw.Draw(c_text)

	drawing.text((0,0), text, fill="#ffffff", font=font)
	c_text.putalpha(100)

	image.paste(c_text, pos, c_text)
	image.save(file)

	return 0
#====================================================================

if __name__ == '__main__':
	#STARTUP/INITIALIZATION PHASE
	#----------------------------------------------------------------
	#Authenticate to Instagram and Reddit, create/connect API objects
	login_i, api_i = login_instagram()
	login_r, api_r, keys_r = login_reddit(authorized = True)
	#----------------------------------------------------------------

	#RUN PHASE
	#----------------------------------------------------------------
	create_post(api_r, api_i, download_count = 50)