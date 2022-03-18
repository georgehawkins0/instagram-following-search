# instagram-following-search
 Find a list of accounts with mutual followings. Primarily designed for OSINT investigations.

 Usage example:

Fetch mutual followings of **githubeducation** and **codenewbies**:

First you need to have put in the credentials of the instagram account you wish to crawl from in creds/creds.yml

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

### Note

To use this tool, you will need an instagram account. If the users you wish to find mutual followings of are private, this instagram account needs to be following them. You need to add login credentials for the account you wish to do the crawling from in creds/creds.yml