#!/usr/bin/env python
#
# reddit.py
# Tools for interacting with the social bookmarking site reddit.com
#
# Author: Marc Sutton <ric@codev.co.uk>
# Copyright (c) 2009 Codev Ltd
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA

import HTMLParser
import urllib
import urllib2
import cookielib
import re

try:
    import json
except:
    print("Failed to load json, requires Python 2.6 or later")
    sys.exit(1)

class RedditLink:
    """
    Store a link from reddit.com along with metadata.
    """

    def __init__(self, title, href, subreddit, domain, name, fullname):
        self.title = title
        self.href = href
        self.subreddit = subreddit
        self.domain = domain
        self.name = name
        self.fullname = fullname

    def __repr__(self):
        return self.title + ": " + self.href

    def comment_page(self):
        return 'http://reddit.com/r/' + self.subreddit + '/comments/' + self.name

class RedditApi:
    """
    A class for using the social bookmark site reddit.com
    """
    def __init__(self, username, password):
        """
        Pass the username and password to create an object to access reddit.com
        """
        self.username = username
        self.password = password

        self.link_type = 't3_' # The 3 may have to change this for reddit installations other than reddit.com

        # Set up the cookie jar and login for the first time
        self.logged_in = False
        self.__cookiejar = cookielib.CookieJar()
        self.url_opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.__cookiejar))
        self.login()

    def login(self):
        """
        Login to reddit.
        Returns True if successful.
        """
        if not self.username:
            self.logged_in = False
            return False
            
        if self.logged_in:
            return True
        
        response = self.url_opener.open('http://www.reddit.com/post/login',
                                        urllib.urlencode([('op', 'login-main'),
                                                          ('user', self.username),
                                                          ('passwd', self.password)]))
        contents = response.read()
        response.close()
                                          
        # Figure out if we logged in
        # The status code is always 200 so look at the contents
        # If we have logged in we see: "logged: 'username'" in the js reddit object
        if contents.find("logged: '%s'" % (self.username)) != -1:
            self.logged_in = True
            
        return self.logged_in

    def search(self, query, sorted_by=None, links_from=None):
        """
        Search reddit for the given query values.
        Returns a list of RedditLink items.
        """
        # Validate parameters
        if not (sorted_by == None or
                sorted_by == 'new' or
                sorted_by == 'top' or
                sorted_by == 'old' or
                sorted_by == 'hot'):
            raise ValueError('sorted_by must be one of: new, top, old, hot (or None for relevance)')
        
        if not (links_from == None or
                links_from == 'hour' or
                links_from == 'day' or
                links_from == 'week' or
                links_from == 'month' or
                links_from == 'year'):
            raise ValueError('links_from must be one of: year, month, week, day, hour (or None for all-time)')
        
        url = "http://www.reddit.com/search.json"
        params = [('q', query)]
        if sorted_by: params += [('sort', sorted_by)]
        if links_from: params += [('t', links_from)]
        
        page = self.url_opener.open(url + "?" + urllib.urlencode(params))
        contents = page.read()
        page.close()
        results = json.loads(contents)
        
        links = []
        for link_meta in results['data']['children']:
            link = link_meta['data']
            links += [RedditLink(link['title'], link['url'], link['subreddit'], link['domain'], link['id'], link['name'])]

        return links

    def submit_comment(self, comment_page_url, comment, reply_to_fullname='', retry=True):
        """
        Submit a comment to reddit.com.
        Pass the page containg the comments from which the subreddit will be extracted.
        If retry is set to True then if the user is not logged in 
        Throws an exception if unsuccessful.
        """
        # Fetch the comments page to extract the anti-XSRF token
        response = self.url_opener.open(comment_page_url)
        modhash = re.search(r"modhash: '([^']*)'", response.read()).group(1)
        response.close()
        
        # Figure out the rest of the parameters from the url or passed in values
        url_parts = re.match(r"http[s]{0,1}://([^/]*)/r/([^/]*)/comments/([^/]*)", comment_page_url)
        subreddit = url_parts.group(2)
        if not reply_to_fullname:
            reply_to_fullname = self.link_type + url_parts.group(3)

        # Submit the comment
        response = self.url_opener.open('http://www.reddit.com/api/comment',
                                        urllib.urlencode([('thing_id', reply_to_fullname),
                                                          ('r', subreddit),
                                                          ('uh', modhash),
                                                          ('text', comment)]))
        result = response.read()
        response.close()
        
        # Test the various responses
        error_code = re.search('"\.error\.([A-Z_]*)"', result)
        if error_code:
            # If we are not logged in try and log in 
            if error_code.group(1) == '.error.USER_REQUIRED':
                self.logged_in = False
                self.login()
                if self.logged_in and retry:
                    return self.submit_comment(comment_page_url, comment, reply_to_fullname, False)
                else:
                    raise RuntimeError('Error posting comment: User required - attempted to log in again')
            else:
                raise RuntimeError('Error posting comment: %s' % (error_code.group(1)))

    def submit_link(self, title, url, subreddit='reddit.com'):
        """
        Submit a link to reddit - pass a title, url and subreddit (defaults to the main reddit).
        See http://www.reddit.com/help/reddiquette before submitting.
        Throws an exception if unsuccessful.
        """
        response = self.url_opener.open('http://www.reddit.com/submit',
                                        urllib.urlencode([('title', title),
                                                          ('url', url),
                                                          ('sr', subreddit)]))
        print response.code
        print response.read()
        response.close()
        raise NotImplementedError("Submitting links does not work yet.")

if __name__ == '__main__':
    # Test the classes
    username = raw_input("Enter reddit.com username: ")
    import getpass
    password = getpass.getpass("Enter reddit.com password: ")
    reddit = RedditApi(username, password)

    print("Reddit.com links about Kant:")
    print(reddit.search('kant'))

    print("Submitting a link to the test subreddit, check http://www.reddit.com/r/test/comments/a2baf")
    reddit.submit_comment('http://www.reddit.com/r/test/comments/a2baf', 'AIOTM')

