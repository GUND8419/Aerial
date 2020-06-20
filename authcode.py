import requests
import selenium
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from termcolor import cprint
import prompt_toolkit
import yaml
import json
import bs4
import os

def get(email: str, password: str) -> str:
	browser = selenium.webdriver.Chrome()
	browser.maximize_window()
	browser.get("https://www.epicgames.com/id/logout?lang=en-US&redirectUrl=https%3A%2F%2Fwww.epicgames.com%2Fid%2Flogin%3FredirectUrl%3Dhttps%253A%252F%252Fwww.epicgames.com%252Fid%252Fapi%252Fredirect%253FclientId%253D3446cd72694c4a4485d81b77adbb2141%2526responseType%253Dcode&lang=en-US")
	WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, "login-with-epic"))).click()
	WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, "email"))).send_keys(email)
	WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, "password"))).send_keys(password)
	WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.ID, "login"))).click()
	WebDriverWait(browser, 300).until(lambda browser: browser.current_url == "https://www.epicgames.com/id/api/redirect?clientId=3446cd72694c4a4485d81b77adbb2141&responseType=code")
	code = json.loads(bs4.BeautifulSoup(browser.page_source, "html.parser").body.pre.string)['redirectUrl'].split("=")[1]
	browser.quit()
	return code