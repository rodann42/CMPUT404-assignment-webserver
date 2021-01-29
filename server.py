#  coding: utf-8
import socketserver
import os
# Copyright 2013 Abram Hindle, Eddie Antonio Santos
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):

    def handle(self):
        self.data = self.request.recv(1024).strip().decode('utf-8').split('\n')
        print ("Got a request of: %s\n" % self.data)

        self.code = '200 OK\r\n'
        self.contentType = ''
        self.content = ''
        self.location = ''
        self.statusMessage = ''
        # self.request.sendall(bytearray("OK",'utf-8'))

        method = self.data[0].split(" ")[0]

        # check method, if method is not GET, return status code 405
        if method.upper() != 'GET':
            self.code = '405\r\n'
            self.statusMessage = '405 Method Not Allowed\r\n\r\n'
            # self.request.sendall(bytearray("HTTP/1.1 405 Method Not Allowed\r\n\r\n", "utf-8"))
        else:
            # get requested path
            relPath = self.data[0].split(' ')[1]
            absPath = "www" + os.path.abspath(relPath)
            print(absPath)
            self.handlePath(absPath, relPath)

        print("prepare to send response")
        self.sendResponse()

    def handlePath(self, absPath, relPath):
        print('here', absPath)

        if (os.path.isdir(absPath)):
            print("pathexist", absPath)
            # bad ending
            if (not relPath.endswith("/")):
                self.location = relPath +'/'
                self.code = '301\r\n'
                self.statusMessage = 'Redirect to correct location'
                return

            # if request end with "/", check index.html
            indexPath = os.path.join(absPath, "index.html")
            print(indexPath)
            if (os.path.exists(indexPath)):
                print("indexPath")
                return self.setResource(indexPath)
            else:
                print("404 ResourceNotFound")
                self.code = '404\r\n'
                self.statusMessage = 'Resource Not Found\r\n\r\n'
                return
                # self.request.sendall(bytearray("HTTP/1.1 404 Resource Not Found\r\n\r\n", "utf-8"))

        elif os.path.exists(absPath):
            return self.setResource(absPath)
        else:
            print("!!!!!!!!!!404 ResourceNotFound")
            self.code = '404\r\n'
            self.statusMessage = 'Resource Not Found\r\n\r\n'
            return


    def sendResponse(self):
        print("sendResponse")
        response = 'HTTP/1.1 {}{}{}{}\r\n{}\r\n'.format(self.code, self.statusMessage, self.location, self.contentType, self.content)
        self.request.sendall(bytearray(response, 'utf-8'))


    def setResource(self, path):
        print("setting resource")
        try:
            with open(path, 'r') as f:
                buffer = f.read()
                print(buffer)
                if (path.endswith(".html")):
                    self.contentType = "Content-Type: text/html\r\n"
                elif (path.endswith(".css")):
                    self.contentType = "Content-Type: text/css\r\n"
                self.content = buffer

        except Exception as e:
            print(e)
            self.code = "404\r\n"
            self.statusMessage = "Resource Not Found"


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True

    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
