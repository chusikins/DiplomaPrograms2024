import sys
import time
import random
import math
import collections


mLeft= brick.motor(M4)
mRight= brick.motor(M3)
eLeft = brick.encoder(E4)
eRight = brick.encoder(E3)

cpr = 360 #574 # # Counts Per Revolution (CPR)
d = 5.60 #8.3 # # diameter
b = 15.40 #19.5 # # dist between wheels

theta = 0
x_n = 0
y_n = 0
encRight_prev = 0
encLeft_prev = 0

n=0
yawOld = 0
direction = 0 

wall, clear, goal = "#", ".", "*"
width, height = 10, 5

def getYaw():
  global direction, yawOld, n
  yaw = brick.gyroscope().read()[6]/1000
  deltaYaw = yaw - yawOld
  yawOld = yaw
  n += -round(deltaYaw/320) # способ 2
  direction = yaw + n * 360


def odometry():
  global x_n, y_n, theta, encRight_prev, encLeft_prev
  encRight_new = eRight.read()
  encLeft_new = eLeft.read()
  encRight = encRight_new - encRight_prev
  encLeft = encLeft_new - encLeft_prev
  encRight_prev = encRight_new
  encLeft_prev = encLeft_new
  delta_Sr = encRight * 180 * d / cpr
  delta_Sl = encLeft * 180 * d / cpr
  theta = direction
  x_n += (delta_Sr+delta_Sl)*math.pi * math.cos(theta*math.pi/180) / (2*180)
  y_n += (delta_Sr+delta_Sl)*math.pi * math.sin(theta*math.pi/180) / (2*180)
  

def move(x, y):
  eLeft.reset()
  eRight.reset()
  
  angle = math.atan2(y,x)* 180/math.pi
  print(x_n, y_n)
  # поворот на угол к цели
  kp = 1
  print(angle)

  while abs(theta-angle) > 1:
    u = kp * (angle - theta)
    mRight.setPower(-u)
    mLeft.setPower(u)
    script.wait(10)
    #print(abs(theta-angle))
    
  # перемещение к цели
  
  while abs(x_n - x)+abs(y_n-y)>10:
    u = 100 + kp * (x - x_n + y-y_n)
    mRight.setPower(u)
    mLeft.setPower(u)
    script.wait(10)
    print(abs(x_n-x)+abs(y_n-y))
    
  mLeft.brake()
  mRight.brake()
  print('x_n: ', x_n,'y_n: ', y_n,'theta: ', theta)
  script.wait(600)
  

def gyro():
  brick.gyroscope().calibrate(60000)
  script.wait(61000)
  param = brick.gyroscope().getCalibrationValues()
  return param
  
#parameters = gyro()
#parameters = (259, -133, -9, -67, 123, 4069)
#print(parameters)
#brick.gyroscope().setCalibrationValues(parameters)
#script.wait(500)
tim = script.timer(200)
tim.timeout.connect(getYaw)
tim.timeout.connect(odometry)
script.wait(300)
move(150, -50)

tim.timeout.connect(getYaw)

tim.timeout.connect(odometry)

script.wait(300)

move(150, -50)
