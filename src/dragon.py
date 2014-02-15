import pygame
import random
import math
import time
from pygame.locals import *


####################
# Custom Settings: #
####################
maxAmmo    = 40   #: Recharges to this amt
maxHuts    = 15   #: Game ends at this point
maxArchers = 3    #: Max on screen at once
archerProb = 0.996#: 1-P(archers to appear)
screenX    = 800  #: Resolution scaling will
screenY    = 600  #   affect the terrain size
frameRate  = 60.0 #: Broken, adj. for speed 
playerHp   = 4    #: Max is 5

# Color settings:
clr_clay   = (210,80,50)
clr_red    = (210,20,10)
clr_gold   = (210,130,50)
clr_orange = (0xf6,0x5b,0x16)
clr_brown  = (80,50,30)
clr_sky    = (80,130,210)
clr_faded  = (50,80,130)
clr_white  = (210,210,210)
clr_grey   = (130,130,130)
clr_char   = (30,30,30)
clr_black  = (0,0,0)

# Scenery colors:
skyColor     = clr_sky
horizonColor = clr_faded
groundColor  = clr_brown


# System variables:
m_px = 0.1  # m/px?
frameCount = 0
ft = float(1.0/frameRate)
cellWidth = screenX/10
scroll_pos = 0
fired = 0
bullets = []
arrows  = []
archers = []
huts    = {}
huts_seen = 0
huts_passed = 0
g_mod = 6.0  # Make gravity stronger 
terrain_length = 4096
default_height = 4.5
terrain_rand = 2.5
hills = []
horizon = []
playerHpCurr = playerHp

# Player animations:
anim = []
anim_idx = 0
for filename in ["1.gif","2.gif","3.gif",
                 "4.gif","5.gif","6.gif"]:
  anim.append(pygame.image.load(filename))

# Archer animations:
anim2 = []
for filename in ["archer1.gif",
                 "archer2.gif",
                 "archer3.gif",
                 "archer4.gif",
                 "archer5.gif",
                 "archer6.gif",
                 "archer7.gif",
                 "archer8.gif",
                 "archer9.gif"
]:
  anim2.append(pygame.image.load(filename))

# Life icon:
life_icon = pygame.image.load("rose.gif")

# Random "wind" functions for flames:
n2fs = [lambda x: x*x,
        lambda x: pow(x,1.8),
        lambda x: pow(x,2.1)]

nfs  = [lambda x: x*8.0,
        lambda x: x*7.0,
        lambda x: x*6.0]


##############
# Hut class: #
##############
class Hut():
  def __init__(o):
    o.hp = random.randint(5,6)
    o.off = 0
    o.alive = True
    o.seen = False
    o.passed = False
    o.position = None,None
    o.flame = []
    o.f1 = n2fs[random.randint(0,2)]
    o.f2 = nfs[random.randint(0,2)]
    for _i in range(0,9):
      o.flame.append(0)

  def draw(o):
    _hx,_hy, = o.position
    if o.hp > 0:
      _houseColor = clr_grey
      _roofColor = clr_clay
    else:
      _houseColor = clr_char
      _roofColor = clr_black
    pygame.draw.rect(screen,_houseColor,
                     pygame.Rect(_hx-21,
                                 _hy-21,
                                 42, 26))
    pygame.draw.polygon(screen,_roofColor,
                         [(_hx-23,_hy-21),
                          (_hx+23,_hy-21),
                         (_hx,_hy-34)])
    if o.hp < 1:
      _clrs = [clr_clay,clr_gold]
      if (frameCount+o.off)%(frameRate*.05) == 0:
        o.flame[0] = (o.flame[0]+1)%55
        if o.flame[0] < 8:
         o.flame[o.flame[0]] = 1
      _flk = [5,8,13,21,34]
      for _j in range(0,7):
        if (_j % 2) > 0:
          if ((frameCount+o.off)/8)%5 == 0:
            _clr = clr_red
          else:
            _clr = clr_orange
        else:
          if ((frameCount+o.off)/8)%5 == 0:
            _clr = clr_orange
          else:
            _clr = clr_red
        if o.flame[_j+1] > 0:
          if ((frameCount+o.off)
              % _flk[random.randint(0,4)]) == 0:
            pygame.draw.polygon(screen,_clr,\
                          [(_hx-11+o.f1(_j),_hy-13-o.f2(_j)),
                           (_hx+10+o.f1(_j),_hy-13-o.f2(_j)),
                           (_hx+o.f1(_j),_hy-34-o.f2(_j))])
          else:
            pygame.draw.rect(screen,_clr,
                             pygame.Rect(_hx-11+o.f1(_j),
                                         _hy-34-o.f2(_j),
                                         21,21))


