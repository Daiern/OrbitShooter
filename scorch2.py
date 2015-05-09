# 1 - Import library
import pygame
from pygame.locals import *
import math
import numpy as np

# 2 - Initialize the game
pygame.init()
width, height = 1000, 700
shipFullHealth = 2000
screen=pygame.display.set_mode((width, height))

background = pygame.image.load("resources/Sprites/spaceBackground.png")

clock = pygame.time.Clock()

playerImg = pygame.image.load("resources/Sprites/playerShip.png")
playerScaled = pygame.transform.scale(playerImg, (25, 25))

greenPlanet = pygame.image.load("resources/Sprites/greenPlanet.png")

bulletImage = pygame.image.load("resources/Sprites/projectile.png")

crosshair = pygame.image.load("resources/Sprites/crosshair.png")

mainFont = pygame.font.Font("resources/Fonts/DeconStruct-Black.ttf", 32)
mainFontSurface = mainFont.render("Orbit Shooter Thing!", 1, (30,210,50))

player1FontSurface = mainFont.render("Player 1 Fire!", 1, (30,210,50))

player2FontSurface = mainFont.render("Player 2 Fire!", 1, (30,210,50))

player1WinFontSurface = mainFont.render("Player 1 Wins!", 1, (30,210,50))

player2WinFontSurface = mainFont.render("Player 2 Wins!", 1, (30,210,50))

gameOverFontSurface = mainFont.render("Game Over!", 1, (30,210,50))

#define classes of sprites

class Ship(pygame.sprite.Sprite):
	def __init__(self, n, position):
		pygame.sprite.Sprite.__init__(self)
		playerNumber = n
		self.vel = [0.0, 0.0]
		self.pos = [position,height/2]
		self.mass = .0011
		self.prograde = False
		self.retro = False
		self.image = playerImg
		self.rect = self.image.get_rect()
		self.radius = self.rect.width/2
		self.health = shipFullHealth
		self.currentWeapon = Bullet(self.pos)

	def move(self):
		self.pos = [self.pos[0] + self.vel[0], self.pos[1] + self.vel[1]]
		self.rect.x = self.pos[0]
		self.rect.y = self.pos[1]
		
	def changeWeapon(self):
		self.currentWeapon

class Planet(pygame.sprite.Sprite):
	def __init__(self):
		pygame.sprite.Sprite.__init__(self)
		self.pos=[width/2-70,height/2-70]
		#self.mass=7.34e22
		self.mass=1000000
		self.image = greenPlanet
		self.rect = self.image.get_rect()
		self.radius = self.rect.width/2

class Bullet(pygame.sprite.Sprite):
	def __init__(self, position):
		pygame.sprite.Sprite.__init__(self)
		self.mass = .001
		self.vel = [0.0, 0.0]
		self.pos = position
		self.fired = 0
		self.image = bulletImage
		self.rect = self.image.get_rect()
		self.radius = self.rect.width/2
		self.damage = 0


	def move(self):
		self.pos = [self.pos[0] + self.vel[0], self.pos[1] + self.vel[1]]
		self.rect.x = self.pos[0]
		self.rect.y = self.pos[1]
		self.damage += abs(self.vel[0]) + abs(self.vel[1])
		
#init classes		

orbiter = Ship(0, 0)
orbiter2 = Ship(1, width-(playerImg.get_size()[0]))

orbiter.rect.x = orbiter.pos[0]
orbiter.rect.y = orbiter.pos[1]
orbiter2.rect.x = orbiter2.pos[0]
orbiter2.rect.y = orbiter2.pos[1]

moon = Planet()
moon2 = Planet()
moon3 = Planet()
moon4 = Planet()

moon.pos = [moon.pos[0]/1.5, moon.pos[1]/1.5]
moon2.pos = [moon2.pos[0]*1.5, moon2.pos[1]*1.5]
moon3.pos = [moon3.pos[0]*1.5, moon3.pos[1]/1.5]
moon4.pos = [moon4.pos[0]/1.5, moon4.pos[1]*1.5]

