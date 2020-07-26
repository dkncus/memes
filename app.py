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
from threading import Timer

#File management dependencies
import os					#Basic file management system
from os import listdir		
from os.path import isfile	
from os.path import join	
import shutil				#For moving files to new file locations
import sys

#Utilities
import random
import re

#CONSTANTS AND SHARED DATA
#Dictionary of SubReddit pages with likelyhood of selection
subreddit_dict = {'memes' : 1.0}

#Key phrases and words to avoid when harvesting memes
keyphrases = [	'reddit', 'mods', 'mod', 
				'u/', 'u\\', 'r/', 'r\\', 
				'instagram', 'normie', 'insta', 
				'awards', 'award', 'karma', 
				'mematic', 'upvote', 'arrow', 
				'updoot', 'orange', 'redditor', 'downvote',
				'sort', 'cake']

#Pytesseract (Text Extraction) necessary files
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract' #Setup for Pytesseract program files

#Location where meme images and already posted images are stored
image_queue_loc = r'.\meme_queue\\'
posted_loc = r'.\posted_photos\\'

#Posting Times (For Threading) DAY : [[H, M, S], [H, M, S], [H, M, S]]

posting_times = {0 : [[6, 0, 0],  [10, 0, 0], [22, 0, 0]], 	#Monday
				 1 : [[2, 0, 0],  [4, 0, 0],  [9, 0, 0]], 	#Tuesday
				 2 : [[11, 0, 0], [13, 0, 0], [23, 0, 0]], 	#Wednesday
				 3 : [[9, 0, 0],  [13, 0, 0], [19, 0, 0]], 	#Thursday
				 4 : [[5, 0, 0],  [10, 0, 0], [11, 0, 0]], 	#Friday
				 5 : [[11, 0, 0], [19, 0, 0], [20, 0, 0]], 	#Saturday
				 6 : [[7, 0, 0],  [8, 0, 0],  [16, 0, 0]]} 	#Sunday