#################
# Player class: #
#################
class Player:
  def __init__(o):
    o.position = cellWidth*2.2,screenY*0.4
    o.velocity = 24.0,10.0
    o.hpos = cellWidth*2.2
    o.ammo = maxAmmo
    o.score = 0
    o.lastLifeAt = 0
    o.hp = playerHpCurr
    
  def gravity(o,ground):
    _g = -9.8/2 # not to scale
    _velx,_vely = o.velocity
    _vely += _g
    _velx *= 0.9975
    _posx,_posy = o.position
    if _posy >= screenY-ground: 
      _posy = screenY-ground-1
      _vely = 0.0
      _velx = 0.0
    else:
      _posy -= _vely/frameRate  # down is up!
    o.position = _posx,_posy
    o.velocity = _velx,_vely


################
# Arrow class: #
################
class Arrow:
  def __init__(o,pos,vel):
    o.position = pos
    o.velocity = vel

  def draw(o):
    _pxp,_pyp = player.position
    _xp,_yp = o.position
    _xc = _xp-_pxp
    _yc = screenY - _yp
    pygame.draw.rect(screen,(random.randint(0,255),
                             random.randint(0,255),
                             random.randint(0,255)),
                     pygame.Rect(_xc,_yc,5,5))

  def move(o):
    _xp,_yp = o.position
    _xv,_yv = o.velocity
    _xp += _xv
    _yp += _yv
    o.position = _xp,_yp


#################
# Archer class: #
#################
class Archer:
  def __init__(o):
    o.hp = random.randint(2,3)
    o.alive = True
    o.off = 0
    _pxp,_ = player.position
    _pxv,_ = player.velocity
    _xp = _pxp+screenX+(_pxv*m_px)
    o.position = _xp,ground_at(_xp)
    o.velocity = -2.0*random.random(),0
    o.fired = False

  def fire_at(o,tpx,tpy):  # ignores target
    _str  = 4.0
    _avx  = -3.0
    _avy  = random.randint(2,4)
    _avel = _avx,_avy
    _a = Arrow(o.position,_avel)
    arrows.append(_a)

  def draw(o):
    _pxp,_ = player.position
    _pxv,_ = player.velocity
    _xp,_yp = o.position
    _xv,_yv = o.velocity
    if _xp < _pxp: 
      archers.remove(o)
      return
    if (frameCount%60 == 0):
      if random.random() > 0.92:
        if _xv != 0:
          _xv = 0
          o.fired = False
        elif o.fired:
          _xv = -2.0*random.random()
          o.fired=False
    _xp += _xv
    _xc = _xp - _pxp
    if _xc < 0:
      archers.remove(o)
    _yp = ground_at(_xp)
    o.position = _xp,_yp
    o.velocity = _xv,_yv
    _ground = screenY-_yp
    if o.alive:
      if _xv != 0: _idx = int(frameCount*2*_xv/frameRate)%2+1
      else:        _idx = 0
    else:
      _idx = min(3+int((8+frameCount - o.off)/13), 8)
      if _idx > 4:
        if _idx == 8: _xv = 0
        else: _xv = 2.0-4.0*random.random()
        o.velocity = _xv,_yv
    screen.blit(anim2[_idx],
                (int(_xc)-17,int(_ground)-27))
  
    