moon.rect.x = moon.pos[0]
moon.rect.y = moon.pos[1]
moon2.rect.x = moon2.pos[0]
moon2.rect.y = moon2.pos[1]
moon3.rect.x = moon3.pos[0]
moon3.rect.y = moon3.pos[1]
moon4.rect.x = moon4.pos[0]
moon4.rect.y = moon4.pos[1]

bodyList = [moon, moon2, moon3, moon4]
bodyImageList = [moon.image, moon2.image, moon3.image, moon4.image]

bodyGroup = pygame.sprite.Group()
bodyGroup.add(moon)
bodyGroup.add(moon2)
bodyGroup.add(moon3)
bodyGroup.add(moon4)

player1Group = pygame.sprite.Group()
player1Group.add(orbiter)

player2Group = pygame.sprite.Group()
player2Group.add(orbiter2)

healthBarLength = 200

player1Colour = (0,0,255)
player2Colour = (255,0,0)

#############################
######SUPPORT FUNCTIONS######
#############################

#find the centre of mass of a body with a sprite
def CoM(body):
	imageSize = body.image.get_size()
	return [body.pos[0]+imageSize[0]/2, body.pos[1]+imageSize[1]/2]
	
#returns the distance between two points
def r(body, wep):
	return math.sqrt(math.pow(CoM(wep)[0] - CoM(body)[0], 2) + math.pow(CoM(wep)[1] - CoM(body)[1], 2))
	
#returns the total attraction force magnitude between the bullet and a body
def f(body, wep):
	return -1*body.mass*wep.mass/math.pow(r(body, wep), 2)
	
#find the unit vector (x,y) of the distance between a body and the bullet
def unitVec(body, wep):
	return [(CoM(wep)[0] - CoM(body)[0])/r(body, wep), (CoM(wep)[1] - CoM(body)[1])/r(body, wep)]
	
#returns the x and y components of the attraction force
def fvec(body, wep):
	return [f(body, wep)*unitVec(body, wep)[0], f(body, wep)*unitVec(body, wep)[1]]
	
#test to see if the bullet has gone offscreen
def offScreen(wep):
	if wep.pos[0] > width or wep.pos[0] < -10 or wep.pos[1] > height or wep.pos[1] < -10:
		return 1
		
#return the magnitude of the distance between a body and the mouse pointer
def rMouse(body):
	return math.sqrt(math.pow(CoM(body)[0] - pygame.mouse.get_pos()[0], 2) + math.pow(CoM(body)[1] - pygame.mouse.get_pos()[1], 2))
	
#return the (x,y) unit vector of the distance from a body to the mouse
def mouseUnitVec(ship):
	return [(pygame.mouse.get_pos()[0] - CoM(ship)[0])/rMouse(ship), (pygame.mouse.get_pos()[1]-CoM(ship)[1])/rMouse(ship)]

#check key events, loops during game
def checkKeyEvent(obj):
	for event in pygame.event.get():
		if event.type==pygame.QUIT:
			pygame.quit()
			exit(0)
		if event.type==pygame.KEYDOWN:
			if event.key==K_w:
				obj.prograde = True
			if event.key==K_s:
				obj.retro = True
			if event.key==K_SPACE:
				if obj.currentWeapon.fired == 0:
					obj.currentWeapon.pos = CoM(obj)
					obj.currentWeapon.vel = [4*mouseUnitVec(obj)[0], 4*mouseUnitVec(obj)[1]]
					bodyList.append(obj.currentWeapon)
					obj.currentWeapon.fired = 1
		#if event.type==pygame.KEYDOWN:
			#if event.key==K_e:
				#obj.nextWep()
			#if event.key==K_q:
				#obj.prevWep()
		if event.type==pygame.KEYUP:
			if event.key==K_w:
				obj.prograde = False
			if event.key==K_s:
				obj.retro = False	