'''
#Spam/debug posting times
posting_times = {0 : [[0, 0, 0], [1, 0, 0], [2, 0, 0], [3, 0, 0], [4, 0, 0], [5, 0, 0], [6, 0, 0], [7, 0, 0], [8, 0, 0], [9, 0, 0], [10, 0, 0], [11, 0, 0], [12, 0, 0], [13, 0, 0], [14, 0, 0], [15, 0, 0], [16, 0, 0], [17, 0, 0], [18, 0, 0], [19, 0, 0], [20, 0, 0], [21, 0, 0], [22, 0, 0], [23, 0, 0]], 	#Monday
				 1 : [[0, 0, 0], [1, 0, 0], [2, 0, 0], [3, 0, 0], [4, 0, 0], [5, 0, 0], [6, 0, 0], [7, 0, 0], [8, 0, 0], [9, 0, 0], [10, 0, 0], [11, 0, 0], [12, 0, 0], [13, 0, 0], [14, 0, 0], [15, 0, 0], [16, 0, 0], [17, 0, 0], [18, 0, 0], [19, 0, 0], [20, 0, 0], [21, 0, 0], [22, 0, 0], [23, 0, 0]], 	#Tuesday
				 2 : [[0, 0, 0], [1, 0, 0], [2, 0, 0], [3, 0, 0], [4, 0, 0], [5, 0, 0], [6, 0, 0], [7, 0, 0], [8, 0, 0], [9, 0, 0], [10, 0, 0], [11, 0, 0], [12, 0, 0], [13, 0, 0], [14, 0, 0], [15, 0, 0], [16, 0, 0], [17, 0, 0], [18, 0, 0], [19, 0, 0], [20, 0, 0], [21, 0, 0], [22, 0, 0], [23, 0, 0]], 	#Wednesday
				 3 : [[0, 0, 0], [1, 0, 0], [2, 0, 0], [3, 0, 0], [4, 0, 0], [5, 0, 0], [6, 0, 0], [7, 0, 0], [8, 0, 0], [9, 0, 0], [10, 0, 0], [11, 0, 0], [12, 0, 0], [13, 0, 0], [14, 0, 0], [15, 0, 0], [16, 0, 0], [17, 0, 0], [18, 0, 0], [19, 0, 0], [20, 0, 0], [21, 0, 0], [22, 0, 0], [23, 0, 0]], 	#Thursday
				 4 : [[0, 0, 0], [1, 0, 0], [2, 0, 0], [3, 0, 0], [4, 0, 0], [5, 0, 0], [6, 0, 0], [7, 0, 0], [8, 0, 0], [9, 0, 0], [10, 0, 0], [11, 0, 0], [12, 0, 0], [13, 0, 0], [14, 0, 0], [15, 0, 0], [16, 0, 0], [17, 0, 0], [18, 0, 0], [19, 0, 0], [20, 0, 0], [21, 0, 0], [22, 0, 0], [23, 0, 0]], 	#Friday
				 5 : [[0, 0, 0], [1, 0, 0], [2, 0, 0], [3, 0, 0], [4, 0, 0], [5, 0, 0], [6, 0, 0], [7, 0, 0], [8, 0, 0], [9, 0, 0], [10, 0, 0], [11, 0, 0], [12, 0, 0], [13, 0, 0], [14, 0, 0], [15, 0, 0], [16, 0, 0], [17, 0, 0], [18, 0, 0], [19, 0, 0], [20, 0, 0], [21, 0, 0], [22, 0, 0], [23, 0, 0]], 	#Saturday
				 6 : [[0, 0, 0], [1, 0, 0], [2, 0, 0], [3, 0, 0], [4, 0, 0], [5, 0, 0], [6, 0, 0], [7, 0, 0], [8, 0, 0], [9, 0, 0], [10, 0, 0], [11, 0, 0], [12, 0, 0], [13, 0, 0], [14, 0, 0], [15, 0, 0], [16, 0, 0], [17, 0, 0], [18, 0, 0], [19, 0, 0], [20, 0, 0], [21, 0, 0], [22, 0, 0], [23, 0, 0]]} 	#Sunday
'''
#Below the caption (Hashtags, whatnot)
below_caption = "\n.\n.\n.\n Follow @suspectcrab for more!\n#meme #memes #funny #dankmemes #memesdaily #funnymemes #lol #follow #dank #humor #like #love #dankmeme #tiktok #lmao #instagram #comedy #anime #fun #dailymemes #memepage #edgymemes #offensivememes #memestagram #funnymeme #memer #fortnite #instagood #bhfyp"

access_keys_i_loc = r'.\access_keys\passwords_i.txt'
access_keys_r_loc = r'.\access_keys\keys_r.txt'

