import os
import shutil
from tqdm import tqdm
import random

MIN = 1
MAX = 8570

my_list = [str(random.randint(MIN, MAX)) for i in range(500)]
with open("pose_random_index.txt", "w") as f:
    f.write(",".join(my_list))