###############
# Shot class: #
###############
class Shot:
  def __init__(o,pos):
    o.position = pos
    o.started = scroll_pos
    o.current = scroll_pos
    o.speed = 5.75+0.5*random.random()
    o.reduce = 0
    o.reload = 0.009

  def move(o):
    _posx,_posy = o.position
    _xp,_ = player.position
    _velx,_vely = player.velocity
    _posx += o.speed - _velx*m_px
    o.speed *= 0.994
    _posy += 3
    _ground = ground_at(_xp+_posx)
    if _posy > screenY-_ground+15:
      bullets.remove(o)
      flame_hit(_posx,_posy)
    o.position = _posx,_posy

  def draw(o):
    _posx,_posy = o.position
    pygame.draw.circle(screen,     
                       clr_gold,
                       (int(_posx),int(_posy)),
                       5)  # Radius


###################
# Initialization: #
###################
# Initialize terrain:
for _i in range(0,terrain_length):
  hills.append(default_height)
  horizon.append(default_height+terrain_rand)

# Fractalize hills:
def frac_hills(a, lo, hi):
  mid = (hi+lo)/2
  if mid == lo: return
  a[mid] = (a[lo] + a[hi])/2
  a[mid] += terrain_rand/2 - random.random()*terrain_rand
  frac_hills(a, lo, mid)
  frac_hills(a, mid, hi)

frac_hills(hills, 0, terrain_length-1)
frac_hills(horizon, 0, terrain_length-1)

# Scale hills, horizon:
hills = map(lambda x: 3.2*pow(abs(x),2.2)+1, hills)
horizon = map(lambda x: 5.1*pow(abs(x),1.6)+1, horizon)

# Player init:
player = Player()

# Pygame library init:
pygame.init()

# Set up fonts:
pygame.font.init()
out_font = pygame.font.Font("EG_Dragon_Caps.ttf", 24)
out2_font = pygame.font.Font("freesansbold.ttf", 42)

# Set up screen surface:
icon   = pygame.image.load('ico.gif')
pygame.display.set_icon(icon)
pygame.display.set_caption('Return of the Dragon')
screen = pygame.display.set_mode((screenX,screenY))

# Initialize Huts: 
for _i in range(0,10):
  huts[_i] = None
for _i in range(10,terrain_length-1):
  if (random.random() > 0.75) and  \
     (abs((hills[_i+1]+hills[_i-1])/2 - hills[_i]) < 30):
    huts[_i] = Hut()
  else:
    huts[_i] = None

##################
# Main function: #
##################
def main():
  global frameCount
  _dt = 0  # Prev loop runtime
  _loop = True

  game_loop()
  game_title()
  game_loop()
  game_best()
  # Run until flagged to stop:
  while _loop:
    if (_dt < ft):
      _ds = _dt
    else:
      _ds = ft  # Frame(s) behind
    time.sleep(ft-_ds)  # "Sync"
    _t0 = time.clock()
    try:
      _e = pygame.event.poll()
    except: break
    if _e.type == QUIT:
      break
    _loop = game_loop()  
    frameCount += 1
    _tf = time.clock()
    _dt = _tf - _t0
  pygame.quit()

  
#######################
# Draw loop function: #
#######################
def game_loop():
  try:
    screen.fill(skyColor)
  except:
    return False
  global scroll_pos

  ##########
  # World: #
  ##########
  _xp,_ = player.position
  _off = -1*(_xp%cellWidth)
  for _i in range(0, 11):
    _x1 = (_i)*cellWidth
    _xs = scroll_pos*cellWidth
    _x2 = (1+_i)*cellWidth
    _o1 = _o2 = 0
    if _i == 0: _o1 = -_off
    if _i == 10: _o2 = -cellWidth-_off
    _points = [(max(_off+_x1,0),
                 screenY-1-ground_at(_xs+_x1+_o1)),
               (max(_off+_x1,0),
                 screenY-1),
               (min(_off+_x2,screenX),
                 screenY-1),
               (min(_off+_x2,screenX),
                 screenY-1-ground_at(_xs+_x2+_o2))]
    _points2 = [(max(_off+_x1,0),
                 screenY-1-horizon_at(_xs+_x1+_o1)),
               (max(_off+_x1,0),
                 screenY-1),
               (min(_off+_x2,screenX),
                 screenY-1),
               (min(_off+_x2,screenX),
                 screenY-1-horizon_at(_xs+_x2+_o2))]
    pygame.draw.polygon(screen,horizonColor,_points2)
    pygame.draw.polygon(screen,groundColor,_points)
    
  #########
  # Huts: #
  #########
  global huts_seen, huts_passed, huts
  for _i in range(0,11):
    if huts[scroll_pos+_i] != None:
      _h = huts[scroll_pos+_i]
      # Mark hut as seen:
      if (_i == 10) and (not _h.seen):
        _h.seen = True
        huts_seen += 1
        if huts_seen == maxHuts:
          for _j in range(1,11):
            huts[scroll_pos+_i+_j] = None
      elif (_i == 0) and (not _h.passed):
        _h.passed = True
        huts_passed += 1
      

      _ground = ground_at(cellWidth*(scroll_pos+_i+.5))
      _hx = _off+cellWidth*(_i+.5)
      _hy = screenY-_ground+5
      _h.position = _hx,_hy

      # Check if any huts were hit:
      for _s in bullets:
        _spx,_spy = _s.position

        # Hit:
        if pow(pow(_hx-_spx,2)+pow(_hy-_spy,2),.5) < 27:
          if _h.hp > 0: _h.hp -= 1 

          # Hut was just destroyed:
          if (_h.hp == 0) and _h.alive: 
            _xv,_ = player.velocity
            _h.off = frameCount
            player.score += int(
                            pow( (pow(_xv,.5)+1.5)/8.0,
                                 .5)
                            *2500)*10
            game_1up()
            _h.alive = False
          bullets.remove(_s)

      _h.draw()

  ###########
  # ARCHER: # [testing]
  ###########
  if ((random.random() > archerProb) and
      (len(archers) < maxArchers)):
    archers.append(Archer())

  for _ar in archers:
    _arx,_ary = _ar.position
    _px,_py = player.position
    if (not _ar.fired) and (_ar.alive):
      if random.random() > 0.9:
        _ar.fire_at(_arx,_ary)
        _ar.fired = True
    _arx -= _px
    _ary = screenY - _ary
    _ary += 2  # Minor adjustment
    for _s in bullets:    
      _spx,_spy= _s.position

      # Hit:
      if _ar.alive:
        if pow(pow(_arx-_spx,2.0)+pow(_ary-_spy,2.0),.5) < 27:
          if _ar.hp > 0: _ar.hp -= 1 

           # Archer was just killed:
          if (_ar.hp == 0) and _ar.alive: 
            _xv,_ = player.velocity
            _ar.off = frameCount
            player.score += int(
                            pow( (pow(_xv,.5)+1.5)/8.0,
                                 .5)
                            *1000)*10
            game_1up()
            _ar.alive = False

          bullets.remove(_s)

    _ar.draw()
    


              

  ##################
  # Player, input: #
  ##################
  _posx,_posy = player.position
  _ground = ground_at(_posx+player.hpos)
  pygame.event.get()
  _m1,_m2,_m3 = pygame.mouse.get_pressed()
  _vx,_vy = player.velocity

  # Movement input:
  if _m2 > 0 or _m3 > 0:
    _vx = min(_vx+0.23,42.0)  # max=42
    _vy += 13 + 8*random.random()
    if _posy >= screenY-_ground: 
      _posy -= 1
      _vx = 0
    player.velocity = _vx,_vy
    _fcmod = 7
  else: _fcmod = 15
  if _posy < -50:  # Ceiling
    _posy += 15
    _vy = 0.0
    player.velocity = _vx,_vy

  # Update position field, scrolling:
  _posx += _vx*m_px
  scroll_pos = int(_posx / cellWidth)
  player.position = _posx,_posy

  # Shot input:
  global fired
  if (_m1 > 0) and (fired <= 0):
    if player.ammo > 0:
      player.ammo -= 1
      _s = Shot((player.hpos,_posy-35))
      bullets.append( _s )
      fired = _s.reload*frameRate
  fired -= 1  # 'Reload' countdown
  if (frameCount%(frameRate*.1) == 0) and \
     (player.ammo < maxAmmo):
    player.ammo += 1  # 'Recharge'


  ###################
  # Animate player: #
  ###################
  global anim_idx
  if (frameCount % _fcmod) == 0:
    anim_idx = (anim_idx+1)%6
  screen.blit(anim[anim_idx],(player.hpos-50,_posy-50))

  #######
  # UI: #
  #######
  # Render life:
  font_obj = out_font.render("Life:",True,clr_white)
  font_obj_b = out_font.render("Life:",True,clr_char)
  screen.blit(font_obj_b,(21,3))
  screen.blit(font_obj,(22,5))
  for _i in range(0,player.hp-1):
    screen.blit(life_icon, (123+(_i*64),13))
                            

  # Render the score:
  global score_updated
  font_obj = out_font.render(
                    "Score:",
                    True,
                    clr_white)
  font_obj_b = out2_font.render(
                    "{:7,d}".format(player.score),
                    True,
                    clr_white)
  font_obj2 = out_font.render(
                    "Score:", 
                    True,
                    clr_char)
  font_obj2_b = out2_font.render(
                    "{:7,d}".format(player.score),
                    True,
                    clr_char)
  screen.blit(font_obj2,(screenX-375,4))
  screen.blit(font_obj,(screenX-377,5))
  screen.blit(font_obj2_b,(screenX-245,14))
  screen.blit(font_obj_b,(screenX-247,15))


  ######################
  # Check player hits: #
  ######################
  for _arrow in arrows:
    _apx, _apy = _arrow.position
    _ppx, _ppy = player.position
    if _apx < _ppx: arrows.remove(_arrow)
    _apx -= _ppx
    _apy = screenY-_apy
    _apy -= 5  # Minor adjustment
    _ppx = player.hpos
    if pow(pow(_apx-_ppx,2)+pow(_apy-_ppy,2),.5) < 34:
      player.hp -= 1
      arrows.remove(_arrow)
      flame_hit(_apx,_apy)
      if player.hp == 0:
        game_over()
  
  if huts_passed >= maxHuts:
    game_next()
    
  ##################
  # Apply physics: #
  ##################
  player.gravity(ground_at(_posx+player.hpos+1))
  for _shot in bullets:
    _shot.draw()
    _shot.move()
  for _arrow in arrows:
    _arrow.draw()
    _arrow.move()


  #######################
  ### UPDATE DISPLAY: ###
  #######################
  pygame.display.update()

  return True


