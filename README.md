# instagram-following-search
 Find a list of accounts with mutual followings. Primarily designed for OSINT investigations.

 Usage example:

Fetch mutual followings of **githubeducation** and **codenewbies**:

        $ search.py -u "githubeducation codenewbies"


### Installation


Clone the github repo
```
$ git clone https://github.com/georgehawkins0/instagram-following-search.git
```
Change Directory

```
$ cd instagram-following-search
``` 

Install requirements

```
$ python3 -m pip install -r requirements.txt
``` 

To use this tool, you need to add login credentials for the account you wish to do the crawling from in creds/creds.yml