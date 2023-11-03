import copy

# Implementation details:
# NOTE: this may not always provide the best solution though it does most of the time, more details below.
# I have hardcoded for 4x4 inputs. The user provides the values in the
# truth table as strings (x's are acceptable!). Then the code calculates the Karnaugh map,
# finds the largest rectangle for each vertex (ties are broken by maximising the number of 1s as opposed to Xs
# in rectangles of equal size). Rectangles of each size are found using detected rectangles of smaller size
# Once these maximal rectangles are obtained (I make the *unproven but maybe correct*
# assumption that it is sufficient to only use these rectangles). Then, to find the smallest set of spanning rectangles,
# in a loop I chose the smallest of the maximal rectangles that spans a 1 (this must be in the output as none of the
# largest rectangles can span this one as otherwise the smaller rectangle wouldn't be part of the list of maximal
# rectangles. Then I check of all the one's this rectangle covers and repeat till all the ones are checked off (the
# logic of this strategy is sound if the smallest maximal rectangle is unique, which may not be the case in practice).
# Finally, the set of rectangles are converted to their corresponding implicants.
# THIS CODE IS NOT WELL WRITTEN BY ANY STANDARDS but this is a busy semester and I need to get other stuff done.


# helpers
def wrap_index(l: list, x: int, y: int):
    return l[x % 4][y % 4]


def pretty_print(l):
    for i in l:
        print(i)


def wrap_update(l: list, x: int, y: int, value):
    l[x % 4][y % 4] = value


# find the number of 1's a given rectangle covers
def score_rectangle(pos, dim, k_map):
    score = 0
    for row in range(pos[0], pos[0] + dim[0]):
        for column in range(pos[1], pos[1] + dim[1]):
            if wrap_index(k_map, row, column) == "1":
                score += 1
    return score


# check if new_rectangle is better than old rectangle.
# Uses size to compare and breaks score with #1s covered
def compare_rectangles(new_rectangle, old_rectangle):
    return new_rectangle[0] > old_rectangle[0] \
    or \
    (new_rectangle[0] == old_rectangle[0]) and (new_rectangle[1] > old_rectangle[1])


def update_best_rectangles(new_rectangle, best_rectangles):
    pos = new_rectangle[2]
    dim = new_rectangle[3]
    for row in range(pos[0], pos[0] + dim[0]):
        for column in range(pos[1], pos[1] + dim[1]):
            cur_best_rect = wrap_index(best_rectangles, row, column)
            if compare_rectangles(new_rectangle, cur_best_rect):
                wrap_update(best_rectangles, row, column, new_rectangle)


# TAKE IN BINARY TABLE
inp = input("enter binary table (0, 1, x): ")
if len(inp) != 16:
    raise Exception("wrong input length")
inp_dict = {}
for i in range(16):
    i_bin = bin(i)[2:]
    i_4_bit = "0" * (4 - len(i_bin)) + i_bin
    inp_dict[i_4_bit] = inp[i] if inp[i] in ("0", "1") else "x"

grey_code = ["00", "01", "11", "10"]
print(inp_dict)
k_map = [[inp_dict[grey_code[j]+grey_code[i]] for j in range(4)]for i in range(4)]
max_k_map = [["1" if ele in ("1", "x") else "0" for ele in row]
            for row in k_map]
if max_k_map == [["1" for i in range(4)] for j in range(4)]:
    print(max_k_map)
    raise Exception("The whole k_map is 1s, no simplification required")
# We want to find the largest rectangle for each elements. To break ties,
# prefer rectangles that cover more 1s and less Xs. Store an array recording the
# best known rectangle for each element so far. Format:
# (size of rectangle, # 1s in rectangle, top-left corner [(x, y)], dimensions [(x, y)])
best_rectangles = [[0 for i in range(4)] for j in range(4)]
# initialize best rectangle with 1x1 squares
for row in range(4):
    for column in range(4):
        if k_map[row][column] == "1":
            best_rectangles[row][column] = (1, 1, (row, column), (1, 1))
        elif k_map[row][column] == "x":
            best_rectangles[row][column] = (1, 0, (row, column), (1, 1))
        else: # we don't care
            best_rectangles[row][column] = (0, 0, 0, 0)

# Find all 2x1 rectangles and update best_rectangles accordingly
rectangles_2_1 = [[0 for i in range(4)] for j in range(4)]
for row in range(4):
    for column in range(4):
        if max_k_map[row][column] == "1" and wrap_index(max_k_map, row + 1, column) == "1":
            rectangles_2_1[row][column] = 1
            pos = (row, column)
            dim = (2, 1)
            score = score_rectangle(pos, dim, k_map)
            rectangle = (2, score, pos, dim)
            update_best_rectangles(rectangle, best_rectangles)

