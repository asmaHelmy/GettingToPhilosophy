import requests
from requests.exceptions import HTTPError
from bs4 import BeautifulSoup
import time
import re

"""
I examined a few pages and concluded the following:
    - class="firstHeading" has Article's title

    - class="mw-body-content" all body

    - class="noprint"  we are **not interested** in links within divs belonging to this class

    - class="hatnote navigation-not-searchable" we are **not interested** in links within divs belonging to this class  #feha ta3reef bl article

    - class="mw-disambig" we are **not interested** in links within divs belonging to this class #first one in page, in hatnote

    - "table tag" sometimes feh box; we are **not interested** in links within box

    - div with class="mw-parser-output"  feha el content in p tag **interested**
        - first link in p tag   **interested**
        - sometimes link has class esmaha mw-redirect or class="extiw"  **interested**
        - ignore class="Latn mention" or not ya3ni :"D  

but noticed that all links are in p tags, not every link has to have a class, so I'll be working on p tags instead.
"""

def getSourceCode(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
    
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
        return None
    
    except Exception as other_err:
        print(f'Other error occurred: {other_err}')
        return None

    else:
        sourceCode = BeautifulSoup(response.text, 'html.parser')
        return sourceCode


def isFullLink(url):
    
    if re.compile(r'https:').findall(url):  # Check if it has the word https
        return 1

    return 0

def removeURLsInParentheses(p):
    
    p = re.sub(r'\([^<]*<\s*a\s*[\w*=\w*]*>(.*)<\s*\/a\s*>[^<]*\)', ' ', p)  #removes links between () 
    p = re.sub(r'  ', ' ', p)
    
    return p

def notAccepted(url):
    
    # Did that before thinking of removing all between ()
    
    if re.compile(r'/Help:IPA').findall(url):    #Check if wiki/Help:IPA
        return 1
    
    elif re.compile(r'#cite_note-').findall(url):  # Check for #cite_note-*
        return 1
    
    elif re.compile(r'upload.wikimedia.org').findall(url):  # Check if its an upload
        return 1
    
    elif re.compile(r'File:').findall(url):  # Check if it's a file
        return 1
    
    elif re.compile(r':Media_help').findall(url):  # Check if it's a file
        return 1 
    
    else:
        return 0

def getNextURL(p_s, visitedURLs):
    
    for p in p_s:
        
        if len(p.find_all('a')) == 0:
            continue
            
        else:
            p = BeautifulSoup(removeURLsInParentheses(str(p)), 'html.parser')

            for a in p.find_all('a'):
                
                nxt = a['href']

                if notAccepted(nxt):
                    continue
                elif nxt in visitedURLs:
                    return 'Loop'
                else:
                    if isFullLink(a['href']):
                        return a['href']
                    else:
                        return 'https://en.wikipedia.org'+a['href']
    return None


def gettingToPhilosophy(url, visitedURLs, previousURL):
        
    if url == 'https://en.wikipedia.org/wiki/Philosophy':
        print(url)
        return
    
    print(url) 
    visitedURLs.append(url)
    sourceCode = getSourceCode(url)
    
    if sourceCode is not None: # If could retrieve source code
        
        p_s = sourceCode.find_all('p') # Get its paragraphs, cuz not always the link is in the first paragraph 
        
        nextUrl = getNextURL(p_s, visitedURLs) # Checking <p>s, to get our next outgoing link
        
        if nextUrl == previousURL or nextUrl == 'Loop': #Check if loop
            print("Loop detected, exiting....")
            return
        
        elif nextUrl is None:      # Check if there are no outgoing links Ex: 
            print('No outdoing URLs')
            return
        
        else:
            time.sleep(0.5)
            gettingToPhilosophy(nextUrl, visitedURLs, url)
    
#url = input('Enter URL: ')
url = 'https://en.wikipedia.org/wiki/Special:Random'
gettingToPhilosophy(url, [], '')