######################
# Support Functions: #
######################
def ground_at(position):
  return hills[int(position/cellWidth)] +  \
      (hills[int(position/cellWidth)+1]-
       hills[int(position/cellWidth)]) *  \
      (position % cellWidth) / cellWidth

def horizon_at(position):
  return horizon[int(position/cellWidth)] +  \
      (horizon[int(position/cellWidth)+1]-
       horizon[int(position/cellWidth)]) *  \
      (position % cellWidth) /cellWidth

def flame_hit(xpos,ypos):
  _clrs = [clr_gold,
           clr_orange,
           clr_red,
           clr_clay,
           clr_brown]
  # Uses screen coordinates!
  for _j in range(1,6):
    for _i in range(0,360):
      if _i % (64-_j*3-random.randint(0,32)) == 0:
        _r  = 2*pow(_j,1.2)+random.randint(0,8)
        _t  = math.pi*_i/180.0
        _xp = int(xpos + _r * math.cos(_t))
        _yp = int(ypos + _r * math.sin(_t))
        pygame.draw.circle(screen,
                           _clrs[_j-1],
                           (_xp,_yp),
                           1)


def game_prompt(text,dur=0.5,cmax=0.5,bypass=False):
  _wid = []
  _lines = text.split('\n')
  _,_,_y1,_y2,_ = out_font.metrics('D')[0]
  for _i in range(0,len(_lines)):
    _acc = 0
    try:
      for _c in out_font.metrics(_lines[_i]):
        _,_,_,_,_off = _c
        _acc  += _off  
    except:
      pass
    _wid.append(_acc)
  _dy = _y2-_y1
  _clicked = False
  _time = time.time()
  while True:
    pygame.event.get()
    _m1,_,_ = pygame.mouse.get_pressed()
    _top  = screenY/2-(len(_lines)*(_dy+4))/2
    for _i in range(0,len(_lines)):
      font_obj = out_font.render(_lines[_i],True,clr_char)
      font_obj_b = out_font.render(_lines[_i],True,clr_white)
      _left = screenX/2-_wid[_i]/2
      screen.blit(font_obj,(_left+1,_top-2))
      screen.blit(font_obj_b,(_left,_top))
      _top += _dy+8
    pygame.display.update()
    if bypass: break
    if _m1 and ((time.time()-_time) > dur):
      if not _clicked:
        _time = time.time()
        _clicked = True
    if _clicked:
      if not _m1:
        if ((time.time()-_time) > cmax):
          _clicked = False
        else: break
    _e = pygame.event.poll()
    if _e.type == QUIT:
      pygame.quit()
      break
      