#move the ship up or down based on keypresses
def doBurn(obj):
	if obj.prograde == True:
		if obj.pos[1] <= 0:
			obj.pos = [obj.pos[0], 0]
			obj.rect.x = obj.pos[0]
			obj.rect.y = obj.pos[1]
		else:
			obj.pos = [obj.pos[0], obj.pos[1]-1]
			obj.rect.x = obj.pos[0]
			obj.rect.y = obj.pos[1]
	if obj.retro == True:
		if obj.pos[1] >= height-obj.image.get_size()[1]:
			obj.pos = [obj.pos[0], height-obj.image.get_size()[1]]
			obj.rect.x = obj.pos[0]
			obj.rect.y = obj.pos[1]
		else:
			obj.pos = [obj.pos[0], obj.pos[1]+1]
			obj.rect.x = obj.pos[0]
			obj.rect.y = obj.pos[1]
			
def blitText(fontSurface):
	screen.blit(fontSurface, (width/2-fontSurface.get_size()[0]/2, height/2-fontSurface.get_size()[1]/2))

def blitWinText(fontSurface):
	screen.blit(fontSurface, (width/2-fontSurface.get_size()[0]/2, height/2-fontSurface.get_size()[1]/2 - 50))

#go through the planets and apply the velocity based on gravitational attraction
def doBulletPhysics(wep, bodylist):
	for body in bodylist:
		if body != wep:
			wep.vel[0] = (wep.vel[0]+fvec(body, wep)[0])
			wep.vel[1] = (wep.vel[1]+fvec(body, wep)[1])
	wep.move()

#blit the text to display whose turn it is
def showTurnFont(player):
	if player == 0:
		blitText(player1FontSurface)
	if player == 1:
		blitText(player2FontSurface)
	pygame.display.flip()
	pygame.time.delay(1000)
			
#reset all keys to unpressed before turn starts
def cleanUpKeys():
	orbiter.prograde = False
	orbiter.retro = False
	orbiter2.prograde = False
	orbiter2.retro = False

def drawHealthBars():
	percentHealth = orbiter.health/shipFullHealth
	healthBar = pygame.Rect(100, 20, healthBarLength*percentHealth, 20)
	pygame.draw.rect(screen, (200,0,0), healthBar, 0)

	healthBarOutline = pygame.Rect(100, 20, healthBarLength, 20)
	pygame.draw.rect(screen, (30,210,50), healthBarOutline, 5)

	percentHealth = orbiter2.health/shipFullHealth
	healthBar = pygame.Rect(width-healthBarLength*percentHealth-100, 20, healthBarLength*percentHealth, 20)
	pygame.draw.rect(screen, (200,0,0), healthBar, 0)

	healthBarOutline = pygame.Rect(width-300, 20, healthBarLength, 20)
	pygame.draw.rect(screen, (30,210,50), healthBarOutline, 5)

def drawPoints(pointlist, colour):
	for rect in pointlist:
		pygame.draw.rect(screen, colour, [rect[0], rect[1], 2, 2])
		
#takes a list of objects and uses their 
def blitObjects(bodyList):
	for body in bodyList:
		screen.blit(body.image, body.pos)
	#if bullet.fired == 1:
	#	screen.blit(bulletImage, bullet.pos)
	screen.blit(playerImg, orbiter.pos)
	screen.blit(playerImg, orbiter2.pos)
	mousePos = [pygame.mouse.get_pos()[0]-crosshair.get_size()[0]/2, pygame.mouse.get_pos()[1]-crosshair.get_size()[1]/2]
	screen.blit(crosshair, mousePos)
	
	
def collision(obj, bodylist):
	for body in bodylist:
		if pygame.sprite.spritecollide(obj, bodylist, False, pygame.sprite.collide_circle):
		#	bullet.pos = [-10.0, -10.0]
		#	bullet.rect.x = bullet.pos[0]
		#	bullet.rect.y = bullet.pos[1]
		#	bullet.vel = [0.0, 0.0]
		#	bullet.fired = 0
			print pygame.sprite.spritecollide(obj, bodylist, False, pygame.sprite.collide_circle)
			return True
		else:
			print "No Collided"
			return False
		
