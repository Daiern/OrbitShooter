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

background = pygame.image.load("resources/Sprites/spaceBackground.png") #Set background image to a space background

clock = pygame.time.Clock() #clock is used for game timing and frame limiting

player = pygame.image.load("resources/Sprites/playerShip.png")
playerScaled = pygame.transform.scale(player, (25, 25)) #scale ship to correct size for window

greenPlanet = pygame.image.load("resources/Sprites/greenPlanet.png") #greenplanet is used as sprite for all planets

bulletImage = pygame.image.load("resources/Sprites/projectile.png")

#Loading fonts for the intro, turn and win screens
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
		self.pos = [position,height/2] #different position for each players ship, both starting mid height
		self.mass = .001
		self.prograde = False #used to move ship up
		self.retro = False #used to move ship down
		self.image = player
		self.rect = self.image.get_rect() #used in collision detection
		self.radius = self.rect.width/2 #used in collision detection
		self.health = shipFullHealth

	def move(self):
		self.pos = [self.pos[0] + self.vel[0], self.pos[1] + self.vel[1]]
		self.rect.x = self.pos[0]
		self.rect.y = self.pos[1]

class Planet(pygame.sprite.Sprite):
	def __init__(self):
		pygame.sprite.Sprite.__init__(self)
		self.pos=[width/2-70,height/2-70] #currently the default position, this is changed after initialization
		#self.mass=7.34e22
		self.mass=1000000 #arbitrary mass for orbital force, NOT TO SCALE
		self.image = greenPlanet
		self.rect = self.image.get_rect() #used for collision
		self.radius = self.rect.width/2	#used for collision

class Bullet(pygame.sprite.Sprite):
	def __init__(self, position):
		pygame.sprite.Sprite.__init__(self)
		self.mass = .001
		self.vel = [0.0, 0.0]
		self.pos = position
		self.fired = 0
		self.image = bulletImage
		self.rect = self.image.get_rect() #used for collision
		self.radius = self.rect.width/2 #used for collision
		self.damage = 0


	def move(self):
		self.pos = [self.pos[0] + self.vel[0], self.pos[1] + self.vel[1]]
		self.rect.x = self.pos[0]
		self.rect.y = self.pos[1]
		self.damage += abs(self.vel[0]) + abs(self.vel[1])


G = 6.67e-11
pi = np.pi
cos = np.cos

orbiter = Ship(0, 0) #player 1's ship
orbiter2 = Ship(1, width-(player.get_size()[0])) #player 2's ship

#setting the position of the sprites rectangles used for collision
orbiter.rect.x = orbiter.pos[0] 
orbiter.rect.y = orbiter.pos[1]
orbiter2.rect.x = orbiter2.pos[0]
orbiter2.rect.y = orbiter2.pos[1]

#instantiate the planets, called moons because legacy naming :/
moon = Planet()
moon2 = Planet()
moon3 = Planet()
moon4 = Planet()

#set all the moons position, needs to be moved to the class
moon.pos = [moon.pos[0]/1.5, moon.pos[1]/1.5]
moon2.pos = [moon2.pos[0]*1.5, moon2.pos[1]*1.5]
moon3.pos = [moon3.pos[0]*1.5, moon3.pos[1]/1.5]
moon4.pos = [moon4.pos[0]/1.5, moon4.pos[1]*1.5]

#set all the collision rectangle positions, can also probably be moved to class definition
moon.rect.x = moon.pos[0]
moon.rect.y = moon.pos[1]
moon2.rect.x = moon2.pos[0]
moon2.rect.y = moon2.pos[1]
moon3.rect.x = moon3.pos[0]
moon3.rect.y = moon3.pos[1]
moon4.rect.x = moon4.pos[0]
moon4.rect.y = moon4.pos[1]

#add moons and their images into lists
bodyList = [moon, moon2, moon3, moon4]
bodyImageList = [moon.image, moon2.image, moon3.image, moon4.image]

#add all moons to a pygame Group for use in the collision functions
bodyGroup = pygame.sprite.Group()
bodyGroup.add(moon)
bodyGroup.add(moon2)
bodyGroup.add(moon3)
bodyGroup.add(moon4)

