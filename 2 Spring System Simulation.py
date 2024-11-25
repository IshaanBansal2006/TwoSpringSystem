#!/usr/bin/env python
# coding: utf-8

#Ishaan Bansal
#Coded using Jupyter Notebook

import pygame
import sys
from pygame.locals import *
import numpy as np
from numpy.linalg import inv

def spring(start, end, nodes, width, lead1, lead2):
    """!
    Return a list of points corresponding to a spring.

    @param r1 (array-like) The (x, y) coordinates of the first endpoint.
    @param r2 (array-like) The (x, y) coordinates of the second endpoint.
    @param nodes (int) The number of spring "nodes" or coils.
    @param width (int or float) The diameter of the spring.
    @param lead1 (int) The starting flat piece of the spring.
    @param lead2 (int) The ending flat piece of the spring.
    @return An array of x coordinates and an array of y coordinates, and the start and end points
    """

    # Check that nodes is at least 1.
    nodes = max(int(nodes), 1)

    # Convert to numpy array to account for inputs of different types/shapes.
    start, end = np.array(start).reshape((2,)), np.array(end).reshape((2,))

    # If both points are coincident, return the x and y coords of one of them.
    if (start == end).all():
        return start[0], start[1]

    # Calculate length of spring (distance between endpoints).
    length = np.linalg.norm(np.subtract(end, start))

    # Calculate unit vectors tangent (u_t) and normal (u_t) to spring.
    u_t = np.subtract(end, start) / length
    u_n = np.array([[0, -1], [1, 0]]).dot(u_t)

    # Add some magic here
    p1 = start + lead1*u_t
    p2 = end - lead2*u_t

    length -= (lead1+lead2)

    # Initialize array of x (row 0) and y (row 1) coords of the nodes+2 points.
    spring_coords = np.zeros((2, nodes + 2))
    spring_coords[:,0], spring_coords[:,-1] = p1, p2

    # Check that length is not greater than the total length the spring
    # can extend (otherwise, math domain error will result), and compute the
    # normal distance from the centerline of the spring.
    normal_dist = math.sqrt(max(0, width**2 - (length**2 / nodes**2))) / 2

    # Compute the coordinates of each point (each node).
    for i in range(1, nodes + 1):
        spring_coords[:,i] = (
            p1
            + ((length * (2 * i - 1) * u_t) / (2 * nodes))
            + (normal_dist * (-1)**i * u_n))

    return spring_coords[0,:], spring_coords[1,:], p1, p2

def F(t):
	F = np.zeros(4)
	F[1] = F0 * np.sin(omega*t)
	return F

def G(y,t): 
	return A_inv.dot( F(t) - B.dot(y) )

def RK4_step(y, t, dt):
	k1 = G(y,t)
	k2 = G(y+0.5*k1*dt, t+0.5*dt)
	k3 = G(y+0.5*k2*dt, t+0.5*dt)
	k4 = G(y+k3*dt, t+dt)

	return dt * (k1 + 2*k2 + 2*k3 + k4) / 6

def update(point1, point2, point3):
	mass1.update(point2)
	mass2.update(point3)

	s1.update(point1, point2)
	s2.update(point2, point3)

def render():
	screen.fill(WHITE)

	render_statics()

	s1.render()
	s2.render()

	mass1.render()
	mass2.render()

def render_statics():
	# floor and wall
	pygame.draw.line(screen, BLACK, (30, point1[1]+45), (770, point1[1]+45), 10)
	pygame.draw.line(screen, BLACK, (30, point1[1]-50), (30, point1[1]+50), 10)

	pygame.draw.line(screen, GRAY, (point1[0]+offset1, point1[1]+55), (point1[0]+offset1, point1[1]+70), 3)
	pygame.draw.line(screen, GRAY, (point1[0]+offset2, point1[1]+55), (point1[0]+offset2, point1[1]+70), 3)

class Mass():
	def __init__(self, position, color, width, height):
		self.pos = position
		self.color = color
		self.w = width
		self.h = height

		self.left = self.pos[0] - self.w/2
		self.top = self.pos[1] - self.h/2

	def render(self):
		pygame.draw.rect(screen, self.color, (self.left, self.top, self.w, self.h))

	def update(self, position):
		self.pos = position
		self.left = self.pos[0] - self.w/2
		self.top = self.pos[1] - self.h/2


class Spring():
	def __init__(self, color, start, end, nodes, width, lead1, lead2):
		self.start = start
		self.end = end
		self.nodes = nodes
		self.width = width
		self.lead1 = lead1
		self.lead2 = lead2
		self.weight = 3
		self.color = color

	def update(self, start, end):
		self.start = start
		self.end = end

		self.x, self.y, self.p1, self.p2 = spring(self.start, self.end, self.nodes, self.width, self.lead1, self.lead2)
		self.p1 = (int(self.p1[0]), int(self.p1[1]))
		self.p2 = (int(self.p2[0]), int(self.p2[1]))

	def render(self):
		pygame.draw.line(screen, self.color, self.start, self.p1, self.weight)
		prev_point = self.p1
		for point in zip(self.x, self.y):
			pygame.draw.line(screen, self.color, prev_point, point, self.weight)
			prev_point = point
		pygame.draw.line(screen, self.color, self.p2, self.end, self.weight)
		

w, h = 800, 480
WHITE = (255,255,255)
BLACK = (0,0,0)
GRAY = (150, 150, 150)
RED = (255,0,0)
BLUE = (0,0,255)

screen = pygame.display.set_mode((w,h))
screen.fill(WHITE)
clock = pygame.time.Clock()

# parameters
m1, m2 = 2.0, 1.0
k1, k2 = 3.0, 2.0

delta_t = 0.1

F0 = 10.0
omega = 1.0

y = 100*np.array([0, 0, 0, 0])
dof = 2

# setup matrices
K = np.array([[k1+k2, -k2],[-k2, k2]])
M = np.array([[m1, 0],[0, m2]])
I = np.identity(dof)

A = np.zeros((2*dof,2*dof))
B = np.zeros((2*dof,2*dof))

A[0:2,0:2] = M
A[2:4,2:4] = I

B[0:2,2:4] = K
B[2:4,0:2] = -I

A_inv = inv(A)

t = 0

mass1 = Mass((150,100), RED, 120, 80)
mass2 = Mass((150,100), BLUE, 80, 80)

s1 = Spring(BLACK, (0,0), (0,0), 20, 50, 20, 70)
s2 = Spring(BLACK, (0,0), (0,0), 15, 30, 70, 50)

point1 = (35, 300)
offset1 = 300
offset2 = 550

while True:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			sys.exit()

	point2 = (point1[0] + offset1 + y[2], point1[1])
	point3 = (point1[0] + offset2 + y[3], point1[1])

	update(point1, point2, point3)
	render()

	t += delta_t
	y = y + RK4_step(y, t, delta_t) 

	clock.tick(60)
	pygame.display.update()


# In[ ]:




