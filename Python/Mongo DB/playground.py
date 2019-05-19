import requests
from bs4 import BeautifulSoup
import re

categories = "gmetal gas"

if re.search(r"\b(metal)\b", categories, flags=re.IGNORECASE) is None:
    print("NOT FOUND")
else:
    print("found")
