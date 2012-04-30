#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# MAS CHAT Client Prototype
#
# Copyright © 2007 Blaiz
#
# Released under the GNU GPL License Version 2
#

# IMPORT OF PYTHON AND PYGAME MODULES
import os, sys # System modules
import socket # Network modules
import select # Module for using the network sockets
import pygame # the pygame module (SDL Library python wrapper)
from pygame.locals import * # Import of the essential pygame modules

# We show error messages if some pygame modules are disabled
if not pygame.font: print 'Warning, fonts disabled'
if not pygame.mixer: print 'Warning, sound disabled'

# CONSTANTS
FRAMES_PER_SEC	= 40  # The number of frames per second
PLAYER_SPEED	= 10 # This multiply the move of the characters
SCREENWIDTH		= 640
SCREENHEIGHT	= 480
SCREENRECT		= Rect(0, 0, SCREENWIDTH, SCREENHEIGHT) # Here are the dimensions of the game window
TITLETEXT		= 'MAS Chat Client Prototype' # The title of the window
DATAFOLDER		= 'data' # The name of the folder where the data (images, sounds, ...) are

ALLOWEDLETTER	= (K_a, K_b, K_c, K_d, K_e, K_f, K_g, K_h, K_i, K_j, K_k, K_l, K_m, K_n, K_o, K_p, K_q, K_r, K_s, K_t, K_u, K_v, K_w, K_x, K_y, K_z, K_0, K_1, K_2, K_3, K_4, K_5, K_6, K_7, K_8, K_9, K_SPACE, K_EXCLAIM) # A list of allowed letter that can be typed into the textfield

# Network variables
host = raw_input("Enter the Name or IP Address of the chat server: ") # Shows a prompt for the server address
host = host.strip(" ")
if host == "":
	host = "localhost" # if nothing given, it connects to localhost

nickname = raw_input("Enter your nickname: ") # show a prompt for the nickname
nickname = nickname.strip(" ")
if nickname == "":
	nickname = "Mario" # if nothing given, the nickname is Mario

port = 12720 # the TCP port

# We use this function to load images into the game
# (inspired by the load_image function from the Chimp Line by Line tutorial)
def load_image(name, colorkey=None):
	"""Loads an image and set the transparent color for it"""
	fullname = os.path.join(DATAFOLDER, name)
	try:
		image = pygame.image.load(fullname)
	except pygame.error, message:
		print 'Cannot load image:', fullname
		raise SystemExit, message
	image = image.convert()
	if colorkey is not None:
		if colorkey is -1:
			colorkey = image.get_at((0,0))
		image.set_colorkey(colorkey, RLEACCEL)
	return image, image.get_rect()

# Class used to create a character sprite in the game
class Character(pygame.sprite.Sprite):
	"""Moves a sprite representing the character on the screen"""
	def __init__(self):
		pygame.sprite.Sprite.__init__(self) #call Sprite initializer
		self.image, self.rect = load_image('mario.png', -1)
		self.rect = self.rect.move(0, 60)

	def move(self, directionX, directionY):
		self.rect = self.rect.move(directionX*PLAYER_SPEED, directionY*PLAYER_SPEED).clamp(0, 60, SCREENWIDTH, SCREENHEIGHT-90)

