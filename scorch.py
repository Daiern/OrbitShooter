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

player = pygame.image.load("resources/Sprites/playerShip.png")
playerScaled = pygame.transform.scale(player, (25, 25))

greenPlanet = pygame.image.load("resources/Sprites/greenPlanet.png")

bulletImage = pygame.image.load("resources/Sprites/projectile.png")

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
		self.mass = .001
		self.prograde = False
		self.retro = False
		self.image = player
		self.rect = self.image.get_rect()
		self.radius = self.rect.width/2
		self.health = shipFullHealth

	def move(self):
		self.pos = [self.pos[0] + self.vel[0], self.pos[1] + self.vel[1]]
		self.rect.x = self.pos[0]
		self.rect.y = self.pos[1]

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
		self.vel = [0, 0.0]
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


G = 6.67e-11
pi = np.pi
cos = np.cos

orbiter = Ship(0, 0)
orbiter2 = Ship(1, width-(player.get_size()[0]))

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

bullet = Bullet([-10.0, -10.0]) #initialize the bullet that will be fired by each player

healthBarLength = 200



def bulletCoM():
	bulletImageSize = bulletImage.get_size()
	return [bullet.pos[0]+bulletImageSize[0]/2, bullet.pos[1]+bulletImageSize[1]/2]

def CoM(body):
	imageSize = greenPlanet.get_size()
	return [body.pos[0]+imageSize[0]/2, body.pos[1]+imageSize[1]/2]

def r(body):
	return math.sqrt(math.pow(bulletCoM()[0] - CoM(body)[0], 2) + math.pow(bulletCoM()[1] - CoM(body)[1], 2))

def f(body):
	return -1*body.mass*bullet.mass/math.pow(r(body), 2)

def unitVec(body):
	return [(bulletCoM()[0] - CoM(body)[0])/r(body), (bulletCoM()[1] - CoM(body)[1])/r(body)]

def fvec(body):
	return [f(body)*unitVec(body)[0], f(body)*unitVec(body)[1]]

#def fvecScaled():
#	return [(f()*unitVec()[0])/10000000000000, (f()*unitVec()[1])/10000000000000]

def fire(ship):
	bullet.pos = [ship.pos[0], ship.pos[1]]
	bullet.fired = 1

def offScreen(proj):
	if bullet.pos[0] > width or bullet.pos[0] < -10 or bullet.pos[1] > height or bullet.pos[1] < -10:
		return 1

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
				if bullet.fired == 0:
					bullet.pos = [obj.pos[0], obj.pos[1]]
					bullet.vel = [(width/2 - obj.pos[0])/128, 0]
					bullet.fired = 1
		if event.type==pygame.KEYUP:
			if event.key==K_w:
				obj.prograde = False
			if event.key==K_s:
				obj.retro = False

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

def blitObjects(bodyList):
	for body in bodyList:
		screen.blit(greenPlanet, body.pos)
	if bullet.fired == 1:
		screen.blit(bulletImage, bullet.pos)
	screen.blit(player, orbiter.pos)
	screen.blit(player, orbiter2.pos)

def bulletOffscreen():
	if offScreen(bullet):
		bullet.pos = [-10.0, -10.0]
		bullet.vel = [0.0, 0.0]
		bullet.fired = 0
		return 1
	return 0

def doBulletPhysics(bodylist):
	#bullet.vel = [bullet.vel[0]+fvec(moon)[0]+fvec(moon2)[0]+fvec(moon3)[0], bullet.vel[1]+fvec(moon)[1]+fvec(moon2)[1]+fvec(moon3)[1]]
	for body in bodylist:
		bullet.vel[0] = (bullet.vel[0]+fvec(body)[0])
		bullet.vel[1] = (bullet.vel[1]+fvec(body)[1])
	bullet.move()

def blitText(fontSurface):
	screen.blit(fontSurface, (width/2-fontSurface.get_size()[0]/2, height/2-fontSurface.get_size()[1]/2))

def blitWinText(fontSurface):
	screen.blit(fontSurface, (width/2-fontSurface.get_size()[0]/2, height/2-fontSurface.get_size()[1]/2 - 50))

def showTurnFont(player):
	if player == 0:
		blitText(player1FontSurface)
	if player == 1:
		blitText(player2FontSurface)
	pygame.display.flip()
	pygame.time.delay(1000)

def cleanUpKeys():
	orbiter.prograde = False
	orbiter.retro = False
	orbiter2.prograde = False
	orbiter2.retro = False

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



turnOver = 0

winner = -1

pointList = [orbiter.pos, orbiter.pos]

##############################
######## GAME LOOP ###########
##############################
def turnLoop(player):
	turnFontShown = 0
	turnOver = 0
	bullet.damage = 0
	pygame.draw.lines(screen, (0,0,255), False, pointList, 4)
	while not turnOver:
		screen.fill(0)

		timeElapsed = clock.tick(60)

		blitObjects(bodyList)

		drawHealthBars()

		#pygame.display.flip()

		if turnFontShown == 0:		#this is to make sure the font is always shown for the whole turn
			showTurnFont(player)
			turnFontShown = 1

		if player == 0:
			checkKeyEvent(orbiter) #check for keypresses for moving and firing
		if player == 1:
			checkKeyEvent(orbiter2)

		if player == 0:
			doBurn(orbiter) #move the orbiter
		if player == 1:
			doBurn(orbiter2) #move the orbiter


		if bullet.fired == 1:
			doBulletPhysics(bodyList)
			#pointList.append(bullet.pos)
		
		#pygame.draw.lines(screen, (0,0,255), False, pointList, 4)

		print pointList

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


	print "Player", winner+1, "wins!"


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