#add both player ships to groups for use in collision functions
player1Group = pygame.sprite.Group()
player1Group.add(orbiter)
player2Group = pygame.sprite.Group()
player2Group.add(orbiter2)

bullet = Bullet([-10.0, -10.0]) #initialize the bullet that will be fired by each player, offscreen

healthBarLength = 200 #used in the drwaing of the health bar, not the value of health

#colours used for tracing the path of each shot from each player
player1Colour = (0,0,255)
player2Colour = (255,0,0)

#find the centre of mass of the bullet, really just the position of the centre of the sprite
def bulletCoM():
	bulletImageSize = bulletImage.get_size()
	return [bullet.pos[0]+bulletImageSize[0]/2, bullet.pos[1]+bulletImageSize[1]/2]

#same as above but for other bodies
def CoM(body):
	imageSize = body.image.get_size()
	return [body.pos[0]+imageSize[0]/2, body.pos[1]+imageSize[1]/2]

#distance from the bullet's centre of mass to a body's centre of mass
def r(body):
	return math.sqrt(math.pow(bulletCoM()[0] - CoM(body)[0], 2) + math.pow(bulletCoM()[1] - CoM(body)[1], 2))

#calculated force on the bullet from a given body
def f(body):
	return -1*body.mass*bullet.mass/math.pow(r(body), 2)

#the distance unit vectors from bullet to body, used in fvec to caculate strength of x and y force
def unitVec(body):
	return [(bulletCoM()[0] - CoM(body)[0])/r(body), (bulletCoM()[1] - CoM(body)[1])/r(body)]

#applied force on body in the x and y directions
def fvec(body):
	return [f(body)*unitVec(body)[0], f(body)*unitVec(body)[1]]

#def fvecScaled():
#	return [(f()*unitVec()[0])/10000000000000, (f()*unitVec()[1])/10000000000000]

#when player fires the bullet goes from the ship that fired towards the mouse
def fire(ship):
	bullet.pos = [ship.pos[0], ship.pos[1]]
	bullet.fired = 1

#used to calculate if the bullet is offscreen
def offScreen(proj):
	if bullet.pos[0] > width or bullet.pos[0] < -10 or bullet.pos[1] > height or bullet.pos[1] < -10:
		return 1

#distance from mouse to bullet
def rMouse():
	return math.sqrt(math.pow(bulletCoM()[0] - pygame.mouse.get_pos()[0], 2) + math.pow(bulletCoM()[1] - pygame.mouse.get_pos()[1], 2))

#unit vector of above calculation
def mouseUnitVec(ship):
	return [(ship.pos[0] - pygame.mouse.get_pos()[0])/rMouse(), (ship.pos[1] - pygame.mouse.get_pos()[1])/rMouse()]


def checkKeyEvent(obj):
	for event in pygame.event.get():
		if event.type==pygame.QUIT:
			pygame.quit()
			exit(0)
		if event.type==pygame.KEYDOWN:
			if event.key==K_w:	    #press W key
				obj.prograde = True #move up
			if event.key==K_s:	 #press S key
				obj.retro = True #move down
			if event.key==K_SPACE:
				if bullet.fired == 0:	#check to make sure player can't fire more than one bullet per turn
					bullet.pos = [obj.pos[0], obj.pos[1]]
					bullet.vel = [4*-mouseUnitVec(obj)[0], 4*-mouseUnitVec(obj)[1]]
					bullet.fired = 1
		if event.type==pygame.KEYUP: #check for held keys
			if event.key==K_w:
				obj.prograde = False
			if event.key==K_s:
				obj.retro = False

#moves ship up or down based on imput
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

#simple blit function for all bodies in the game
def blitObjects(bodyList):
	for body in bodyList:
		screen.blit(greenPlanet, body.pos)
	if bullet.fired == 1:
		screen.blit(bulletImage, bullet.pos)
	screen.blit(player, orbiter.pos)
	screen.blit(player, orbiter2.pos)


#reset bullet position to a non-visible position when it has left the screen
def bulletOffscreen():
	if offScreen(bullet):
		bullet.pos = [-10.0, -10.0]
		bullet.vel = [0.0, 0.0]
		bullet.fired = 0
		return 1
	return 0

