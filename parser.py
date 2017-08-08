#! /usr/bin/python
# -*- coding: UTF-8 -*-

# Install module: selenium
# Download driver https://sites.google.com/a/chromium.org/chromedriver/downloads
# Place it in /usr/local/bin or /usr/bin
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By


initialLink = 'https://www.linkedin.com' # No need to change
comp = 'companies.txt' # Path to file with company name and link
login = 'login' # linkedin login
password = 'password' #linkedin password
timeout = 2000

with open(comp, 'r') as companies:
	com = dict([line.split('-')[::-1] for line in companies])
links = {}
for k, v in com.iteritems():
      links[k.strip().replace('\n', ' ')]=v.strip()
print '\033[34mCompanies for search: \n'
for k, v in links.iteritems():
	print '%s - %s' % (v,k)
print '\033[0m\n'

driver = webdriver.Chrome()
driver.get(initialLink)
driver.find_element_by_name('session_key').send_keys(login);
driver.find_element_by_name('session_password').send_keys(password);
driver.find_element_by_class_name('submit-button').click()
hellomessage = driver.find_element_by_class_name('feed-s-identity-module__actor-link').text
print 'You are authorized as: ', hellomessage
print '###################################'

for link, company in links.iteritems():
	print '\033[034mWork with:', company, '\033[0m\n'
	driver.get(link)
	pagination = True
	page = 1
	with open('result.txt', 'a') as result:
		while pagination:
			result.write('Page: %s \n' % page)
			print '\n\033[33m Page: %s \033[0m\n' % page
			lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
			match=False
			while(match==False):
				lastCount = lenOfPage
				time.sleep(3)
				lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
				if lastCount==lenOfPage:
					match=True
			# driver.execute_script("document.body.style.zoom='70%'")
			driver.implicitly_wait(timeout)

			# Magic below.
			raw = []
			raw = driver.find_elements_by_xpath("//*[contains(@class, 'search-result')]/div/div[contains(@class, 'search-result__info')]/*[self::a/h3/span/span[contains(@class, 'actor-name')] or self::p[contains(@class, 'subline-level-1')]]")
			if len(raw) % 2 != 0:
				print '\033[31mSomething went wrong! List is not even. Lost some name or position.\033[0m\n'
				result.write('Something went wrong! List is not even. Lost some name or position.\n\n')
				for x in raw:
					print x.text
				print '\n####################################################################\n'
				driver.close()
				quit()
			if len(raw) < 20:
				print '\033[31mI have lost someone here =(. Found %s instead of 10 people\033[0m\n' % int(len(raw)/2)
				result.write('I have lost someone here =(. Found %s instead of 10 people\n\n' % int(len(raw)/2))
			rw = []
			for x in raw:
				rw.append(x.text.encode('utf-8'))

			rwd = {}
			rwd = list(tuple((zip(rw[0::2], rw[1::2]))))

			data = []
			for tup in rwd:
				l = list(tup)
				l[0] = l[0].split('\n')[0]
				data.append(tuple(l))
			for x in data:
				print x[0]+' - '+company+' - '+x[1]
			 	result.write(x[0]+' - '+company+' - '+x[1]+'\n')
			result.write('\n')

			try:
				buttons = driver.find_elements_by_xpath("//ol[contains(@class, 'ember-view')]/li/button/*[self::div[contains(@class, 'prev-text')] or self::div[contains(@class, 'next-text')]]")
				for x in buttons:
					if x.text == 'Previous':
						buttons.remove(x)
				if buttons and 'Next' in buttons[0].text:
					page+=1
					buttons[0].click()
				else:
					raise NoSuchElementException
			except NoSuchElementException:
				pagination = False
				print '\n \033[31m ############# FINISHED ############\033[0m'

driver.close()
