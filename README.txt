Reddit-Imgur-Craigslist
-----------------------

ric is a small program for watching reddit.com for new craigslist posts,
taking snapshots of them and uploading them to imgur.com.

Requirements
------------

ric requires Python 2.6 and PyQt4 which you can obtain from:

http://www.riverbankcomputing.co.uk/software/pyqt/download

Usage
-----

Start ric.py from the command line with:

python ric.py

Enter your imgur key and you reddit username and password to start posting
imgur caches to reddit.com - there is already a daemon running this process
on Codev's servers so you should not do this unless you have modified the
program (for example to cache a different page). If you leave the reddit
username blank you will get a list of stories and filenames of screenshots
of the stories instead.

Utilities
---------

Comes with three utility python modules that may be useful for other things:

imgur.py - API for uploading images to imgur.com
reddit.py - API for searching and posting to reddit.com
webshot.py - API for taking screenshots of web pages

License
-------

Author: Marc Sutton <ric@codev.co.uk>
Copyright (c) 2009 Codev Ltd

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program in LICENSE.txt; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA

