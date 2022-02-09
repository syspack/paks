__author__ = "Vanessa Sochat, Alec Scott"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat and Alec Scott"
__license__ = "Apache-2.0"

from random import choice


class RobotNamer:

    _descriptors = [
        "chunky",
        "buttery",
        "delicious",
        "scruptious",
        "dinosaur",
        "boopy",
        "lovely",
        "carniverous",
        "hanky",
        "loopy",
        "doopy",
        "astute",
        "gloopy",
        "outstanding",
        "stinky",
        "conspicuous",
        "fugly",
        "frigid",
        "angry",
        "adorable",
        "sticky",
        "moolicious",
        "cowy",
        "spicy",
        "grated",
        "crusty",
        "stanky",
        "blank",
        "bumfuzzled",
        "fuzzy",
        "hairy",
        "peachy",
        "tart",
        "creamy",
        "arid",
        "strawberry",
        "butterscotch",
        "wobbly",
        "persnickety",
        "nerdy",
        "dirty",
        "placid",
        "bloated",
        "swampy",
        "pusheena",
        "hello",
        "goodbye",
        "milky",
        "purple",
        "rainbow",
        "bricky",
        "muffled",
        "anxious",
        "misunderstood",
        "eccentric",
        "quirky",
        "lovable",
        "reclusive",
        "faux",
        "evasive",
        "confused",
        "crunchy",
        "expensive",
        "ornery",
        "fat",
        "phat",
        "joyous",
        "expressive",
        "psycho",
        "chocolate",
        "salted",
        "gassy",
        "red",
        "blue",
        "nostalgic",
        "unfortunate",
        "misty",
        "cheeky",
        "mysterious",
        "crawly",
        "creepy",
        "complex",
        "considerate",
        "medicated",
        "solemn",
        "hairless",
        "ducky",
        "zippy",
        "naked",
        "impressive",
        "wild",
        "stubborn",
        "rebellious",
        "relentless",
        "demanding",
        "fierce",
        "brave",
        "bearded",
        "boorish",
        "fastidious",
        "baleful",
        "guileless",
        "turgid",
        "zealous",
        "oniony",
        "adios",
        "aloha",
        "que-paso",
        "bitter",
        "faithful",
        "breezy",
        "magnificent",
        "striped",
        "sour",
        "whispering",
        "rugged",
        "hangry",
        "grassy",
    ]

    _nouns = [
        "squidward",
        "hippo",
        "butter",
        "animal",
        "peas",
        "lettuce",
        "carrot",
        "onion",
        "peanut",
        "cupcake",
        "muffin",
        "buttface",
        "leopard",
        "parrot",
        "parsnip",
        "poodle",
        "itch",
        "punk",
        "kerfuffle",
        "soup",
        "noodle",
        "avocado",
        "peanut-butter",
        "latke",
        "milkshake",
        "banana",
        "lizard",
        "lemur",
        "lentil",
        "bits",
        "house",
        "leader",
        "toaster",
        "signal",
        "pancake",
        "kitty",
        "cat",
        "cattywampus",
        "poo",
        "malarkey",
        "general",
        "rabbit",
        "chair",
        "staircase",
        "underoos",
        "snack",
        "lamp",
        "eagle",
        "hobbit",
        "diablo",
        "earthworm",
        "pot",
        "plant",
        "leg",
        "arm",
        "bike",
        "citrus",
        "dog",
        "puppy",
        "blackbean",
        "ricecake",
        "gato",
        "nalgas",
        "lemon",
        "caramel",
        "fudge",
        "cherry",
        "sundae",
        "truffle",
        "cinnamonbun",
        "pastry",
        "egg",
        "omelette",
        "fork",
        "knife",
        "spoon",
        "salad",
        "train",
        "car",
        "motorcycle",
        "bicycle",
        "platanos",
        "mango",
        "taco",
        "pedo",
        "nunchucks",
        "destiny",
        "hope",
        "despacito",
        "frito",
        "chip",
        "poopies",
        "chimichangas",
        "tacos",
        "naglas",
        "despacito",
        "jelly",
        "chestnut",
        "broom",
        "swampman",
        "leezard",
        "monkey",
        "giraffe",
        "starfish",
        "fish",
        "iguana",
        "snakey",
        "snakey",
        "cookie",
        "salmon",
        "erudite",
        "dragon",
        "koala",
        "flamingo",
        "toaster",
        "queso",
        "soup",
        "strudel",
        "cake",
        "burrito",
        "manbun",
        "wagon",
        "socks",
    ]

    def _generate(self, delim="-", length=4, chars="0123456789"):
        """Setup for generation of a name or badge.
                 Inspiration from Haikunator, but much more
                 poorly implemented ;)

        Parameters
        ==========
        delim: Delimiter
        length: TokenLength
        chars: TokenChars
        """

        self.descriptor = self._select(self._descriptors)
        self.noun = self._select(self._nouns)
        self.numbers = "".join((self._select(chars) for _ in range(length)))

    def generate(self, delim="-", length=4, chars="0123456789"):
        """
        Generate a robot name. Inspiration from Haikunator, but much more
                 poorly implemented ;)

        """
        self._generate(delim, length, chars)
        return delim.join([self.descriptor, self.noun, self.numbers])

    def generate_badge(self, length=4, chars="0123456789", link=None):
        """
        Generate a robot name badge (in markdown).
        """
        from openbases.main.badges import Badge
        from openbases.main.defaults import BADGE_COLORS

        # Default link, if not defined, send used to badge generator
        default_link = "https://openbases.github.io/openbases-python"
        if link is None:
            link = "%s/html/usage.html#badges" % default_link
        self._generate(length=length, chars=chars)
        color = self._select(BADGE_COLORS)
        badge = Badge(
            color=color,
            label=self.descriptor,
            name="%s-%s" % (self.noun, self.numbers),
            link=link,
        )
        return badge.get_markdown()

    def _select(self, select_from):
        """select an element from a list using random.choice

        Parameters
        ==========
        should be a list of things to select from
        """
        if len(select_from) <= 0:
            return ""

        return choice(select_from)


namer = RobotNamer()
