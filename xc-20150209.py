from bs4 import BeautifulSoup
import sys
from urlparse import urlparse
from tldextract import tldextract

import logging
LOG_FILENAME = 'redditScraper.log'
logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)


# We only want the 'description' field or we get any resource mentioned in the post title, so delete the 'title' column 
#before making the input csv

f = open(sys.argv[1]) #remember sys.argv[0] is the name of the script
					  #open defaults to read if no argument given

resources = {} #create a dictionary to keep the resource names in and count the number of appearences
soup = BeautifulSoup(f) #parse the document
links = soup.find_all('a') #find all a href link tags
# we need to find markdown links also


for x in links:
	print x
	burl = urlparse(x['href']).hostname 
	
	if burl:
		resourceFound = tldextract.extract(burl).domain # we only want top level domains
		if resources.has_key(resourceFound): #check each name against this list to see if it's new
			resources[resourceFound] = (resources[resourceFound]+1)  #if in list, increment count
		else:
			resources[resourceFound] = 1  #if not in list, add it 
	else: 
		print x
print resources

 



