import sys
import time
import random
import math
import os
import pickle

class Position():
  def __init__(self, x=0, y=0, theta=0):
    self.x = x
    self.y = y
    self.theta = theta
    
  

class Robot():
  __infrared_port = "A1"
  
  __left_motor = "M3"
  
  __right_motor = "M4"
  
  __left_encoder = "E3"
  
  __right_encoder = "E4"
  
  """Number of signals from encoder until full rotate"""
  __calls_per_rotate = 360
  
  __wheel_diameter = 5.6
  
  __track_width = 15.4
  
  __wheel_length = __wheel_diameter * math.pi
 
  __gyro_callback = lambda x: None
  
  __position = Position()
  
  __points_cloud = []
  
  left_motor_on = brick.motor(__left_motor).setPower
  
  right_motor_on = brick.motor(__right_motor).setPower
  
  left_motor_off = brick.motor(__left_motor).powerOff
  
  right_motor_off = brick.motor(__right_motor).powerOff
 
  
  def __init__(self, gyro_callback):
    self.__gyro_callback = gyro_callback
#    brick.setCalibrationValues([0, 0, 0, 7824, 0, 4025])
    pass
    
    
  def calibrate_gyroscope(self, time):
    brick.gyroscope().calibrate(time)
    script.wait(time)
    print(brick.gyroscope().getCalibrationValues())
    script.wait(1000)
    
  
  def travel_along_wall(self, v):
    i = 0
    while True:
      dist = brick.sensor(self.__infrared_port).read()
      if (40 > dist and dist > 20):
        i = 0
        self.left_motor_on(v)
        self.right_motor_on(v)
        
      elif (dist <= 20):
        i = 0
        self.left_motor_on(-v)
        self.right_motor_on(v)
        
      else:
        self.left_motor_on(v)
        self.right_motor_on(-v + i)
        i += 1
      
      script.wait(50)
  
  """ Launch the robot at 's' with speed 'v'
  
  Keyword arguments:
    v - speed at percent (from -100 to 100)
    s - distance at sm
  """
  def run(self, v, s):
    
    limit = s / self.__wheel_length * self.__calls_per_rotate
    
    
    self.left_motor_on(v)
    self.right_motor_on(v)
    
    brick.encoder(self.__left_encoder).reset() 
    while abs(brick.encoder(self.__left_encoder).readRawData()) < limit:
      script.wait(10)
    
    self.left_motor_off()
    self.right_motor_off()
  
  
  """ Launch the robot at 's' with speed 'v'
  
  Keyword arguments:
    v - speed at percent (from -100 to 100). 
    If v > 0, then robot rotate clockwise.  
    If v < 0, then robot rotate counterclockwise
    alpha - angle at radian
  """
  def rotate(self, alpha, v=100):
    assert(v != 0)
    if alpha < 0:
      v = -v
    r = self.__track_width / 2
    limit = r * alpha / self.__wheel_length * self.__calls_per_rotate
    
    self.left_motor_on(-v)
    self.right_motor_on(v)
    
    brick.encoder(self.__left_encoder).reset() 
    while abs(brick.encoder(self.__left_encoder).readRawData()) < abs(limit):
      script.wait(10)
    
    self.left_motor_off()
    self.right_motor_off()
  
  def rotate_gyroscope(self, alpha, v=100):
   
    initial = self.__gyro_callback()
    target = alpha * 360 / 2 / math.pi
    sgn = 1 if target < 0 else -1
    
    self.left_motor_on(-sgn * v)
    self.right_motor_on(sgn * v)
     
    while abs(self.__gyro_callback() - initial) < abs(target):
