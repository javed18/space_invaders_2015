import pygame
import time
import thread
from copy import copy
from random import randint
from sprites import *
from Audio import audio
from sched import scheduler

sched = scheduler(time.time, time.sleep)

class Controller():
    _score = 0;
    _lives = 3;
    _gameover = 0
    def __init__(self,n,m,screen,speed):
        self._font = pygame.font.SysFont("monospace", 16)
        self.scoretext = self._font.render("Score: "+str(self._score), 1, (0,255,0))
        self.lifetext = self._font.render("Lives: "+str(self._lives), 1, (0,255,0))
        self.leveltext = self._font.render("Level: "+str(speed), 1, (0,255,0))
        self._screen = screen
        self._rowNo = n;
        self._columnNo = m;
        self.no_of_enemies = n*m
        self.direction ="LEFT"
        self.moveDownFlag = 0
        self.enemyArray = []
        for i in range(self._rowNo):
            self.enemyArray.append([])
            for j in range(self._columnNo):
                enemy1 = Enemy([15,10],[60+i*30,80+j*25],speed)
                self.enemyArray[i].append(copy(enemy1))
        self.bullet = []
        for i in range(0,3):
            self.bullet.append(Bullet([0,0],"DOWN"))
            delay = randint(1, 7)
            self.bullet[i].bulletFlag = -delay
            sched.enter(delay, 1, self.bullet[i].run, ())
        thread.start_new_thread(sched.run, ())
        self.boss = None
    
    def bulletUpdate(self,i):
        if self.bullet[i].bulletFlag == 0:
            random_row = randint(0,self._rowNo-1)
            random_column = randint(0,self._columnNo-1)
            if (self.enemyArray[random_row][random_column]. \
                    enemyFlag != 1):
                return
            bullet_x = self.enemyArray[random_row][random_column].rect.x
            bullet_y = self.enemyArray[random_row][random_column].rect.y
            self.bullet[i] = Bullet([bullet_x,bullet_y],"DOWN")
            audio.enemyFire()
            self.bullet[i].run()
    
    def blit(self):
        for i in range(0,3):
            self.bulletUpdate(i)
            if self.bullet[i].bulletFlag > 0:
                self._screen.blit(self.bullet[i].image,self.bullet[i].rect)
        self.moveDownFlag =  self.moveDownFlag +1
        self.flipDirection()
        self._screen.blit(self.scoretext,(50,50))
        self._screen.blit(self.lifetext,(450,50))
        self._screen.blit(self.leveltext,(250,50))
        for enemylist in self.enemyArray:
            for enemy in enemylist:
                if (enemy.enemyFlag == 1):
                    enemy.updateDirection(self.direction)
                    self._screen.blit(enemy.image,enemy.rect)
                    enemy.update()
                    if (self.moveDownFlag  == 200):
                        enemy.moveDown();
        if (self.moveDownFlag  == 200):
            self.moveDownFlag = 0

        if self.boss is not None:
            self.boss.update()
            self._screen.blit(self.boss.image, self.boss.rect)
        elif (self._score % 1000 == 0):
            self.boss = BossEnemy((0,0));



    def flipDirection(self):
        for enemylist in self.enemyArray:
            for enemy in enemylist:
                if (enemy.enemyFlag == 1):
                    if (enemy.checkposX() == 1):
                        self.direction = "LEFT"
                    if (enemy.checkposX() == -1):
                        self.direction = "RIGHT";

    def collision(self,bullet):
        for enemylist in self.enemyArray:
            for enemy in enemylist: 
                self.collision_check(enemy,bullet)
        if self.boss is not None and bullet.bulletFlag > 0:
            if self.boss.rect.colliderect(bullet.rect):
                self._score += 600;
                self.scoretext = self._font.render("Score = "+str(self._score), 1, (0,255,0))
                self.boss = None
                bullet.bulletFlag = 0

    def collision_check(self,enemy,bullet):
        if (enemy.enemyFlag == 1):
            if (enemy.reached_destiny() == 1):
                self._gameover = 1

            if bullet.bulletFlag > 0 and enemy.rect.colliderect(bullet.rect):
                enemy.enemyFlag = 0
                enemy.rect =None
                audio.hit()
                bullet.bulletFlag = 0
                self._score = self._score + 100;
                self.scoretext = self._font.render("Score = "+str(self._score), 1, (0,255,0))
                self._screen.blit(self.scoretext,(50,50))
                self.no_of_enemies = self.no_of_enemies -1 
    
    def player_collision_check(self,player):
        for cbullet in self.bullet:
            if cbullet.bulletFlag > 0 and player.rect.colliderect(cbullet.rect):
                audio.playerHit()
                self._lives = self._lives -1;
                self.lifetext = self._font.render(
                        "Lives = "+str(self._lives), 1, (0,255,0))
                cbullet.bulletFlag = 0
    
    def gameover(self):
        if self._lives  < 0 or self._gameover == 1:
            return True
        else:
            return False

    def level_complete():
        if self.no_of_enemies == 0:
            return 1
        else:
            return 0