#where all the magic happens, all force calculation done here (only applies to bullet)
def doBulletPhysics(bodylist):
	#bullet.vel = [bullet.vel[0]+fvec(moon)[0]+fvec(moon2)[0]+fvec(moon3)[0], bullet.vel[1]+fvec(moon)[1]+fvec(moon2)[1]+fvec(moon3)[1]]
	for body in bodylist:
		bullet.vel[0] = (bullet.vel[0]+fvec(body)[0])
		bullet.vel[1] = (bullet.vel[1]+fvec(body)[1])
	bullet.move()

#simple functions for font blitting
def blitText(fontSurface):
	screen.blit(fontSurface, (width/2-fontSurface.get_size()[0]/2, height/2-fontSurface.get_size()[1]/2))

def blitWinText(fontSurface):
	screen.blit(fontSurface, (width/2-fontSurface.get_size()[0]/2, height/2-fontSurface.get_size()[1]/2 - 50))

#shows different text for each players turns
def showTurnFont(player):
	if player == 0:
		blitText(player1FontSurface)
	if player == 1:
		blitText(player2FontSurface)
	pygame.display.flip()
	pygame.time.delay(1000)

#ensures that there is no movement from player after their turn is over (if they haven't released the key)
def cleanUpKeys():
	orbiter.prograde = False
	orbiter.retro = False
	orbiter2.prograde = False
	orbiter2.retro = False

#check collision of bullet with other bodies
def collision(obj, bodylist):
	for body in bodylist:
		if pygame.sprite.spritecollide(obj, bodylist, False, pygame.sprite.collide_circle):
			bullet.pos = [-10.0, -10.0]
			bullet.rect.x = bullet.pos[0]
			bullet.rect.y = bullet.pos[1]
			bullet.vel = [0.0, 0.0]
			bullet.fired = 0
			return True
		else:
			return False

#draw simple health bars with the rect fuctions in pygame
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

#used for drawing trail behind the bullet to show player where they have fired
def drawPoints(pointlist, colour):
	for rect in pointlist:
		pygame.draw.rect(screen, colour, [rect[0], rect[1], 2, 2])



turnOver = 0 #set to 1 when the bullet is offscreen

winner = -1 

player1PointList = [bullet.pos]
player2PointList = [bullet.pos]

##############################
######## GAME LOOP ###########
##############################
def turnLoop(player):
	turnFontShown = 0
	turnOver = 0
	bullet.damage = 0
	pointListTimer = 0
	while not turnOver:
		screen.fill(0)

		timeElapsed = clock.tick(60)

		blitObjects(bodyList)

		drawHealthBars()

		pygame.draw.line(screen, (255,255,255), orbiter.pos, pygame.mouse.get_pos())

		if turnFontShown == 0:		#this is to make sure the font is always shown for the whole turn
			showTurnFont(player)
			turnFontShown = 1			

		if player == 0:
			checkKeyEvent(orbiter)
			doBurn(orbiter) #move the orbiter
			if bullet.fired == 1:
				doBulletPhysics(bodyList)
				if pointListTimer == 0:
					player1PointList.append(bulletCoM())
		if player == 1:
			checkKeyEvent(orbiter2)
			doBurn(orbiter2) #move the orbiter
			if bullet.fired == 1:
				doBulletPhysics(bodyList)
				if pointListTimer == 0:
					player2PointList.append(bulletCoM())

		drawPoints(player1PointList, player1Colour)
		drawPoints(player2PointList, player2Colour)

		if collision(bullet, bodyList):
			turnOver = 1

		if player == 0:
			if collision(bullet, player2Group):
				orbiter2.health = orbiter2.health - bullet.damage
				turnOver = 1
				print orbiter2.health
				if orbiter2.health < 0:
					return 0

		if player == 1:
			if collision(bullet, player1Group):
				orbiter.health = orbiter.health - bullet.damage
				turnOver = 1
				print orbiter.health
				if orbiter.health < 0:
					return 1

		if bulletOffscreen():
			turnOver = 1

		pygame.display.flip()

		pointListTimer = pointListTimer + 1
		if pointListTimer > 4:
			pointListTimer = 0

	return -1


def gameLoop():
	player = 0
	blitText(mainFontSurface)
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


gameOver(gameLoop())
