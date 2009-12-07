#!/usr/bin/env python
#
# webshot.py
# Render a page with Qt's QWebPage widget and save a screenshot of it
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
import sys
import tempfile

try:
    import PyQt4.QtWebKit
    import PyQt4.QtGui
    import PyQt4.QtCore
except:
    print("Failed to load PyQt4 - get it from http://www.riverbankcomputing.co.uk/software/pyqt/download")
    print(" or on Debian/Ubuntu run: sudo apt-get install python-qt4")
    sys.exit(1)

class WebshotRenderer(PyQt4.QtWebKit.QWebPage):
    """
    Class for rendering a webpage with webkit (via Qt).
    """

    def __init__(self):
        """
        Create the renderer.
        """
        self.application = PyQt4.QtGui.QApplication([])
        PyQt4.QtWebKit.QWebPage.__init__(self)
        self.loadFinished.connect(self.__load_finished)
        self.timer = PyQt4.QtCore.QTimer()
        self.timer.timeout.connect(self.__load_timeout)
        self.timer.setSingleShot(True)
        self.timer.setInterval(5 * 60 * 100) # 5 minute timeout

    def render(self, url, timeout_seconds=300):
        """
        Given a url return a temporary filename pointing to a png screenshot of the page.
        It is the callers responsibility to delete or move the file when finished.
        Pass a timeout in seconds if you want to override the default of 5 minutes.
        """
        # Generate a temporary file
        filehandle, filename = tempfile.mkstemp(prefix='webshot', suffix='.png')
        os.close(filehandle)

        # Set the viewport to a standard frame
        frame_size = PyQt4.QtCore.QSize(800, 600)
        self.setViewportSize(frame_size)

        # Send the request and then loop until we get the complete or timeout signal
        self.__render_result = None
        self.mainFrame().load(PyQt4.QtCore.QUrl(url))
        self.timer.start()
        while self.__render_result == None:
            self.application.processEvents()

        # Stop the timer
        self.timer.stop()

        # If we failed to render then throw an exception
        if self.__render_result == False:
            # Stop the browser so we don't get a later success message after a timeout
            self.triggerAction(PyQt4.QtWebKit.QWebPage.Stop)
            self.application.processEvents()
            raise RuntimeError("Failed to render %s" % (url))

        # Save the result into an image the size of the content
        frame_size = self.mainFrame().contentsSize()
        self.setViewportSize(frame_size)
        image = PyQt4.QtGui.QImage(frame_size, PyQt4.QtGui.QImage.Format_RGB32)
        painter = PyQt4.QtGui.QPainter(image)
        if painter.isActive() == False: raise RuntimeError("Failed to create painter")
        self.mainFrame().render(painter)
        if painter.end() == False: raise RuntimeError("Failed to paint")
        if image.save(filename) == False: raise RuntimeError("Failed to save image")
        
        return filename

    def __load_timeout(self):
        self.__render_result = False

    def __load_finished(self, result):
        self.__render_result = result


if __name__ == '__main__':
    # Test the webkit rendering class
    print("Taking two screenshots of http://codev.co.uk to:")
    webshot = WebshotRenderer()
    try:
        print(webshot.render("http://codev.co.uk"))
    except Exception, e:
        print(e)
    try:
        print(webshot.render("http://codev.co.uk"))
    except Exception, e:
        print(e)
    print("Please check both have rendered correctly")

