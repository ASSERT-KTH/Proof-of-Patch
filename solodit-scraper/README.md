Dependencies:

To install all the required dependencies, run:

pip install -r requirements.txt

Run:

To run the solodit-scraper, use following command in the ../solodit-scraper terminal:

/Users/linussvensson/Desktop/exjobb/VeriSet/solodit-scraper/.venv/bin/python /Users/linussvensson/Desktop/exjobb/VeriSet/solodit-scraper/scraper.py

Result description:

The script will generate a file named results.json in the same directory. This file contains a JSON object where:

Keys are the OWASP Top 10 vulnerability categories (e.g., 'access control').
Values are lists of URLs, with each URL pointing to a specific Solodit audit report that matches the category and includes a coded Proof of Concept.

The result includes many duplicate links that are included in multiple search categories. To process this, look at /my_result/data_processing

Tester mail address to login when running the scraper: 

Mail: tester_linus@outlook.com
Password: testertester@123

GAINED HELP FROM: https://github.com/OnchainGuard/OnchainGuard/blob/main/src/solidit-scrapping/parser.py 