class TextField(pygame.Surface):
	"""Creates a textfield to type text and send to the discussion"""
	def __init__(self):
		"""Creates the textfield"""
		if pygame.font:
			self.blink = 0
			self.answerText = "|"
			self.update()

	def update(self):
		"""Update the textfield at every image"""

		# Every 40 images, we change the | by a space, and the space by a |
		# so it makes a blinking effect simulating a cursor
		if self.blink < 40:
			self.blink = self.blink + 1
		else:
			if self.answerText[len(self.answerText)-1] == "|":
				self.answerText = self.answerText[:len(self.answerText)-1] + " "
			elif self.answerText[len(self.answerText)-1] == " ":
				self.answerText = self.answerText[:len(self.answerText)-1] + "|"
			self.blink = 0

		# Creates a text label
		self.font = pygame.font.Font(None, 36)
		self.textSurface = self.font.render(self.answerText, 1, (255, 255, 255), (10, 10, 10))
		self.text = pygame.Surface((SCREENWIDTH, 30))
		self.text.blit(self.textSurface, (0, 0))

	def __convert(self, letter):
		"""Pygame returns words for certain letters, so we need to convert it"""
		if letter == "space":
			return " "
		elif letter == "exclaim":
			return "!"
		else:
			return letter

	def removeLast(self):
		"""Used if the user press Backspace, it removes the last letter"""
		self.answerText = self.answerText[:len(self.answerText)-2] + "|"

	def append(self, letter):
		"""If the user type something, it adds the letter to the surface"""
		letter = self.__convert(letter)
		if self.answerText[len(self.answerText)-1] == "|" or self.answerText[len(self.answerText)-1] == " ":
			self.answerText = self.answerText[:len(self.answerText)-1] + letter + "|"
		else:
			self.answerText = self.answerText + letter + "|"

	def outputText(self):
		"""If the user press Enter, we put the text in the self.returnText variable, and empty the label"""
		self.returnText = self.answerText[:len(self.answerText)-1]
		self.answerText = "|"

class TextLabel(pygame.Surface):
	"""Creates a text label to show the discussion"""
	def __init__(self):
		"""Create the textlabel"""
		if pygame.font:
			self.answerText = "" # It's the last sentence sent
			self.answerTextOld = "" # It's the last but one sentence sent
			self.update()

	def add(self, sentence):
		"""Adds a sentence to the text label"""
		self.answerTextOld = self.answerText
		self.answerText = sentence
		self.update()

	def update(self):
		"""Used to create the text labels and apply the changes"""
		self.font = pygame.font.Font(None, 36)

		self.textSurfaceOld = self.font.render(self.answerTextOld, 1, (255, 255, 255), (10, 10, 10))
		self.textOld = pygame.Surface((SCREENWIDTH, 30))
		self.textOld.blit(self.textSurfaceOld, (0, 0))

		self.textSurface = self.font.render(self.answerText, 1, (255, 255, 255), (10, 10, 10))
		self.text = pygame.Surface((SCREENWIDTH, 30))
		self.text.blit(self.textSurface, (0, 0))

class Window(pygame.Surface):
	"""Creates a new window and background"""
	def __init__(self):
		self.screen = pygame.display.set_mode(SCREENRECT.size, 0) # Creates the window
		pygame.display.set_caption(TITLETEXT) # Sets the title of the window

		#Creates the background
		self.background = pygame.Surface(self.screen.get_size())
		self.background = self.background.convert()
		self.background.fill((250, 250, 250))

		#Display The Background
		self.screen.blit(self.background, (0, 0))
		pygame.display.flip()

	def update(self):
		"""Used to refresh the background at every frame"""
		self.screen.blit(self.background, (0, 0))

def main():
	"""this function is called when the program starts.
   	it initializes everything it needs, then runs in a loop"""
#Initialize pygame, the repeat for the keys of the keyboard, and creates a window
	pygame.init()
	pygame.key.set_repeat(75, 50)
	window = Window()

#Prepare Game Objects
	clock = pygame.time.Clock()
	characters = {} # Creates a dictionary for characters sprites
	characters[nickname] = Character() # Adds your character to the dictionary
	sprites = pygame.sprite.RenderPlain([characters[nickname]]) # Render your character as a pygame sprite

	textfield = TextField() # Creates the textfield
	textlabel = TextLabel() # Creates the textlabel (discussion)

	# Creates a socket and connects to the server
	clisock = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
	clisock.connect((host, port))
	clisock.send("HELO\0" + nickname + "\0MAS Chat Client Prototype\00\n") # Sends an identifying message
	descriptors = [clisock] # Creates a list with the socket (because the select function works with lists)

	directionXOld = 0 # Used to compare if the direction has changed between two frames
	directionYOld = 0

