from bs4 import BeautifulSoup
from urllib import request
 
# Initializing variable
url =  "https://en.wikipedia.org/wiki/Vivian_Smith_(suffragist)"
response = requests.get(url)

soup = BeautifulSoup(response.content)
print(soup.get_text())