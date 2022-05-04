(In progress)

## Setting Virtualenv and Dev environment on localhost

```
pip3 install virtualenv

mkdir playstorescrapper
cd playstorescrapper
virtualenv venv -p python3
source venv/bin/activate
git clone <repo_url>
cd playstorescrapper
pip install -r requirements.txt

//----------CREATE DATABASE TABLES-------------
(venv) MacBooks-MacBook-Pro:playstorescrapper macbookpro$ python
Python 3.7.4 (default, Jul  9 2019, 18:13:23) 
[Clang 10.0.1 (clang-1001.0.46.4)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> from playstorescrapperapp import db
>>> db.create_all()
>>> exit()
//---------------------------------------------

python seed_data.py
python run.py
```

Dev environment has admin panel available at http://localhost:5000/admin

Create a username and password ( Can be created from python shell as well )

## Application Settings

Settings in init.py file

```
app.config['SCRAPPER_REFRESH_DAYS'] = 30
app.config['JWT_TOKEN_EXPIRY_HOURS'] = 24
```

## API Endpoints

**/login** - POST request with JSON like this -

```
{
	"username": "<username>",
	"password": "<password>""
}

Response :

{
  "token": "<token>"
}
```

Send token with all requests to protected routes like so -  "Authorization: Bearer [TOKEN]" header

**/refresh_token** - GET request

**Response:**

```
{
  "new_token": "<new_token>"
}
```

**/categories**

```
[
  {
    "categoryId": 1,
    "categoryName": "ANDROID_WEAR"
  },
  {
    "categoryId": 2,
    "categoryName": "ART_AND_DESIGN"
  },
  
  ......
```

**/get_app/net.one97.paytm/**

```
{
    "title": "Paytm - BHIM UPI, Money Transfer & Mobile Recharge",
    "icon": "https://lh3.googleusercontent.com/k7yz57K2OxhNrPNKF2U18Zcv9rodOu7CfWh47U15FFUN8-_B0hQfXsM-BaLG0gOtvw",
    "screenshots": [],
    "video": "https://www.youtube.com/embed/-WXkoGfjaXY",
    "category": [
    
    ......
```

**get_apps_by_category/8**/

List of apps of a certain category

```
[
	{},
	{},
	{}
]
```
