from random import random, randint, choice
from pprint import pprint
from PIL import Image, ImageDraw, ImageFont
from copy import copy
import string


def vary_angle(angle, seed) :
	seed = 1 / abs(431 / (((seed * 997 + angle * 997) % 431) + 1))
	return angle - 0.2 + seed * 0.4


def vary_step(seed, seedB) :
	seed = 1 / abs(997 / (((seed * 991 + seedB * 223) % 997) + 1))
	return seed


def vary_bit(seed, seedB, seedC, seedD) :
	return (int(255 * seedB + 255 * seedC + 255 * seedD) >> seed) & 1


def create_bit(setup) :
	arr =  [ vary_bit(x, setup['size'], setup['dist'], setup['angle']) for x in range(setup['ring_count']) ]
	return arr


def moon_rings(dist, setup) :
	scale = setup['unit'] / 300
	offset = dist * 170
	
	add = lambda a, x: a + (offset + x / 8) * scale
	dec = lambda a, x: a - (offset + x / 8) * scale

	return [[ dec(p, x) if i < 2 else add(p, x) for i, p in enumerate(setup['planet'])] for x in range(10)]


def draw_moons(x, setup, image) :
	dist = setup['dist'] / (x + 1)
	angle = vary_angle(setup['angle'], setup['ring_count'] + x)

	moons = Image.new('RGBA', image.size, (0,0,0,0))
	add = lambda a : a + setup['rad'] / ((x + 1) * 5)
	dec = lambda a : a - setup['rad'] / ((x + 1) * 5)
	moon_setup = copy(setup)
	moon_setup['planet'] = [ dec(setup['center'][0]), dec(setup['center'][1]),\
							 add(setup['center'][0]), add(setup['center'][1]) ]
	moon_setup['diam'] = moon_setup['planet'][2] - moon_setup['planet'][0]
	moon_setup['r'] = moon_setup['diam'] / 2

	draw_planet(moon_setup, moons, setup['colors']['compl'])
	draw_shadow(moon_setup, moons, setup['colors']['compl'], setup['colors']['compl_dark'])
	moons = moons.rotate(-180 * angle)

	rec_dist = (dist * 170) * setup['unit'] / 300
	rec_dist = (-1)**(int(random() * 2) % 2) * (rec_dist + setup['rad'])
	moons = moons.transform(moons.size, Image.AFFINE, (1, 0, rec_dist, 0, 1, 0))
	
	coord_rings = moon_rings(dist, setup)
	rings = Image.new('RGBA', image.size, (0,0,0,0))
	draw = ImageDraw.Draw(rings)
	draw_ring(setup, coord_rings, draw)
	
	draw.chord(setup['planet'], -180, 0, fill=(0, 0, 0, 0))
	mask_moon = [ x - rec_dist if i % 2 == 0 else x for i, x in enumerate(moon_setup['planet'])]
	draw.chord(mask_moon, -180, 0, fill=(0, 0, 0, 0))

	moons = Image.alpha_composite(moons, rings)
	moons = moons.rotate(180 * angle)
	return Image.alpha_composite(image, moons)


def draw_ring(setup, coord_rings, draw) :
	center = setup['center'][1]

	for ring in coord_rings :
		offset = center - ring[1]
		ring[1] = center - (offset * setup['tilt'])
		ring[3] = center + (offset * setup['tilt'])
		draw.ellipse(ring, outline=tuple(setup['colors']['compl']))


def create_rings(dist, setup) :
	step = (40 * vary_step(dist, setup['ring_count'])) * (dist + 0.5) * setup['size'] / 500
	scale = setup['unit'] / 300
	offset = dist * 170

	add = lambda a, x: a + (offset + x * step) * scale
	dec = lambda a, x: a - (offset + x * step) * scale

	return [[ dec(p, x) if i < 2 else add(p, x) for i, p in enumerate(setup['planet'])] for x in range(700)]


def draw_rings(x, setup, image) :
	dist = setup['dist']  / (x + 1)

	rings = Image.new('RGBA', image.size, (0,0,0,0))
	draw = ImageDraw.Draw(rings)

	coord_rings = create_rings(dist, setup)
	draw_ring(setup, coord_rings, draw)

	angle = vary_angle(setup['angle'], setup['ring_count'] + x)
	draw.chord(setup['planet'], -180, 0, fill=(0, 0, 0, 0))
	rings = rings.rotate(180 * angle)
	return Image.alpha_composite(image, rings)


def draw_shadow(setup, image, base, shadow) :
	draw = ImageDraw.Draw(image)

	middle_color = shadow if abs(setup['shadow']) > 0.5 else base
	dark_half = (90, 270) if setup['shadow'] < 0 else (-90, 90)
	
	shad_geom = copy(setup['planet'])
	transform = (1 - abs(0.5 - abs(setup['shadow'])) * 2) * setup['diam'] / 2
	shad_geom[0] += transform
	shad_geom[2] -= transform
	
	draw.chord(setup['planet'], *dark_half, fill=tuple(shadow))
	draw.ellipse(shad_geom, fill=tuple(middle_color))