#Main Loop
	while 1:
		clock.tick(FRAMES_PER_SEC)

		(sread, swrite, sexc) = select.select( descriptors, [], [], 0.01) # Gets the state of the socket

		# Loops in the active sockets (in fact there is maximum one socket active, but we
		# have to use a loop because select() returns a list)
		for sock in sread:
			strfuck = sock.recv(100) # Gets the message received from the server

			if strfuck != '':
				print strfuck # If the message is not empty, it can be used
				strcrap = strfuck.split("\n") # the "\n" character is the separator for protocol instructions
				# Every protocol instruction must finish by a "\n" character

				for strgnou in strcrap:
					# If the string is empty, we don't treat it
					if strgnou != "":
						strcrap2 = strgnou.split("\0") # the "\0" character is the separator for instruction arguments
						follow = 0

						# If the argument begins with a ":" character, the it's a prefix
						# A prefix contains the nicknames concerned by the instruction
						# example: ":Mario\0MESS\0Hello" means Mario says Hello
						if strcrap2[0][0] == ":":
							nickused = strcrap2[0].strip(":")
							follow = 1 # If there is a prefix, we have to shift the place of the argument
							# example: in "MESS\0Hello" the MESS is at the first place, and in ":Mario\0MESS\0Hello", the MESS is at the second place

						if strcrap2[0+follow] == "MESS":
							strshow = strcrap2[1+follow]
							if follow == 1:
								strshow = nickused + ": " + strshow # If there is a prefix, we add it to before the message
							else:
								strshow = "Server: " + strshow # If there is no prefix, it's a server message
							textlabel.add(strshow) # Adds the message to the text label

						elif strcrap2[1] == "JOIN":
							newCharacter = Character() # JOIN means there is a new chatter, so we add a new character
							characters[nickused] = newCharacter # Adds it to the character dictionary
							sprites.add(characters[nickused]) # and adds it to the pygame sprites

						elif strcrap2[1] == "MOVE":
							characters[nickused].move(int(strcrap2[2]), int(strcrap2[3]))

		# Gets the pygame events, such as key pressed
		for event in pygame.event.get():
			# QUIT is for clicking on the Close button
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
			elif event.type == KEYDOWN:
				# Closes the program if Escape is pressed
				if event.key == K_ESCAPE:
					pygame.quit()
					sys.exit()
				elif event.key == K_BACKSPACE:
					textfield.removeLast()
				elif event.key == K_RETURN:
					# If the string is not empty, it send the returnText to the textlabel for adding
					if len(textfield.answerText) > 1:
						textfield.outputText()
						print "You:", textfield.returnText
						textlabel.add("You: " + textfield.returnText)
						clisock.send("MESS\0" + textfield.returnText + "\n") # Sends the message
				elif event.key in ALLOWEDLETTER:
					textfield.append(pygame.key.name(event.key))

				# Gets the states of the arrow keys
				keystate = pygame.key.get_pressed()
				directionX = keystate[K_RIGHT] - keystate[K_LEFT]
				directionY = keystate[K_DOWN] - keystate[K_UP]
				if directionX != directionXOld or directionY != directionYOld:
					characters[nickname].move(directionX, directionY) # Moves the sprite
					clisock.send("MOVE\0" + str(directionX) + "\0" + str(directionY) + "\n") # Sends the new direction

		textfield.update() # Refresh the text label
		sprites.update() # Refresh the sprites
		window.update() # Refresh the background

	#Draws Everything
		window.background.blit(textfield.text, (0, SCREENHEIGHT-30))
		window.background.blit(textlabel.textOld, (0, 0))
		window.background.blit(textlabel.text, (0, 30))
		sprites.draw(window.screen)
		pygame.display.flip()

#Game Over


#this calls the 'main' function when this script is executed
if __name__ == '__main__': main()