turnOver = 0

winner = -1

player1PointList = []
player2PointList = []

##############################
######## GAME LOOP ###########
##############################
def turnLoop(player):
	turnFontShown = 0
	turnOver = 0
	pointListTimer = 0
	while not turnOver:
		screen.fill(0)

		timeElapsed = clock.tick(60)

		blitObjects(bodyList)

		drawHealthBars()

		if turnFontShown == 0:		#this is to make sure the font is always shown for the whole turn
			showTurnFont(player)
			turnFontShown = 1			

		if player == 0:
			orbiter.currentWeapon.damage = 0
			checkKeyEvent(orbiter)
			doBurn(orbiter) #move the orbiter
			if orbiter.currentWeapon.fired == 1:
				doBulletPhysics(orbiter.currentWeapon, bodyList)
				if collision(orbiter.currentWeapon, bodyGroup) or offScreen(orbiter.currentWeapon):
					orbiter.currentWeapon.fired = 0
					orbiter.currentWeapon.vel = [0.0, 0.0]
					bodyList.remove(orbiter.currentWeapon)
					turnOver = 1
				if pointListTimer == 0:
					player1PointList.append(CoM(orbiter.currentWeapon))
					
		if player == 1:
			orbiter2.currentWeapon.damage = 0
			checkKeyEvent(orbiter2)
			doBurn(orbiter2) #move the orbiter
			if orbiter2.currentWeapon.fired == 1:
				doBulletPhysics(orbiter2.currentWeapon, bodyList)
				if collision(orbiter2.currentWeapon, bodyGroup) or offScreen(orbiter2.currentWeapon):
					orbiter2.currentWeapon.fired = 0
					orbiter2.currentWeapon.vel = [0.0, 0.0]
					bodyList.remove(orbiter2.currentWeapon)
					turnOver = 1
				if pointListTimer == 0:
					player2PointList.append(CoM(orbiter2.currentWeapon))

		drawPoints(player1PointList, player1Colour)
		drawPoints(player2PointList, player2Colour)

		if player == 0:
			if collision(orbiter.currentWeapon, player2Group):
				orbiter2.health = orbiter2.health - orbiter.currentWeapon.damage
				turnOver = 1
				print orbiter2.health
				if orbiter2.health < 0:
					return 0

		if player == 1:
			if collision(orbiter2.currentWeapon, player1Group):
				orbiter.health = orbiter.health - orbiter2.currentWeapon.damage
				turnOver = 1
				print orbiter.health
				if orbiter.health < 0:
					return 1

		pygame.display.flip()

		pointListTimer = pointListTimer + 1
		if pointListTimer > 4:
			pointListTimer = 0

	return -1
	
def gameLoop():
	player = 0
	pygame.mouse.set_visible(0)
	blitText(mainFontSurface)
	drawPoints(player1PointList, player1Colour)
	drawPoints(player2PointList, player2Colour)
	pygame.display.flip()
	pygame.time.delay(2000)
	while 1:
		winner = turnLoop(player)
		cleanUpKeys() #ensures that keyup events happen so the ship doesn't move on it's own
		if player == 0:
			player = 1
		else:
			player = 0
		
		for event in pygame.event.get():
			if event.type==pygame.QUIT:
			# if it is quit the game
				pygame.quit()
				exit(0)

		if winner != -1:
			return winner


#Shows the Game Over text and the winner after a player dies
def gameOver(winner):
	while 1:
		screen.fill(0)
		blitText(gameOverFontSurface)
		if winner == 0:
			blitWinText(player1WinFontSurface)
		if winner == 1:
			blitWinText(player2WinFontSurface)
		
		pygame.display.flip()

		for event in pygame.event.get():
			if event.type==pygame.QUIT:
			# if it is quit the game
				pygame.quit()
				exit(0)
				
gameOver(gameLoop()) #game loop returns a winner