# Find all 1x2 rectangles and update best_rectangles accordingly
for row in range(4):
    for column in range(4):
        if max_k_map[row][column] == "1" and wrap_index(max_k_map, row, column + 1) == "1":
            pos = (row, column)
            dim = (1, 2)
            score = score_rectangle(pos, dim, k_map)
            rectangle = (2, score, pos, dim)
            update_best_rectangles(rectangle, best_rectangles)

# Find all 1x4 rectangles and update best_rectangles accordingly
for row in range(4):
    if max_k_map[row] == ["1", "1", "1", "1"]:
        pos = (row, 0)
        dim = (1, 4)
        score = score_rectangle(pos, dim, k_map)
        rectangle = (4, score, pos, dim)
        update_best_rectangles(rectangle, best_rectangles)

# Find all 4x1 rectangle and update best_rectangles accordingly
for column in range(4):
    if [row[column] for row in max_k_map] == ["1", "1", "1", "1"]:
        pos = (0, column)
        dim = (4, 1)
        score = score_rectangle(pos, dim, k_map)
        rectangle = (4, score, pos, dim)
        update_best_rectangles(rectangle, best_rectangles)


# Find all 2x2 rectangles
rectangles_2_2 = [[0 for j in range(4)] for i in range(4)]
for row in range(4):
    for column in range(4):
        if rectangles_2_1[row][column] and wrap_index(rectangles_2_1, row, column + 1):
            rectangles_2_2[row][column] = 1
            pos = (row, column)
            dim = (2, 2)
            score = score_rectangle(pos, dim, k_map)
            rectangle = (4, score, pos, dim)
            update_best_rectangles(rectangle, best_rectangles)
# find all 2x4 rectangles
for row in range(4):
    if rectangles_2_2[row][0] and rectangles_2_2[row][2]:
        pos = (row, 0)
        dim = (2, 4)
        score = score_rectangle(pos, dim, k_map)
        rectangle = (8, score, pos, dim)
        update_best_rectangles(rectangle, best_rectangles)

# find all 4x2 rectangles
for column in range(4):
    if rectangles_2_2[0][column] and rectangles_2_2[2][column]:
        pos = (0, column)
        dim = (4, 2)
        score = score_rectangle(pos, dim, k_map)
        rectangle = (8, score, pos, dim)
        update_best_rectangles(rectangle, best_rectangles)


# We have now found the maximal rectangle for each position!
def is_k_map_empty(k_map):
    for row in k_map:
        if "1" in row:
            return False
    return True


def find_smallest_maximal_rect(k_map, best_rectangles):
    rect = (100, 100, 100, 100) #some large value
    for row in range(4):
        for column in range(4):
            if k_map[row][column] == "1":
                if not compare_rectangles(best_rectangles[row][column], rect):
                    rect = best_rectangles[row][column]
    return rect


def update_k_map(k_map, rectangle):
    new_k_map = copy.deepcopy(k_map)
    pos = rectangle[2]
    dim = rectangle[3]
    for row in range(pos[0], pos[0] + dim[0]):
        for column in range(pos[1], pos[1] + dim[1]):
            wrap_update(new_k_map, row, column, 0)
    return new_k_map


# to get a minimal spanning set of rectangles, do the following in a loop:
# 1 - find the minimal max rectangle - add this to our set
# 2 - remove all the one's covered by this rectangle in the k_map
# 3 - stop if k_map is empty, else loop
spanning_set = []
print("the provided k_map is: ")
pretty_print(k_map)
while not is_k_map_empty(k_map):
    smallest_max_rect = find_smallest_maximal_rect(k_map, best_rectangles)
    spanning_set.append(smallest_max_rect)
    k_map = update_k_map(k_map, smallest_max_rect)


#print("the best rectangles for every vertex are: ", best_rectangles)
print("a (possibly) minimal spanning set of rectangles is: ", spanning_set)

# The last step is to find the minterms for each rectangle
# Assume the variables are A, B, C, D in that order
grey_code = [(-1, -1), (-1, 1), (1, 1), (1, -1)]
minterms = []
for rectangle in spanning_set:
    minterm = ""
    pos = rectangle[2]
    dim = rectangle[3]
    A = 0
    B = 0
    C = 0
    D = 0
    for column in range(pos[1], pos[1] + dim[1]):
         A += grey_code[column % 4][0]
         B += grey_code[column % 4][1]

    for row in range(pos[0], pos[0] + dim[0]):
         C += grey_code[row % 4][0]
         D += grey_code[row % 4][1]
    d = ((A, "A"),  (B, "B"), (C, "C"), (D, "D"))
    for X in d:
        if X[0] == 0:
            pass
        elif X[0] > 0:
            minterm += X[1]
        else:
            minterm += X[1] + "'"
    minterms.append(minterm)
print("the optimal boolean expression (probably) is: ")
print(" + ".join(minterms))












