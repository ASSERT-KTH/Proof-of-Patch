To install all the required dependencies and create the desired environment, run: 

    Create and activate a virtual environment: 
        macOS/Linux, run:
            python3 -m venv venv
            source venv/bin/activate
        Windows, run:
    
    Install required dependencies, run:
        pip install -r requirements.txt
    
    Setup OpenAI API key (for parser, not necessary for scraper):
        Add OPENAI_API_KEY="your_api_key_here" to the .env in the project root
        Run: export OPENAI_API_KEY="your_api_key_here"

Run:

    To run the solodit-scraper and parser, you have to use your venv:

    Scraper:
        Run: python scraper.py
        The scraper requires the user to manually log in to the webpage. Thus, you will need a cyfrin login to run the scraper. When the scraper is run, manually login to the webpage, and when the login is complete you navigate back to the terminal and press enter.

    Parser (requires result from scraper to run), run:
        python parser.py

Result description:

    My result can be seen in solodit-scraper/my_result

    Scraper:
        The scraper will generate two files named results.json and disregarded_links.json in the same directory. 

        results.json:
            This file consists of audit links as keys, with corresponding data in following format:

            audit_link: {
                scrapping_date: date of scraping,
                poc_content_types: [ combination of "text", "link", and "code" ],
                vulnerabilities: [ search category vulnerabilities the audit appeared in ],
                impact: the stated impact of the audit,
                publication_date: date of audit publication,
                client_source_link: link to audit source,
                authors: names of authors,
                n_authors: #,
                contains_github_link: "yes" or "no",
                audit_content: all content from the entire audit,
                ai_summary: ai summary provided by webpage
            }
        
        disregarded_links.json:
            This json file consists of the links of all disregarded audits for this study, these are all audits that did not include a Proof of Concept.

    parser.py:
        The parser generates one file named enriched_data.json, this is the finalized data.

        enriched_data.json:
            This file has the same structure as results.json, but with the new added categories {
                has_poc_code: "yes" or "no",
                is_well_reasoned: "yes", "mostly", or "no",
                is_correct: "yes" or "no"
            }

Worth to mention:

    The scraper is highly dependent on the webpage of https://solodit.cyfrin.io/ and any change of the html will likely result in the scraper not working and demanding an update. The scraper is up to date with the webpage as of 27th of June 2025.

    Tester mail address to login when running the scraper: 

        Mail: tester_linus@outlook.com
        Password: testertester@123