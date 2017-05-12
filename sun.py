from random import random, randint
from PIL import Image, ImageDraw, ImageFont
import perlin

def draw_background(setup) :
	canvas = setup['canvas']

	image = Image.new('RGBA', canvas, tuple(setup['color']['back']))
	background = Image.new('RGBA', canvas, (0,0,0,0))
	draw = ImageDraw.Draw(background)

	stars = [[ int(p * random()) for p in canvas ] for x in range(400) ]
	scale = lambda x, r : x + r * (min(canvas) / 320)
	color = (255, 255, 255, 100)

	for x, y in stars :
		r = random()
		draw.ellipse([x, y, scale(x, r), scale(y, r)], fill=color)

	return Image.alpha_composite(image, background)

def apply_noise(image, setup) :
	generator = perlin.Perlin()
	octaves = 5
	persistence = 5
	coef = 30
	width, height = setup['canvas'][0], setup['canvas'][1]

	list_of_pixels = list(image.getdata())
	for i, pixel in enumerate(list_of_pixels) :
		if pixel != (0, 0, 0, 0) :
			noise = generator.OctavePerlin((i % width) / coef, i / (height * coef), 0, 1, 5)
			new_pixel = [ int(x * (1 + noise)) for x in pixel[:3] ]
			new_pixel.append(pixel[3])
			list_of_pixels[i] = tuple(new_pixel)

	image = Image.new(image.mode, image.size)
	image.putdata(list_of_pixels)
	return image


def apply_ray_effect(sun_image, setup) :
	canvas = setup['canvas']
	width, height = setup['canvas'][0], setup['canvas'][1]
	decay = 0.8
	density = 1.2
	samples = 128
	center = [ x / 2 for x in setup['canvas'] ]

	list_of_pixels = list(sun_image.getdata())

	new_image = []
	print("starting postprocessing...")
	for y in range(height) :
		print("\rjob completed {0:.2f}%".format(round(100 * (y / height), 2)), flush=True, end="")
		for x in range(width) :
			tc = [x, y]
			delta = [ (x - center[0]) / (samples * density), (y - center[1]) / (samples * density) ]
			color = list_of_pixels[x + y * width]
			illumination = 1
			for m in range(samples) :
				tc = [ tc[0] - delta[0], tc[1] - delta[1]]
				add_color = tuple( illumination * x for x in list_of_pixels[int(tc[0]) + int(tc[1]) * width] )
				illumination *= decay		
				color = tuple( x + y for x, y in zip(color, add_color))


			new_image.append(tuple(int(x) for x in color))


	image = Image.new(sun_image.mode, sun_image.size)
	image.putdata(new_image)
	return image


def draw_sun(image, setup) :
	canvas = setup['canvas']
	sun_image = Image.new('RGBA', canvas, (0,0,0,0))
	draw = ImageDraw.Draw(sun_image)
	draw.ellipse(setup['sun'], fill=tuple(setup['color']['base']))
	
	sun_image = apply_noise(sun_image, setup)
	sun_image = apply_ray_effect(sun_image, setup)
	
	return Image.alpha_composite(image, sun_image)

def create_sun(setup) :
	canvas, size = setup['canvas'], setup['size']
	d = min([x * 0.08 * 5 * size for x in canvas])
	planet = [ (x - d) / 2  for x in canvas ]
	planet.append(planet[0] + d)
	planet.append(planet[1] + d)
	setup['sun'] = planet
	setup['diam'] = d
	setup['rad'] = d / 2
	setup['center'] = [ planet[0] + d / 2, planet[1] + d / 2 ]

def sun_setup(setup) :
	tmp_setup = {}
	tmp_setup['color'] = {}
	tmp_setup['color']['base'] = setup[2]
	tmp_setup['color']['back'] = [ int(x * 0.05) for x in setup[2] ]
	tmp_setup['canvas'] =  [ x * 2 for x in setup[0] ]
	tmp_setup['size'] = setup[1] / (255 * 2)
	return tmp_setup

def sun(setup) :
	setup = sun_setup(setup)
	create_sun(setup)
	image = draw_background(setup)
	image = draw_sun(image, setup)

	canvas = [ int(x / 2) for x in setup['canvas'] ]
	resized = image.resize(canvas, Image.ANTIALIAS)
	resized.save("test.png")


setup = ((1200, 750), 128, (180, 120, 100))
sun(setup)

