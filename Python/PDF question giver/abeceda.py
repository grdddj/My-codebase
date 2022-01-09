import random

alphabet = """
Alpha
Bravo
Charlie
Delta
Echo
Foxtrot
Golf
Hotel
India
Juliet
Kilo
Lima
Mike
November
Oscar
Papa
Quebec
Romeo
Sierra
Tango
Uniform
Victor
Whiskey
X-ray
Yankee
Zulu
""".strip()

words = alphabet.split("\n")
while True:
    word = random.choice(words)
    print(f"The letter is... {word[0]}")
    input("Enter...")
    print(f"                 {word}")
