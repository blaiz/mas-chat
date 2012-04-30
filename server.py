#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# MAS CHAT Server Prototype
# Based on a Python tutorial
#
# Copyright © 2007 Blaiz
#
# Released under the GNU GPL License Version 2
#

# IMPORT OF MODULES
import socket
import select

# DECLARES THE CHAT CLASS
class ChatServer:
	"""Class for creating and executing a new chat server"""
	def __init__( self, port ):
		self.port = port;
		self.srvsock = socket.socket( socket.AF_INET, socket.SOCK_STREAM ) # Creates a server socket
		self.srvsock.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )
		self.srvsock.bind( ("", port) ) # Sets where to listen
		self.srvsock.listen( 5 ) # Sets the state of the socket to listening to new connections
		self.descriptors = [self.srvsock] # Creates a list of sockets (server socket, and client sockets)
		self.nicknames = {} # A dictionary of the nicknames with the socket.fileno() as the key
		print 'ChatServer started on port %s' % port
		
	def run( self ):
		"""Launch the server"""
		while 1:
			# Await an event on a readable socket descriptor
			(sread, swrite, sexc) = select.select( self.descriptors, [], [] )
			
			# Iterate through the tagged read descriptors
			for sock in sread:
					
				# Received a connect to the server (listening) socket
				if sock == self.srvsock:
					self.accept_new_connection()
				else:
					
					# Received something on a client socket
					strfuck = sock.recv(100)
					
					# Check to see if the peer socket closed
					if strfuck == '':
						host,port = sock.getpeername()
						strfuck = "MESS\0" + self.nicknames[sock.fileno()] + " left"
						self.broadcast_strfucking( strfuck, sock )
						sock.close
						self.descriptors.remove(sock)
					else:
						host,port = sock.getpeername()
						stragneugneu = strfuck.split("\n") # the "\n" character is the separator for protocol instructions
						
						for stragneugneu2 in stragneugneu:
							if stragneugneu2 != "":
								strcrap = stragneugneu2.split("\0") # the "\0" character is the separator for instruction arguments
								
								if strcrap[0] == "MESS":
									newstrfuck = ":" + self.nicknames[sock.fileno()] + "\0MESS\0" + strcrap[1]
									
								elif strcrap[0] == "HELO":
									self.nicknames[sock.fileno()] = strcrap[1]
									newstrfuck = "MESS\0" + self.nicknames[sock.fileno()] + " joined\n"
									newstrfuck += ":" + self.nicknames[sock.fileno()] + "\0JOIN"
									
								elif strcrap[0] == "MOVE":
									newstrfuck = ":" + self.nicknames[sock.fileno()] + "\0" + strcrap[0] + "\0" + strcrap[1] + "\0" + strcrap[2]
									
								else:
									newstrfuck = strfuck
								self.broadcast_strfucking( newstrfuck, sock ) # Sends the message to everybody except the sender
	
	def broadcast_strfucking( self, strfuck, omit_sock ):
		"""Sends a message to every client except the sender of the message"""
		strfuck += "\n" # Adds the protocol instruction delimiter character at the end of the sentence
		
		for sock in self.descriptors:
			if sock != self.srvsock and sock != omit_sock:
				sock.send(strfuck)
				
		print strfuck
	
	def accept_new_connection( self ):
		"""Executes operations for adding a new client on the server"""
		
		newsock, (remhost, remport) = self.srvsock.accept()
		self.descriptors.append( newsock ) # Adds the client to the socket list
		
		newsock.send("MESS\0Welcome to the chat room\n") # Send a welcome message to the new client
		
		# Sends to the new client, the list of all the conncted clients
		for sock in self.descriptors:
			if sock != self.srvsock and sock != newsock:
				newsock.send(":" + self.nicknames[sock.fileno()] + "\0JOIN\n")

myServer = ChatServer( 12720 ).run()