#      print(initial, target, self.__gyro_callback(), (self.__gyro_callback() - initial))
      script.wait(10)
    
    self.left_motor_off()
    self.right_motor_off()
  
  def run_using_gyroscope(self, s, v=100):
    limit = s / self.__wheel_length * self.__calls_per_rotate
    initial = self.__gyro_callback()
    
    self.left_motor_on(v)
    self.right_motor_on(v)
    
    brick.encoder(self.__left_encoder).reset() 
    while abs(brick.encoder(self.__left_encoder).read()) < limit:
      current_angle = self.__gyro_callback()
      d_angle = (current_angle - initial)
      
      self.left_motor_on(v + d_angle)
      self.right_motor_on(v - d_angle)
      script.wait(10)
    
    self.left_motor_off()
    self.right_motor_off()
  
  def test_lidar(self):
    script.wait(1000)
    vec = brick.lidar().read()
    print(vec)
    print(len(vec))
    rad = 180 / math.pi
    brick.display().clear()
    minX = 10000
    minY = 10000
    
    for i in range(0, 360):
      phi = i / rad
      dist = vec[i]
      
      x1 = dist * math.cos(phi)
      y1 = dist * math.sin(phi)
      minX = min(minX, x1)
      minY = min(minY, y1)

      
      x = (x1 / 2) + 100
      y = (y1 / 2) + 100
      brick.display().drawPoint(int(x), int(y))
    brick.display().redraw()
    script.wait(4000)
    return
  
  def lidar_measure(self):
    script.wait(100)
    vec = brick.lidar().read()
    print(vec)
    rad = 180 / math.pi
    pos = self.__position
    
    for i in range(0, 360):
      phi = i / rad - pos.theta
      dist = vec[i]
      if dist == 0:
        continue
      x1 = dist * math.cos(phi) + pos.x
      y1 = dist * math.sin(phi) - pos.y
            
      self.__points_cloud.append((x1, y1))
 
 
  def draw_points(self):
    brick.display().clear()
    
    for point in self.__points_cloud:
      x = (point[0] / 6) + 50
      y = (point[1] / 6) + 50
      brick.display().drawPoint(int(x), int(y))
    
    brick.display().redraw()
    script.wait(1)
    
    
  
  def set_absolute_direction(self, target):
    source = self.__gyro_callback()
    source = -source / 360 * 2 * math.pi    
    theta = math.atan2(math.sin(target-source), math.cos(target-source))
    self.rotate_gyroscope(theta, 50) 
    self.__position.theta = target
    
    
  def goto(self, new_position: Position):
    angle = math.atan2(new_position.y - self.__position.y, new_position.x - self.__position.x,)
    self.set_absolute_direction(angle)
    self.__position.theta = angle
    dist = ((new_position.x - self.__position.x)**2 +  (new_position.y - self.__position.y)**2)**(1/2)
    self.run_using_gyroscope(dist)
    if new_position.theta != None:
      self.set_absolute_direction(new_position.theta)
      self.__position = new_position
    else:
      self.__position.x = new_position.x
      self.__position.y = new_position.y
    


  

class Program():
  __interpretation_started_timestamp__ = time.time() * 1000
  __initial_angle = 0
  __last_angle = 0
  __n = 0
  
  def __init__(self):
    self.robot = Robot(self.get_angle_val_degrees)
    __initial_angle = brick.gyroscope().read()[-1] / 1000
    __last_angle = __initial_angle
    

  def angle_val(self):
    current_angle = brick.gyroscope().read()[-1]
    current_angle /= 1000
    if abs(current_angle) > 170 and current_angle * self.__last_angle < 0:
      self.__n += 1 if self.__last_angle > current_angle else -1
    
    """if 90000 < self.__last_angle and self.__last_angle < 180000 and current_angle > -180000 and current_angle < -90000:
      self.__n += 1
    elif 90000 < current_angle and current_angle < 180000 and self.__last_angle > -180000 and self.__last_angle < -90000:
      self.__n -= 1"""
    self.__last_angle = current_angle

  def print_angle_val_degrees(self):
    current_angle = self.__last_angle
    current_angle += self.__n * 360
    print(current_angle)

  def get_angle_val_degrees(self):
    self.angle_val()
    current_angle = self.__last_angle
    current_angle += self.__n * 360
    return current_angle

    
    
  def execMain(self):    
    self.robot.calibrate_gyroscope(1)
    
    with open('C:\\Users\\aleks\\PycharmProjects\\TRIK-geo\\data\maps\\gradients_lists.pickle', 'rb') as handle:
      gradients = pickle.load(handle)
#      print(gradients)
   
      x = 0
      y = 0
      theta = 210
      alpha = 10
      factor = 3
      
    for i in range(100):
      print(i)
      dx = gradients[0][y+120][x+150]
      dy = gradients[1][y+120][x+150]
      
      x = int(x - alpha * dx)
      y = int(y - alpha * dy)
      self.robot.goto(Position(x*factor, y*factor, None))
        
        
    
    


#    self.robot.lidar_measure()
#    self.robot.draw_points()
    
#    self.robot.goto(Position(400, 0, None))
#    self.robot.lidar_measure()
#    self.robot.draw_points()
    
    script.wait(100000)
    brick.stop()
    return

def main():
  program = Program()
  program.execMain()

if __name__ == '__main__':
  main()
