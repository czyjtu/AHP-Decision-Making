from itertools import combinations
from string import ascii_letters 



names = list(ascii_letters[:4])
scores = range(6)
print(list(zip(list(combinations(names ,2)), scores)))