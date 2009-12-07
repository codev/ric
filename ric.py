#!/usr/bin/env python
#
# ric.py
#
# Looks for posts on reddit that link to sites that may be removed
# (craigslists.org posts by defaults) and uploads a screenshot of
# the site to imgur and re-submits the post.
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

import os
import time
import pickle
import getpass
import imgur
import reddit
import webshot

if __name__ == '__main__':
    # Load the settings
    # Is a tuple of (pages we have already processed so we don't repeat,
    #                imgur key,
    #                reddit username)
    settings_filename = os.path.join(os.path.expanduser('~'), '.ric.pkl')
    try:
        with open(settings_filename, 'rb') as settings:
            processed, imgur_key, reddit_username = pickle.load(settings)
    except:
        processed = []
        imgur_key = None
        reddit_username = None

    # Fetch any settings we are missing
    if not reddit_username:
        reddit_username = raw_input("Enter reddit.com username (blank for dry-run mode where no comments will be posted): ")
    if not reddit_username:
        reddit_password = None
        dry_run = True
    else:
        reddit_password = getpass.getpass("Enter reddit.com password for %s: " % (reddit_username))
        dry_run = False
    if reddit_username and not imgur_key:
        imgur_key = raw_input("Enter imgur.com api key: ")

    # Create the app and webkit and renderer
    renderer = webshot.WebshotRenderer()
    imgur = imgur.ImgurApi(imgur_key)
    reddit = reddit.RedditApi(reddit_username, reddit_password)

    # This contains a list of links we couldn't process for one reason or another
    # (may be because it appears on a NSFW reddit or just a network problem)
    # They will be skipped for one round and ignored until we have completed examining all links
    error_links = set()

    # Load all the links from the last day mentioning craigslist
    first = True
    while True:
        # Process all links on the page
        uploaded = False
        link = None
        try:
            for link in reddit.search('craigslist.org', 'new', 'day'):
                # Skip links that caused problems for one loop only
                if link in error_links:
                    continue

                # If the url is a link to craigslist examine it
                if link.domain == 'craigslist.org' or link.domain.endswith('.craigslist.org'):
                    # See if we have already processed it
                    if link.href not in processed:
                        # Get a screenshot of it
                        filename = renderer.render(link.href)
                        
                        if dry_run:
                            print("Created image for story\n    %s\n    %s\n    %s" % (link.title, link.comment_page(), filename))
                            processed += [link.href] # Don't store settings in dry-run mode
                        else:
                            # Submit the screenshot to imgur.com
                            imgur_link = imgur.upload_image(filename)
                            print("Uploading image for story\n    %s\n    %s\n    %s" % (link.title, link.comment_page(), imgur_link))
                            
                            # Delete image
                            os.unlink(filename)

                            # Submit the link back to reddit
                            reddit.submit_comment(link.comment_page(), 'Imgur cache: %s' % (imgur_link))

                            # Mark this link as processed
                            processed += [link.href]
                            with open(settings_filename, 'wb') as settings:
                                pickle.dump((processed, imgur_key, reddit_username), settings)

                        # Skip to waiting for the next link
                        uploaded = True
                        break

            # Saw all the links so reset the error set to allow us to try again
            error_links = set()
        except Exception, e:
            print ('ERROR: %s' % str(e))
            if link:
                error_links.add(link.href)
                
        # Pause for 11 minutes before processing the list again to avoid reddit thinking 'FLOOD'
        if uploaded or first:
            print("> Waiting for 11 minutes or the next new story, whichever is sooner...")
            first = False
        time.sleep(660)

