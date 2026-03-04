"""
Subcontroller module for Alien Invaders

This module contains the subcontroller to manage a single level or wave in
the Alien Invaders game.  Instances of Wave represent a single wave. Whenever
you move to a new level, you are expected to make a new instance of the class.

The subcontroller Wave manages the ship, the aliens and any laser bolts on
screen. These are model objects.  Their classes are defined in models.py.

Most of your work on this assignment will be in either this module or
models.py. Whether a helper method belongs in this module or models.py is
often a complicated issue.  If you do not know, ask on Piazza and we will
answer.

Jack Lehman (jsl369), Arefa (ar955)
December 11th, 2023
"""
from game2d import *
from consts import *
from models import *
import random

# PRIMARY RULE: Wave can only access attributes in models.py via getters/setters
# Wave is NOT allowed to access anything in app.py (Subcontrollers are not
# permitted to access anything in their parent. To see why, take CS 3152)


class Wave(object):
    """
    This class controls a single level or wave of Alien Invaders.

    This subcontroller has a reference to the ship, aliens, and any laser bolts
    on screen. It animates the laser bolts, removing any aliens as necessary.
    It also marches the aliens back and forth across the screen until they are
    all destroyed or they reach the defense line (at which point the player
    loses). When the wave is complete, you  should create a NEW instance of
    Wave (in Invaders) if you want to make a new wave of aliens.

    If you want to pause the game, tell this controller to draw, but do not
    update.  See subcontrollers.py from Lecture 24 for an example.  This
    class will be similar to than one in how it interacts with the main class
    Invaders.

    All of the attributes of this class ar to be hidden. You may find that
    you want to access an attribute in class Invaders. It is okay if you do,
    but you MAY NOT ACCESS THE ATTRIBUTES DIRECTLY. You must use a getter
    and/or setter for any attribute that you need to access in Invaders.
    Only add the getters and setters that you need for Invaders. You can keep
    everything else hidden.

    """
    # HIDDEN ATTRIBUTES:
    # Attribute _ship: the player ship to control
    # Invariant: _ship is a Ship object or None
    #
    # Attribute _aliens: the 2d list of aliens in the wave
    # Invariant: _aliens is a rectangular 2d list containing Alien objects or None
    #
    # Attribute _bolts: the laser bolts currently on screen
    # Invariant: _bolts is a list of Bolt objects, possibly empty
    #
    # Attribute _dline: the defensive line being protected
    # Invariant : _dline is a GPath object
    #
    # Attribute _lives: the number of lives left
    # Invariant: _lives is an int >= 0
    #
    # Attribute _time: the amount of time since the last Alien "step"
    # Invariant: _time is a float >= 0s
    #
    # Attribute _right: if the aliens are moving right or left
    # Invariant: _right is a boolean
    #
    # Attribute _reverse: if the alien is in the process of reversing
    # Invariant: _reverse is a boolean
    #
    # Attribute _collided: True if the ship currently collides with an alien bolt
    # Invariant: _collided is a boolean, starts as False
    #
    # Attribute _fire: number of steps until the alien fires a bolt
    # Invariant: _fire is an int in range [0,BOLT_RATE]
    #
    # Attribute _wavenum: the number of the current wave, starting at 0
    # Invariant: _wavenum is an int in range [0,infinity] - inclusive
    #
    # Attribute _steps: the number of steps the aliens have taken
    # Invariant: _steps int in the range [0,infinity]
    # You may change any attribute above, as long as you update the invariant
    # You may also add any new attributes as long as you document them.
    # LIST MORE ATTRIBUTES (AND THEIR INVARIANTS) HERE IF NECESSARY


    # GETTERS AND SETTERS (ONLY ADD IF YOU NEED THEM)
    def getAliens(self):
        """returns the 2d list of aliens in the wave"""
        return self._aliens
    def getShip(self):
        """returns the player's ship to control"""
        return self._ship
    def getDline(self):
        """returns the defensive line being protected"""
        return self._dline
    def createAliens(self):
        """a helper function that creates the 2d list of aliens in the wave"""
        y=GAME_HEIGHT-ALIEN_CEILING + (ALIEN_HEIGHT/2)
        for row in range(ALIEN_ROWS):
            x=ALIEN_H_SEP + ALIEN_WIDTH/2
            aliens = []
            for col in range(ALIENS_IN_ROW):
                bot = ALIEN_ROWS-1
                index = (bot-row)%6//2
                a = Alien(x,y,ALIEN_WIDTH,ALIEN_HEIGHT,ALIEN_IMAGES[index])
                aliens.append(a)
                x=x+(ALIEN_H_SEP+ALIEN_WIDTH)
            self._aliens.append(aliens)
            y=y+(-ALIEN_V_SEP-ALIEN_HEIGHT)
    def setShip(self):
        """creates the player's ship to control"""
        x=GAME_WIDTH/2
        y=SHIP_BOTTOM+SHIP_HEIGHT/2
        ship=Ship(x,y,SHIP_WIDTH,SHIP_HEIGHT,SHIP_IMAGE[0])
        self._ship=ship
    def setDline(self):
        """helper function that creates the defensive line being protected"""
        dline=GPath(points=[0,DEFENSE_LINE,GAME_WIDTH,DEFENSE_LINE],linewidth=2,linecolor='black')
        self._dline=dline
    def getTime(self):
        """returns the amount of time since the last Alien 'step'"""
        return self._time
    def setTime(self,x):
        """
        sets the amount of time since the the last Alien 'step'
        precondition: x is an int or float and x>=0s
        """
        assert isinstance(x,int) or isinstance(x,float)
        assert x>=0
        self._time = x
    def getLives(self):
        """returns the number of lives left"""
        return self._lives
    def getCollided(self):
        """returns True if the players bolt collides with this alien"""
        return self._collided
    # INITIALIZER (standard form) TO CREATE SHIP AND ALIENS
    def __init__(self,wave,lives):
        """
        Initializes ship, aliens, and laser bolt
        parameter: wave is the number of the current wave
        parameter: lives is the current number of lives left
        precondition: wave is an int or float in range [0,infinity), starts at 0
        precondition: lives is an int or float [1,infinity], starts at 3
        """
        assert isinstance(wave,int) or isinstance(wave,float)
        assert isinstance(lives,int) or isinstance(lives,float)
        assert wave>=0
        assert lives>=1
        self._aliens = []
        self.createAliens()
        self._collided = False
        self._steps = 1
        self._lives = lives
        self._right = True
        self._reverse = False
        self._time = ALIEN_SPEED
        self._wavenum = wave
        self._bolts = []
        if BOLT_RATE<=self._wavenum+1:
            self._fire = 0
        else:
            self._fire = random.randrange(1,(BOLT_RATE-self._wavenum))
        self.setShip()
        self.setDline()

    def update(self,input,dt):
        """"
        animates the ship, aliens, and laser bolt
        parameter: input is the user's input on the keyboard
        parameter: dt is the time in seconds since the last call to update
        precondition: input is a GInput object
        precondition: dt is an int or float and dt>=0
        """
        assert isinstance(input,GInput)
        assert isinstance(dt,int) or isinstance(dt,float)
        assert dt>=0
        if self._collided:
            self.setShip()
            self._collided = False
        self.alienCollide()
        self.checkPlayerCollide()
        if not self._ship is None:
            x = self._ship.x
            if input.is_key_down('left'):
                self._ship.x=max(x-SHIP_MOVEMENT,SHIP_WIDTH/2)
            if input.is_key_down('right'):
                self._ship.x=min(x+SHIP_MOVEMENT,GAME_WIDTH-SHIP_WIDTH/2)
        if self._time>ALIEN_SPEED:
            self.moveAliens()
            self.alienFire()
            self._steps = self._steps + 1
        else:
            self.setTime(self._time + dt*((1 + (self._wavenum/500))**self._steps))
        if input.is_key_down('up') and self.noBolts() and not self._ship is None:
            b = Bolt(self._ship.x,SHIP_BOTTOM+SHIP_HEIGHT+(BOLT_HEIGHT/2),BOLT_SPEED)
            self._bolts.append(b)
        self.moveBolts()

    def moveAliens(self):
        """
        determines if the aliens should move right, left or reverse,
        then calls the respective helper functions to move them
        """
        if self._reverse:
            self.alienReverse()
        elif self._right:
            self.alienRight()
        else:
            self.alienLeft()

    def alienRight(self):
        """
        moves all aliens one step to the right, and then sets the
        time since last alien step to 0s
        """
        self._reverse = False
        self.setTime(ALIEN_SPEED)
        rev = False
        for row in self._aliens:
            for col in row:
                if not col is None:
                    col.x = col.x + ALIEN_H_WALK
                    if col.x > GAME_WIDTH-ALIEN_WIDTH/2-ALIEN_H_WALK:
                        self._reverse = True
        self.setTime(0)

    def alienLeft(self):
        """
        moves all aliens one step to the left, and then sets the
        time since last alien step to 0s
        """
        self._reverse = False
        for row in self._aliens:
            for col in row:
                if not col is None:
                    col.x = col.x - ALIEN_H_WALK
                    if col.x < ALIEN_WIDTH/2+ALIEN_H_WALK:
                        self._reverse = True
        self.setTime(0)

    def alienReverse(self):
        """
        determines if the alien is in the process of reversing,
        if moves all aliens one step down, changes the direction of the aliens
        and then sets the time since last alien step to 0s
        """
        self._reverse = False
        for row in self._aliens:
            for col in row:
                if not col is None:
                    col.y = col.y - ALIEN_V_WALK
        self._right = not self._right
        self.setTime(0)

    def noBolts(self):
        """fruitful function that goes through all bolts and removes the ones
        that are out of frame, returns True if there are no bolts that belong to
        the player in the frame, false otherwise"""
        for bolts in self._bolts:
            if bolts.y<GAME_HEIGHT-(BOLT_HEIGHT/2) and bolts.y>-BOLT_HEIGHT:
                if bolts._velocity>0:
                    return False
            elif bolts._velocity>0:
                self._bolts.remove(bolts)
        return True

    def moveBolts(self):
        """
        moves all of the bolts in self._bolts one step in the y direction
        by their respective velocities
        """
        for bolts in self._bolts:
            bolts.y = bolts.y + bolts._velocity

    def alienCollide(self):
        """
        determines if an alien has been struck by a bolt; if so, removes
        the bolt from self._bolts and sets the hit alien to None
        """
        for row in self._aliens:
            for col in range(len(row)):
                if not row[col] is None and row[col].collides(self.playerBolt()):
                    row[col] = None
                    self._bolts.remove(self.playerBolt())

    def playerBolt(self):
        """
        returns the bolt in self._bolts that was shot from the player and is
        currently in frame; returns None if there are none
        """
        for bolts in self._bolts:
            if bolts._velocity>0:
                return bolts
        return []


    def chooseAlien(self):
        """
        Helper function that returns the lowest alien in a random non-empty
        column. If there are no non-empty columns, returns None
        """
        a = []
        for col in range(len(self._aliens[0])):
            done = False
            for row in reversed(self._aliens):
                if row[col] != None and done == False:
                    a.append(row[col])
                    done = True
        if len(a) == 0:
            return None
        return random.choice(a)

    def alienFire(self):
        """
        Calls chooseAlien as a helper function to determine which alien fires a
        bolt, then fires a bolt from that alien and adds the bolt to self._bolts
        """
        if self._fire == 0:
            a = self.chooseAlien()
            if not a is None:
                b = Bolt(a.x,a.y-(ALIEN_HEIGHT/2)-(BOLT_HEIGHT/2),-BOLT_SPEED)
                self._bolts.append(b)
                if BOLT_RATE<=self._wavenum+1:
                    self._fire = 0
                else:
                    self._fire = random.randrange(1,BOLT_RATE-self._wavenum)
        else:
            self._fire = self._fire-1

    def checkWin(self):
        """returns True if the player has won the round, otherwise returns False"""
        if self.chooseAlien() is None:
            self._bolts = []
            return True
        return False

    def checkLoss(self):
        """
        Returns True if the player has lost the game, checking if the player's
        lives have reached 0 or if the aliens have crossed the defense line
        otherwise, return False
        """
        if self._lives == 0 or self.checkCross():
            self._bolts = []
            return True
        return False

    def checkCross(self):
        """
        helper for checkLoss, returns True if any of the aliens in self._aliens
        have crossed the defense line, returns False otherwise
        """
        for row in self._aliens:
            for col in row:
                if not col is None:
                    if col.y-(ALIEN_HEIGHT/2)<= DEFENSE_LINE:
                        return True
        return False

    def checkPlayerCollide(self):
        """
        Checks if an alien bolt has collided with the players ship; if so, it
        removes all bolts, decreases self._lives by 1, sets the ship to None
        and sets self._collided equal to True
        """
        for bolts in self._bolts:
            if self._ship.collides(bolts) and bolts._velocity<0:
                self._bolts = []
                self._lives = self._lives - 1
                self._ship = None
                self._collided = True
                return True
        return False

    def isGameOver(self):
        """
        Returns True if the player has completed the wave,
        returns False if the player lost the game; calls helpers checkWin()
        and checkLoss()"""
        if self.checkWin() or self.checkLoss():
            return True
        return False

    def draw(self,view):
        """
        Draws the ship, aliens, defensive line, and bolts
        """
        for row in self._aliens:
            for alien in row:
                if not alien is None:
                    alien.draw(view)
        if not self._ship is None:
            self._ship.draw(view)
        self._dline.draw(view)
        for bolts in self._bolts:
            bolts.draw(view)
