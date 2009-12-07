#!/usr/bin/env python
#
# imgur.py
# Tools for interacting with imgur.com via their api (http://code.google.com/p/imgur-api/)
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

import os.path
import urllib2

try:
    import json
except:
    print("Failed to load json, requires Python 2.6 or later")
    sys.exit(1)

class ImgurApi:
    """
    A class for using the imgur.com api
    See http://code.google.com/p/imgur-api
    """
    def __init__(self, apikey):
        self._apikey = apikey

    def upload_image(self, filename):
        """
        Upload an image to imgur and return the viewing url.
        """

        boundary = '----------boundary'
        body = '--' + boundary + '\r\n'
        body += 'Content-Disposition: form-data; name="key"\r\n'
        body += '\r\n'
        body += self._apikey + '\r\n'

        body += '--' + boundary + '\r\n'
        body += 'Content-Disposition: form-data; name="image"; filename="ric'
        body += os.path.splitext(filename)[1]
        body += '"\r\n'
        body += 'Content-Type: application/octet-stream\r\n'
        body += '\r\n'

        handle = open(filename, 'r')
        body += handle.read() + '\r\n'
        handle.close()

        body += '--' + boundary + '--\r\n'
        body += '\r\n'

        content_type = 'multipart/form-data; boundary=%s' % boundary

        # TODO: Switch to urllib2
        request = urllib2.Request('http://imgur.com/api/upload.json', body, { 'content-type': content_type, 'content-length': str(len(body)) })
        http = urllib2.urlopen(request)
        contents = http.read()
        http.close()
        result = json.loads(contents)

        if result['rsp']['stat'] != 'ok':
            raise RuntimeError('Failed to upload image to imgur.com, error %d: %s' % (result['rsp']['error_code'], result['rsp']['error_msg']))
        
        return result['rsp']['image']['imgur_page']
        
if __name__ == '__main__':
    # Test the class
    key = raw_input("Enter your Imgur key:")
    imgur = ImgurApi(key)
    filename = raw_input("Enter the full path to an image:")
    print("Please check this url contains the correct image:")
    print(imgur.upload_image(filename))

