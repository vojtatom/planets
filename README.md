# Planet Dreamer

Python script to generate colorful planets, runs on twitter - [@planetdreamer](https://twitter.com/planetdreamer)

## Getting Started

You will need to install two python packages - Tweepy and Pillow, there is also a simple test prepared for you to check correct instalation of Pillow.

### Prerequisites

Requires Pillow for drawing with planet.py and Tweepy for communication with bot.py. The script was tested with python 3.5 and higher.

```
pip install pillow
pip install tweepy
```

### Running tests

Be sure to test correct instalation of pillow with the following command, tweepy has no test packages here.

```
python generate_logo.py
```

## Planet names explained

Let's say we have a planet name 0xC405FF0CCC231E. It is a seven byte number, that is 56 bits in total which determine the size, number of orbits, scale, base for generating inidividual orbits and color. Broken down:

```
0xC4 - planet size
0x05 - number of orbits
0xFF - distance - size ratio
0x0C - base for generating inidividual orbits
0xCC 0x23 0x1E - RGB colors of the planet
```

The other color used in the picture is the additive color of the specified base RGB value. 


## License and Contact

This project is licensed under the GNU General Public License v3.0.
Contact me here, on twitter (@vojtatom) or on my mail tomas (at) vojtatom.cz. Happy coding!