def game_over():
  global playerHpCurr, archerProb, maxArchers,  \
        maxHuts, maxAmmo, player, \
        skyColor, horizonColor, groundColor
  game_prompt("GAME\nOVER")
  playerHpCurr = playerHp
  archerProb = 0.996
  maxArchers = 2
  maxHuts = 15
  maxAmmo = 40
  skyColor = clr_sky
  horizonColor = clr_faded
  groundColor = clr_brown
  game_reinit(player.score)
  game_loop()
  game_best()
  player.score = 0
  player.lastLifeAt = 0
  game_loop()
  game_title()


def game_best():
  _scores = game_hiscore()
  _outs = ''
  for _i in range(0,10):
    _init,_score = _scores[_i]
    _score = str(_init) + "    {:13,d}".format(int(_score)) + '\n'
    _outs = _outs+_score.rjust(13)
  game_fade(80,210,210)
  _rule = '========'
  game_prompt(_rule+'  Hall of Eternity  '+_rule+'\n'+
              _outs+
              'game by darren ringer '+
              '(dwringer@gmail.com)\n ')


def game_next():
  game_fade(-50,-50,-50)
  game_prompt("stage\nComplete!")
  global archerProb, maxArchers, maxHuts, playerHpCurr, \
         skyColor, horizonColor, groundColor, maxAmmo
  playerHpCurr = player.hp
  archerProb -= 0.001
  maxArchers += 1
  maxHuts    += 5
  maxAmmo    -= 1
  _sr,_sg,_sb = skyColor
  _hr,_hg,_hb = horizonColor
  _gr,_gg,_gb = groundColor
  for _c in [_sb,_hr,_hg,_gg,_gb]:
    _c = max(0,_c- 50)
  _sr = min(255,_sr+ 50)
  skyColor     = _sr,_sg,_sb
  horizonColor = _hr,_hg,_hb
  groundColor  = _gr,_gg,_gb
  game_reinit(player.score)
  

def game_reinit(score=0):
  global player, huts, hills, horizon, \
         scroll_pos, huts_seen, huts_passed,  \
         bullets, arrows
  if score > 0:
    _lastlife = player.lastLifeAt
  player = Player()
  player.score = score
  if score > 0:
    player.lastLifeAt = _lastlife
  huts = {}
  hills = []
  horizon = []
  bullets = []
  arrows = []
  scroll_pos = 0
  # Initialize terrain:
  for _i in range(0,terrain_length):
    hills.append(default_height)
    horizon.append(default_height+terrain_rand)
  # Fractalize hills:
  frac_hills(hills, 0, terrain_length-1)
  frac_hills(horizon, 0, terrain_length-1)
  # Scale hills, horizon:
  hills = map(lambda x: 3.2*pow(abs(x),2.2)+1, hills)
  horizon = map(lambda x: 5.1*pow(abs(x),1.6)+1, horizon)
  # Initialize Huts: 
  for _i in range(0,10):
    huts[_i] = None
  for _i in range(10,terrain_length-1):
    if (random.random() > 0.75) and  \
       (abs((hills[_i+1]+hills[_i-1])/2 - hills[_i]) < 30):
      huts[_i] = Hut()
    else:
      huts[_i] = None
  huts_seen = 0
  huts_passed = 0


