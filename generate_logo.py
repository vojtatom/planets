import planet
import secrets

def create_image() :
    print(">>   creating planet values")
    my_planet = planet.hex_to_planet(secrets.token_hex(7))
    print("++   planet", my_planet)
    print(">>   creating scene")
    my_scene = ((1500, 500), 235, 0.2784557339318898)
    print("++   scene", my_scene)
    print(">>   generating name")
    name = planet.planet_to_hex(my_planet)
    print(">>   creating planet image")
    planet.planet(my_planet, my_scene, name)
    print("++   planet", name, "created")
    return name + ".png"


create_image()