def draw_planet(setup, image, base) :
	draw = ImageDraw.Draw(image)
	draw.ellipse(setup['planet'], fill=tuple(base))


def draw_background(setup) :
	canvas = setup['canvas']

	image = Image.new('RGBA', canvas, tuple(setup['colors']['back']))
	background = Image.new('RGBA', canvas, (0,0,0,0))
	draw = ImageDraw.Draw(background)

	stars = [[ int(p * random()) for p in canvas ] for x in range(400) ]
	scale = lambda x, r : x + r * (min(canvas) / 320)
	color = (255, 255, 255, 100)

	for x, y in stars :
		r = random()
		draw.ellipse([x, y, scale(x, r), scale(y, r)], fill=color)

	return Image.alpha_composite(image, background)


def draw_text(setup, planet, image) :
	draw = ImageDraw.Draw(image)
	font = ImageFont.truetype("font.ttf", int(setup['canvas'][1] / 40))
	name = planet_to_hex(planet)

	draw.text((setup['canvas'][0] / 20, setup['canvas'][1] * 8 / 9),"planet {}".format(name),(255,255,255),font=font)


def planet_to_hex(planet) :
	name = [ x for x in planet[0:4]]
	for x in planet[4] :
		name.append(x)
	name = ''.join([ str(hex(x)[2:]).upper() if len(str(hex(x)[2:])) == 2 else "0" + str(hex(x)[2:]).upper() for x in name ])
	return name

def hex_to_planet(hex) :
	try:
		planet = [ int(hex[2 * x:2 * x + 2], 16) for x in range(len(hex) // 2) ]
		planet[4] = (planet[4], planet[5], planet[6])
		del planet[5:]
	except :
		print("unable to convert to planet format")
		quit()
	return planet


def create_planet(setup) :
	canvas, size = setup['canvas'], setup['size']
	d = min([x * 0.08 * 5 * size for x in canvas])
	planet = [ (x - d) / 2  for x in canvas ]
	planet.append(planet[0] + d)
	planet.append(planet[1] + d)
	setup['planet'] = planet
	setup['diam'] = d
	setup['rad'] = d / 2
	setup['center'] = [ planet[0] + d / 2, planet[1] + d / 2 ]


def hilo(a, b, c):
    if c < b: b, c = c, b
    if b < a: a, b = b, a
    if c < b: b, c = c, b
    return a + c


def complement(r, g, b):
    k = hilo(r, g, b)
    return [ int(k - u / 1.2) for u in (r, g, b) ]


def colors_setup(setup) :
	color = setup['colors']['base']
	setup['colors']['back'] = [ int(x * 0.05) for x in color ]
	setup['colors']['shadow'] =  [ int(x * 0.5) for x in color ]
	setup['colors']['compl'] = [ x for x in complement(*color) ]
	setup['colors']['compl_dark'] = [ int(x * 0.5) for x in complement(*color)]
	setup['colors']['base'] = [ x for x in color ]
	for x in setup['colors'] :
		setup['colors'][x].append(255)


def create_setup(planet, view) :
	setup = {}
	setup['size'] = planet[0] / 255
	setup['ring_count'] = planet[1]
	setup['dist'] = planet[2] / 255 + 20 / 255 
	setup['angle'] = (planet[3] - 127.5) / 127.5
	setup['colors'] = { 'base' : planet[4] }
	setup['canvas'] = [ x * 4 for x in view[0] ]
	setup['tilt'] = view[2]
	setup['shadow'] = (view[1] - 127.5) / 127.5 
	setup['unit'] = min(setup['canvas'][0] * 0.08 * 5, setup['canvas'][1] * 0.08 * 5)
	return setup


def planet(planet, view, name) :
	setup = create_setup(planet, view)
	colors_setup(setup)
	create_planet(setup)
	image = draw_background(setup)
	draw_planet(setup, image, setup['colors']['base'])
	draw_shadow(setup, image, setup['colors']['base'], setup['colors']['shadow'])
	bit_array = create_bit(setup)
	for x in reversed(range(setup['ring_count'])) :
		if bit_array[x] == 1 :
			image = draw_rings(x, setup, image)
		else  :
			image = draw_moons(x, setup, image)

	draw_text(setup, planet, image)
	canvas = [ int(x / 4) for x in setup['canvas'] ]
	resized = image.resize(canvas, Image.ANTIALIAS)
	resized.save(name + ".png")


def random_planet() :
	size = randint(15, 255)
	ring_count = randint(0, 7)
	distance = 255
	angle = randint(0, 255)
	color = (randint(0, 255), randint(0, 255), randint(0, 255))
	return (size, ring_count, distance, angle, color)


def scene() :
	dimensions = (800, 1000)
	shadow = randint(0, 60)
	tilt = random() * 0.1 + 0.2
	return (dimensions, shadow, tilt)


my_planet = random_planet()
my_scene = scene()
name = planet_to_hex(my_planet)
print(name, hex_to_planet(name))
planet(my_planet, my_scene, name)
