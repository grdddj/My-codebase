"MONGO_CLIENT": 'mongodb+srv://grdddj:myFirstDB@cluster-l467y.mongodb.net/test?retryWrites=true',
"DATABASE": 'Alza',
"COLLECTION": 'Powerbanks',

"DOMAIN": 'https://www.alza.cz',
"SUFFIX": ' - Alza.cz',
"INIT_PAGE": 'https://www.alza.cz/powerbanky/18854166-p1.htm',

"TOGETHER_COUNT_PATH": 'int(soup.find("span", {"id": "lblNumberItem"}).get_text())',
"ONE_PAGE_COUNT_PATH": 'len(soup.findAll(class_="canBuy"))',
"ITERATIVE_PAGE": '"https://www.alza.cz/powerbanky/18854166-p" + str(number) + ".htm"',

"ALL_GOODS_PATH": 'soup.findAll(class_="canBuy")',
"LINK_PATH": 'goods.find("a")["href"]',

"NAME_PATH": 'soup.find("h1").get_text().strip()',
"PRICE_PATH": 'soup.find(class_="bigPrice").get_text().strip()',
"HIGH_PRICE_PATH": 'soup.find(class_="crossPrice").get_text().strip()',
"DESCRIPTION_PATH": 'soup.find(class_="nameextc").get_text().strip()',
"PARAMETERS_PATH": 'soup.findAll(class_="row")',
