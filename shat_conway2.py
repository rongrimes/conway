#!/usr/bin/python3

from sense_hat import SenseHat
import sys
import time
import signal
import random

#---------------------------------------------------------

msleep = lambda x: time.sleep(x / 1000.0)

con_x, con_y   = 12, 12          # Dimensions to full conway matrix
disp_x, disp_y = 8, 8          # Dimensions to display matrix:  max 8x8 for Pi Sense Hat
pi_disp_x, pi_disp_y = 8, 8    # For Pi Sense Hat, must be 8 x 8
offs_x, offs_y = 2, 2          # Pi Sense Hat to show displ offset from full conway matrix
                               # For 0x0, top left of disp matrix is top left of conway matrix
INIT_FILL_PROBABILITY = 4      # Probability for a cell filled in itinital load of the matrix.
                               # Value is int, in range (0,10)
#---------------------------------------------------------

def signal_handler(signal, frame):
    print("Keyboard/kill Interrupt. Iteration count:", iterations, "\n")
    clear_disp([0,0,0])
    sys.exit(0)

def clear_disp(rgb):
    sense.clear(rgb)

#---------------------------------------------------------
def next_colour(rgb):
    r, g, b = rgb   # unpack the rgb list

    if (r == 255 and g < 255 and b == 0):
        g += 1

    if (g == 255 and r > 0 and b == 0):
        r -= 1

    if (g == 255 and b < 255 and r == 0):
        b += 1

    if (b == 255 and g > 0 and r == 0):
        g -= 1

    if (b == 255 and r < 255 and g == 0):
        r += 1

    if (r == 255 and b > 0 and g == 0):
        b -= 1
    return [r, g, b]

#---------------------------------------------------------
def init_matrix():
    matrix = [None] * con_x
    for i in range(0, con_x):
        matrix[i] = [None] * con_y
        for j in range(0, con_y):
            matrix[i][j] = random.randrange(10) < INIT_FILL_PROBABILITY
    return matrix

def init_false_matrix():
    matrix = [None] * con_x
    for i in range(0, con_x):
        matrix[i] = [False] * con_y
    return matrix

def con_calc(matrix, me, indexes):
#   print(me, indexes)
    count = 0
    for i,j in indexes:
        if matrix[i][j]:
            count += 1

# Conway rules    
#   Any live cell with fewer than two live neighbours dies, as if caused by underpopulation.
#   Any live cell with two or three live neighbours lives on to the next generation.
#   Any live cell with more than three live neighbours dies, as if by overpopulation.
#   Any dead cell with exactly three live neighbours becomes a live cell, as if by reproduction.

    i, j = me
    if matrix[i][j]:                 # Me, a live cell
        return count == 2 or count == 3
    else:                            # Me, a dead cell
        return count == 3


def filter(indexes, max_x, max_y):
    index2 = []
    for ind in indexes:
        i, j = ind
        if i < 0 or j < 0 or i >= max_x or j >= max_y:
            continue    
        index2.append(ind)
    return index2

def conway(matrix1):
    matrix2 = [None] * con_x    # Initialize output matrix
    for i in range(0, con_x):
        matrix2[i] = [None] * con_y

    for i in range(0, con_x):
        for j in range(0, con_y):
        # Above   
            indexes = [(i-1, j-1), (i-1,j), (i-1, j+1)]
        # Adjacent
            indexes.extend([(i, j-1), (i,j+1)])
        # Below
            indexes.extend([(i+1, j-1), (i+1,j), (i+1, j+1)])

            indexes = filter(indexes, con_x, con_y)          # discard entries that don't work
            matrix2[i][j] = con_calc(matrix1, (i,j), indexes)

    return matrix2

def show_matrix(matrix, rgb):
    DARK = [0, 0, 0]

    disp_matrix = [DARK] * (pi_disp_x * pi_disp_y)   # disp matrix is 1-dimensional and for Pi Sense Hat mut be 8x8

    for i in range(0, disp_x):
        for j in range(0, disp_y):
            if matrix[offs_x+i][offs_y+j]:
                disp_matrix[i*pi_disp_x + j] = rgb

    sense.set_pixels(disp_matrix)
    msleep(500)
    return next_colour(rgb)

def store_matrix(matrix):
    global mh_index
    global matrix_history

    max_mhi = 50                 # max matrix history index
    try:                         # initialize mhi in firts iteration
        x = mh_index
    except NameError:
        mh_index = 0
  
    if len(matrix_history) < max_mhi:
        matrix_history.append(matrix)
    else:
        matrix_history[mh_index] = matrix

    mh_index = (mh_index+1) % max_mhi

def matrix_repeat(matrix):
    global matrix_history

    for i in range(0, len(matrix_history)):
        if matrix == matrix_history[i]:
            return True
    return False

#---------------------------------------------------------

signal.signal(signal.SIGTERM, signal_handler)       # kill in background mode

sense = SenseHat()

rgb = [255, 0, 0]
iterations_hw_mark = 0         # iterations high water mark
false_matrix = init_false_matrix()

try:
    while True:
    # Create initial matrix
        matrix = init_matrix()
        rgb = show_matrix(matrix, rgb)
        iterations = 1
        print(" ", iterations, " (max: ", iterations_hw_mark, ")", end="\r", sep="")
        repeat_count = 0

        matrix_history = []
        mh_index = 0

        while True:
            store_matrix(matrix)
            matrix2 = conway(matrix)
            rgb = show_matrix(matrix2, rgb)

            if matrix2 == false_matrix:
                S = "Empty grid. "
                break
            if matrix == matrix2:
                S = "Steady grid."
                break
            if matrix_repeat(matrix2):
                repeat_count += 1
            else:
                iterations += 1
                print(" ", iterations, " (max: ", iterations_hw_mark, ")", end="\r", sep="")
            if repeat_count >= 5:
                S = "Repeating grid."
                break
            matrix = matrix2
            
        print(S, "Iteration count:", iterations, "\n")
        clear_disp([255,0,0])
        msleep(500)
        sense.show_message("I=" + str(iterations), text_colour = (255,0,0))
        iterations_hw_mark = max(iterations, iterations_hw_mark)

        clear_disp([255,0,0])
        msleep(500)
        clear_disp([0,0,0])
        msleep(500)

    clear_disp([0,0,0])

except KeyboardInterrupt:
    print("\nKeyboard/kill Interrupt. Iteration count:", iterations, "\n")
    clear_disp([255,0,0])
    msleep(500)
    sense.show_message("I=" + str(iterations), text_colour = (255,0,0))
    clear_disp([0,0,0])