class Poster:
	#LOGIN/SETUP METHODS
	#====================================================================
	#Initialization method
	def __init__(	self, subreddit_dict, keyphrases, posting_times, below_caption,	fetch_random, #Required Positional Arguments
					auth = True, 													#Whether Reddit authorization is required
					access_keys_i_loc = r'.\access_keys\passwords_i.txt', 			#Location of Instagram username and password
					access_keys_r_loc = r'.\access_keys\keys_r.txt',				#Location of Reddit username and password
					image_queue_loc = r'.\meme_queue\\', 							#Location of Meme Queue (Image Folder for Queueing)
					posted_loc = r'.\posted_photos\\', 								#Photos that have previously been posted on the account
					download_count = 70, 											#Number of Reddit posts to download per cycle into Meme Queue
					subreddit = 'memes', 											#Subreddit to harvest from
					custom_caption = '',											#Caption that is used if 
					override_caption = False,										#
					ar_limit = 1.3):												#Acceptable Aspect Ratio limit

		self.subreddit_dict = subreddit_dict
		self.keyphrases = keyphrases
		self.image_queue_loc = image_queue_loc
		self.posted_loc = posted_loc
		self.posting_times = posting_times
		self.override_caption = override_caption
		self.custom_caption = custom_caption
		self.below_caption = below_caption
		self.default_caption = "Tag a friend who would laugh"
		self.access_keys_i_loc = access_keys_i_loc
		self.access_keys_r_loc = access_keys_r_loc
		self.fetch_random = fetch_random
		self.subreddit = subreddit
		self.download_count = download_count
		self.ar_limit = ar_limit
		self.login_i, self.api_i = self.login_instagram()
		self.account_name = self.login_i[0]
		self.account_pass = self.login_i[1]
		self.login_r, self.api_r, self.keys_r = self.login_reddit(authorized = False)
		
		print("Clearing Image Queue and Downloading Base Set...")
		self.clear_image_queue() #Cleans out the current image queue
		self.caption_map = self.download_and_augment() #Relevant captions to each image in the file directory
	
	#Log in and authenticate to Instagram, returns API object
	def login_instagram(self):
		#Try logging in, if there is a problem, try again.
		try:
			#Instagram Username and Password, insta_keys[0] : Username, insta_keys[1] : Password
			insta_keys = ['username', 'password']
			fp = open(self.access_keys_i_loc, 'r')
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
			return self.login_instagram()

	#Log in and authenticate to Reddit, returns API object
	def login_reddit(self, authorized):
		#Try logging in, if there is a problem, try again.
		try:
			#Load in authentication information
			reddit_keys = ['public', 'secret']
			reddit_login = ['username', 'password']
			#Load Reddit authentication keys
			fp = open(access_keys_r_loc, 'r')
			reddit_keys[0] = fp.readline().rstrip('\n')
			reddit_keys[1] = fp.readline().rstrip('\n')
			#Load Reddit login information
			fp = open(self.access_keys_r_loc, 'r')
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

	#Start base thread - Master Method
	def start(self):
		#Get time until the next post is scheduled
		time = self.get_time_until_next_post()
		#Start thread to countdown until next scheduled post, then post
		thread = Timer(time, self.create_post)
		thread.start()
		self.countdown(time, message = "Time before next post : ")
	#====================================================================

	#THREADING METHODS
	#====================================================================
	#Creates a post
	def create_post(self, num_posts = 4, start_next = True):
		print("\n", datetime.now(), ": STARTING NEW POST")

		#Post the photo
		print("Posting Photo(s)...")

		#Create and post num_posts posts
		for i in range(num_posts):
			dirs = os.listdir(image_queue_loc) #List all files in the directory

			#Get the closest to the top hottest non-eliminated post in the directory
			f = ''
			if self.fetch_random:
				for i in range(self.download_count):
					string_start = str(i) + "_"
					for entry in enumerate(dirs):
						if entry[1].startswith(string_start):
							f = entry[1]
							break
					if f != '':
						f = f.rstrip('\\')
						break
			else:
				f = dirs[0]
			
			print("Getting File:", f)

			#Generate a caption to the image
			caption_text = ""

			if not self.override_caption:
				#Get related caption on the caption map
				cap = self.caption_map[f]
				print(cap)
				caption_text = cap + self.below_caption 	#Get related caption from caption map
				for word in self.keyphrases: 				#Use a default caption if any of the keywords are mentioned
					if word in cap:							
						print("BEING REPLACED WITH DEFAULT CAPTION, WORD :", word)
						caption_text = self.default_caption  + self.below_caption
						break
			else:
				caption_text = self.custom_caption + self.below_caption #Use custom caption

			print(caption_text)
			#Post the actual photo to Instagram
			self.api_i.upload_photo(image_queue_loc + f, caption = caption_text)

			#Place the previously posted photo into the POSTED_LOC, so duplicates are not added
			try:
				os.rename(self.image_queue_loc + f + ".REMOVE_ME", self.posted_loc + f)
			except FileExistsError:
				os.remove(self.posted_loc + f)
				os.rename(self.image_queue_loc + f, self.posted_loc + f)
			except FileNotFoundError:
				os.rename(self.image_queue_loc + f, self.posted_loc + f)

			print("Photo posted.\n")

		#If fetching memes
		if self.fetch_random:
			#Select a subreddit to draw content from
			self.subreddit = self.choose_subreddit()

			#Queue a new set of memes from Reddit
			print("Downloading new set of images...")
			self.clear_image_queue()	#Clear the image queue (Delete all memes in queue)
			self.caption_map = self.download_and_augment() #Download, Watermark, and Filter memes in Image Queue folder
			print("New image set downloaded.")

		#Wait until next time slot, and then post again
		if start_next: 
			time = self.get_time_until_next_post()
			next_thread = Timer(time, self.create_post)
			next_thread.start()
			self.countdown(time, message = "Time before next post : ")
		else:
			print("System Exiting.")
		return 0

	#Download, Watermark, and Filter memes. Return corresponding captions.
	def download_and_augment(self):
		print("\tFetching links to download from...")
		memes_links = self.get_links_and_captions()
		print("\tDownloading images from links...")
		caption_map = self.download_list(memes_links, self.image_queue_loc)

		#Watermark each image in the directory
		self.watermark_images()

		#Filter memes for keyword phrases and duplicated
		self.filter_memes_keywords_aspectratio()
		self.filter_memes_duplicates()

		return caption_map
	#====================================================================

	#INSTAGRAM/REDDIT INTERACTION METHODS
	#====================================================================
	#Get the top hot image links from a given subreddit, reddit API, and count
	def get_links_and_captions(self):
		#Filled with URL's to meme and their respective top comment
		memes = {}

		#Find all memes within a given criteria on the subreddit's current hot page
		for meme in self.api_r.subreddit(self.subreddit).hot(limit = self.download_count):
			img = meme.url
			#Check if the image is a .png or .jpg image and whether it is NSFW marked
			if (".jpg" in img) and not (meme.over_18) and meme.num_comments > 0:
				#Pair meme and top comment together in dict object
				memes[img] = meme.comments[0].body

		return memes

	#Download a given list of memes
	def download_list(self, meme_list, folder_loc):
		caption_map = {}
		#For each meme in the list
		for i, meme in enumerate(meme_list):
			#Create unique title for each meme
			split = re.split("/", meme)
			image = str(i) + "_" + str(split[-1])
			title = folder_loc + image

			try:
				#Download the meme into the meme queue folder
				urllib.request.urlretrieve(meme, title)

				#Save the caption and meme
				print("\t\tImage", meme, "saved as", image)
				caption_map[image] = meme_list[meme]
			except:
				print("Failed to download image.")

		print("\tDownloaded images successfully.")
		return caption_map

	#====================================================================

	#IMAGE FILTERING METHODS
	#====================================================================
	#Filters out memes with a certain keyphrase in the image or outside of a specific range of aspect ratios
	def filter_memes_keywords_aspectratio(self):
		print("\tFiltering images for keyphrases and aspect ratios")
		queue_location = self.image_queue_loc

		#Get file list from the queue location
		dirs = os.listdir(queue_location)

		#For each image listed in the directory
		for image in dirs:
			image_loc = queue_location + image
			#Get the body text of the meme
			body_text = self.read_meme(image_loc).lower()
			#Fetch the aspect ratio of the image
			aspect_ratio = self.get_aspect_ratio(image_loc)
			
			if aspect_ratio <= self.ar_limit:
				for keyword in self.keyphrases:
					#Check if any keyword appears in that body text, if so, remove it
					if keyword in body_text:
						print("\t\tRemoved Image ", image_loc, " - Body text contains keyphrase '", keyword, "'", sep ='')
						os.remove(image_loc)
						#shutil.move(image_loc, (r'.\eliminated\\' + image )) #For Debugging
						break
			else:
				print("\t\tRemoved Image", image_loc, "- Out of Aspect Ratio")
				os.remove(image_loc)
				#shutil.move(image_loc, (r'.\eliminated\\' + image )) #For Debugging

	#Filter out memes that are duplicates of already posted photos or duplicates of photos already in the meme queue
	def filter_memes_duplicates(self):
		queue_directory = os.listdir(self.image_queue_loc)
		posted_directory = os.listdir(self.posted_loc)

		for queue_file in queue_directory:
			search = re.split("_", queue_file)[1]
			for posted_file in posted_directory:
				if search in posted_file:
					file = self.image_queue_loc + queue_file
					os.remove(file)
					print("\t\tRemoved", file, "- Duplicate post detected.")
		return 0
	#====================================================================

	#UTILITIES
	#====================================================================
	#Fetches the text from a meme
	def read_meme(self, photo_path):
		#Return pytesseract read text from meme
		return pytesseract.image_to_string(Image.open(photo_path), lang = 'eng')
		
	#Return the aspect ratio of a given image file
	def get_aspect_ratio(self, file):
		image = Image.open(file)
		width, height = image.size

		aspect_ratio = width / height

		if aspect_ratio < 1:
			aspect_ratio = height / width

		return aspect_ratio

	#Watermark all images in a given folder
	# - base code from https://bit.ly/3hjMh36
	def watermark_images(self):
		dirs = os.listdir(self.image_queue_loc)
		for img in dirs:
			file = self.image_queue_loc + img
			image = Image.open(file)
			width, height = image.size
			
			drawing = ImageDraw.Draw(image)

			font_size = width // 30

			font = ImageFont.truetype("cmunss.ttf", font_size)

			text = "@" + self.account_name
			text_w, text_h = drawing.textsize(text, font)
			pos = width - text_w - 20, (height - text_h) - 20

			c_text = Image.new('RGB', (text_w, text_h))
			drawing = ImageDraw.Draw(c_text)

			drawing.text((0,0), text, fill="#ffffff", font=font)
			c_text.putalpha(100)
			image.paste(c_text, pos, c_text)
			try:
				image.save(file)
			except:
				print("Watermarking image failed.")
				os.remove(file)
		return 0

	#Gets the time until the next post in seconds
	def get_time_until_next_post(self):
		#Get the current time and day, and create a tomorrow object
		today = datetime.today() #YYYY-MM-DD HH:MM:SS.UUUUUU
		weekday = today.weekday()
		tomorrow = today + timedelta(days = 1)
		w_tomorrow = tomorrow.weekday()

		#Get posting times for today's day of the week
		timeset = self.posting_times[weekday]

		#Convert all posting times into a datetime object, incl. the first posting time of the next morning
		possible_future_times = []
		for time in timeset:
			update = datetime(today.year, today.month, today.day, time[0], time[1], time[2])
			possible_future_times.append(update)
		#	incl. the first posting time of the next morning
		tomorrow_time = posting_times[w_tomorrow][0]
		tomorrow_first = datetime(tomorrow.year, tomorrow.month, tomorrow.day, tomorrow_time[0], tomorrow_time[1], tomorrow_time[2])
		possible_future_times.append(tomorrow_first)

		#find closest time to current time for next post
		today = datetime.today()
		timeslot = -1
		for i, time in enumerate(possible_future_times):
			if time > today:
				timeslot = i
				break

		#Time until the next future timeslot
		time_until_next = possible_future_times[timeslot] - datetime.now()
		return time_until_next.seconds

	#Clears all images in the image queue
	def clear_image_queue(self):
		files = [f for f in os.listdir(self.image_queue_loc)]
		for f in files:
			os.remove(os.path.join(self.image_queue_loc, f))
		return 0

	#Pick a random subreddit from weighted list of subreddit_dict
	def choose_subreddit(self):
		subs = []
		weights = []

		for subreddit in self.subreddit_dict:
			subs.append(subreddit)
			weights.append(subreddit_dict[subreddit])

		weighted_choice = random.choices(subs, weights, k = 1)
		print("Content From r/", weighted_choice[0], sep = '')
		return weighted_choice[0]

	#Print a dynamic countdown onto the console
	def countdown(self, seconds, message = ''):
		print()
		for i in range(seconds):
			m = message + str(timedelta(seconds=seconds))
			print(f'{m}\r', end = "")
			sys.stdout.flush()
			time.sleep(1)
			seconds -= 1
	#====================================================================

if __name__ == '__main__':
	p = Poster(subreddit_dict, keyphrases, posting_times, below_caption, fetch_random = True)

	p.start()