def game_fade(dr=80,dg=80,db=80):
  _pxs = pygame.PixelArray(screen)
  _brush = None
  _last = None
  for _i in range(0,screenY):
    for _j in range(0,screenX):
      _next = _pxs[_j,_i]
      if _next != _last:
        _last = _next
        _s = "0x{:06x}".format(int(_last))
        _r,_g,_b = int(_s[2:4],16),int(_s[4:6],16),int(_s[6:8],16) 
        _r = min(max(0, _r-dr), 255)
        _g = min(max(0, _g-dg), 255)
        _b = min(max(0, _b-db), 255)
        _brush = _r,_g,_b
      _pxs[_j,_i] = _brush
  pygame.display.update()
  del _pxs  # Unlock screen surface
  

def game_title():
  game_fade(130,80,50)
  _img = pygame.image.load("title.gif")
  _ix,_iy = 512,512
  screen.blit(_img,(screenX/2-_ix/2,screenY/2-_iy/2))
  game_prompt("")


def game_hiscore():
  global player
  with open("scores.txt", "r+") as scores:
    _open_pos = scores.tell()
    _his = []
    _outs = ""
    for _line in scores.readlines():
      _line = _line.split()
      _key,_val = _line[0],_line[1]
      _his.append((_key,_val))
    scores.truncate(0)
    _j = 0
    for _init,_score in _his:
      if player.score > int(_score):
        for _i in range(9,_j,-1):
          _his[_i] = _his[_i-1]
        _his[_j] = game_inits(),player.score
        break
      _j += 1
    for _init,_score in _his:
      _outs = _outs + str(_init) + ' ' + str(_score) + '\n'
    scores.seek(_open_pos)
    scores.write(_outs)
  return _his


def game_inits():
  _cstr = ''
  _alphas = [K_a,K_b,K_c,K_d,K_e,K_f,K_g,
             K_h,K_i,K_j,K_k,K_l,K_m,
             K_n,K_o,K_p,K_q,K_r,K_s,K_t,
             K_u,K_v,K_w,K_x,K_y,K_z,
             K_1,K_2,K_3,K_4,K_5,K_6,K_7,
             K_8,K_9,K_0]
  _ltrs = 'abcdefghijklmnopqrstuvwxyz1234567890'
  screen.fill(clr_black)
  _frame = pygame.image.load('frame.gif')
  screen.blit(_frame,(100,160))
  pygame.display.update()
  while True:
    _e = pygame.event.poll()
    if _e.type == KEYDOWN:
      if ((len(_cstr) > 0) and  
          _e.key == K_BACKSPACE):
        _cstr = _cstr[0:len(_cstr)-1]
      elif _e.key == K_RETURN:
        return str(_cstr[0].upper()+
                   _cstr[1]+
                   _cstr[2].upper())
      elif len(_cstr) < 3:
        for _i in range(0,len(_alphas)):
          if _e.key == _alphas[_i]:
            _cstr = _cstr+_ltrs[_i]
            break
      #screen.fill(clr_black)
      #screen.blit(_frame,(100,160))
      pygame.draw.rect(screen, clr_black,
                       pygame.Rect(300,200,200,200))
      pygame.display.update()
    game_prompt(str('Enter your initials:\n'+
                _cstr),bypass=True)


def game_1up():
  global player, playerHpCurr
  if (player.score - player.lastLifeAt) > 1000000:
    player.lastLifeAt = (player.score -
                         (player.score%1000000))
    _newlife = min(5,player.hp+1)
    playerHpCurr = _newlife
    player.hp = _newlife


################
# Run program: #  
################
if __name__ == "__main__":
  main()


