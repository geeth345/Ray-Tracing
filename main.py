import numpy as np
import matplotlib.pyplot as plt

# render parameters
####################

# resolution
width = 300
height = 200

# camera position
camera = np.array([3.8, -1.6, 0])

# camera facing direction
xRotation = 0
yRotation = 0
zRotation = 55

# field of view
fov = 90 


# scene
###################

# objects in scene
objects = [
	{ 'centre': np.array([6, 0.1, -0.2]), 'radius': 0.4, 'colour': np.array([0, 0, 1]) },
	{ 'centre': np.array([5, -0.35, 0.2]), 'radius': 0.2, 'colour': np.array([1, 0, 0]) },
	{ 'centre': np.array([5, 1, 0]), 'radius': 0.8, 'colour': np.array([0, 1, 0]) }
]

# scene lighting
lighting = {'position': np.array([5, -5, 2])}


####################





def generateTransformationMatrix(xRotation, yRotation, zRotation):
	z = np.radians(zRotation)
	y = np.radians(yRotation)
	x = np.radians(xRotation)
	zMatrix = np.array([
		[np.cos(z),-np.sin(z), 0],
		[np.sin(z), np.cos(z), 0],
		[0        , 0        , 1]
	])
	yMatrix = np.array([
		[np.cos(y) , 0, np.sin(y)],
		[0         , 1, 0        ],
		[-np.sin(y), 0, np.cos(y)]
	])
	xMatrix = np.array([
		[1, 0        , 0        ],
		[0, np.cos(x),-np.sin(x)],
		[0, np.sin(x), np.cos(x)]
	])
	sumRotationMatrix = (zMatrix @ yMatrix) @ xMatrix
	return sumRotationMatrix


def normalise(vector):
	return vector / np.linalg.norm(vector)

def sphereIntersect(centre, radius, start, direction):
	x = start - centre
	a = np.dot(direction,direction)
	b = 2 * np.dot(x, direction)
	c = np.dot(x, x) - radius**2
	disc = b**2 - (4*a*c)
	if disc > 0:
		t1 = (-b + np.sqrt(disc)) / 2
		t2 = (-b - np.sqrt(disc)) / 2
		if t1>0 and t2>0:
			return min(t1, t2)
	return None

def nearestObject(objects, origin, direction):
	distances = [sphereIntersect(obj['centre'], obj['radius'], origin, direction) for obj in objects]
	nearest = None
	minDist = np.inf
	for i, dist in enumerate(distances):
		if dist and dist < minDist:
			minDist = dist
			nearest = objects[i]
	return nearest, minDist

def illumination(object, distance, origin, direction, light):
	#checking if point is shadowed
	intersection = origin + (distance * direction)
	intersection = intersection + (1e-5 * (normalise(intersection - object['centre'])))
	incedentRay = light['position'] - intersection
	a, b = nearestObject(objects, intersection, normalise(incedentRay))
	magnitudeIncedentRay = np.linalg.norm(incedentRay)
	shadowed = b < magnitudeIncedentRay
	if not shadowed: 
		return object['colour']
	else: return object['colour'] * 0.25


ratio = float(width)/height 
screen = (1 , (1/ratio), -1, -(1/ratio)) # left,top,right,bottom

def compute():
	image = np.zeros((height, width, 3))
	rotation = generateTransformationMatrix(xRotation, yRotation, zRotation)
	separation = (np.tan(np.radians(fov/2)))**-1
	for i, z in enumerate(np.linspace(screen[1], screen[3], height)):
		for j, y in enumerate(np.linspace(screen[0], screen[2], width)):
			direction = normalise(rotation @ np.array([separation, y, z]))
			origin = camera
			nearest, distance = nearestObject(objects, origin, direction)
			if nearest != None:
				image[i, j] = illumination(nearest, distance, origin, direction, lighting)
		print("Progress: %d/%d" % (i+1, height))       
	return(image)


filename = input("Enter Filename: ")
plt.imsave(filename + ".png", compute())
print("Render Complete")
