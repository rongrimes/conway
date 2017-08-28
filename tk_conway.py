#!/usr/bin/python3
# Job Jar
# 1. Add control buttons

#from tkinter import *
from tkinter import *
import random
import sys
import signal
#import time

FASTMATRIXLOAD = False
#FASTMATRIXLOAD = True

# Conway matrix display
con_x, con_y   = 40, 20        # Dimensions to full conway matrix
disp_x, disp_y = 40, 20        # Dimensions to display matrix (<= con_x, con_y)
new_w, new_h = con_x, con_y

# Config window display
config_w, config_h   = 240, 190        # Dimensions to configuration window

# Windows/TK display
sq_size = 20     # square size in grid
oval_offset= 4   # offset of oval in grid (size = sq_size)

#offset_x = 15    # offset of grid in frame from top left corner
offset_x = 1    # offset of grid in frame from top left corner
#offset_y = 15
#offset_y = 2
offset_y = 1

INIT_FILL_PROBABILITY = 3      # Probability for a cell filled in initial load of the matrix.
                               # Value is int, in range [0,10]
TitleWidth = 340               # Min width to hold program title.

#--------------------------------------------------------------------------------------------------
class App:
   def __init__(self, master, conway):
      self.rgb = [255, 0, 0]
      self.cycle_count = 0
      self.screen_size()

# Frames------------
#     status - to show counts
      Button(master, text = "Config", command=self.st_config, font = "Verdana 10", 
           height=1, width=10).grid(row=0, column=0, padx=10, sticky="W")

      self.iter_count = StringVar()
#     self.it_count = Label(master,
      Label(master, textvariable=self.iter_count, fg = "black",
                 font = "Verdana 10").grid(row=0, column=1, ipady=7, sticky="W")

#     Main canvas for Conway grid
      self.canvas_size()

#     controls - for single step/restart

      seq_buts = Frame(master)
      seq_buts.grid(row=2, column=0, columnspan=2)

      bRestart = Button(seq_buts, text = "Restart", command=self.restart, font = "Verdana 10", 
           height=1, width=8)
      bRestart.grid(row=0, column=0, padx=5)

      bSingle = Button(seq_buts, text = "Single Step", command=self.single_step, font = "Verdana 10",
           height=1, width=8)
      bSingle.grid(row=0, column=1, padx=5)

      self.bCont = Button(seq_buts, text = "Continue", command=self.normal_progress, font = "Verdana 10",
           height=1, width=8)
      self.bCont.grid(row=0, column=2, padx=5)
      self.bCont.config(state = DISABLED)

      self.init_states()

      self.process()

   def init_states(self):
      self.states = { "initialize": "initialize", "init_by_cols": "init_by_cols",
                      "process": "process", "single-step":"single-step",
                      "transition1": "transition1", "transition2": "transition2",
                      "transition3": "transition3", "transition4": "transition4"
                    }
      self.state = self.states["initialize"]

   def st_config(self):
      conf = Config()
#--------------------------------------------------------------- 

   def change_screen_size(self):
      global new_w, new_h
      global con_x, con_y
      global disp_x, disp_y

      result = False
      if new_w != con_x:
          con_x = disp_x = new_w
          result = True

      if new_h != con_y:
          con_y = disp_y = new_h
          result = True

      return result
  
   def screen_size(self):
      self.min_width = max(disp_x * sq_size + 2*offset_x,    # width of matrix
                      TitleWidth)                            # space to fit title
      my_w, my_h = self.min_width+20, disp_y * sq_size + 2*offset_y+60+20
#     master.geometry(str(my_w) + "x" + str(my_h) + "+20+20") 

   def canvas_size(self):
#     Main canvas for Conway grid
      f = Frame(master,
                 width=self.min_width+2,
                 height=disp_y * sq_size + 2)
      f.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

      self.w = Canvas(f, width=self.min_width+1, height=disp_y * sq_size + 1)

   def process(self):
      pause = 500 # milliseconds, default
      if self.state == "initialize":
         self.initial_all()
         if FASTMATRIXLOAD:
            self.initial_fast()
            self.state = self.states["process"]
         else:
            self.state = self.states["init_by_cols"]
            pause = self.initial_by_cols()   # returns 1 (short), or 1000 at end of generation
                                             # actually... here it should always return "1"
         self.checkered(conway.matrix, new_rgb=False )
      elif self.state == "init_by_cols":
         pause = self.initial_by_cols()      # returns 1 (short), or 1000 at end of generation
         self.checkered(conway.matrix, new_rgb=False )
      elif self.state == "process" or self.state == "single-step":
         result = conway.iterate()
         self.checkered(conway.matrix, new_rgb=True)

         if result[0]:       # We have reached the end of the cycle
            conway.iterations_hw_mark = max(conway.iterations, conway.iterations_hw_mark)
            close_reason = result[1]
            print("Iteration count:", conway.iterations, close_reason, "\n")
            self.state = self.states["transition1"]
         elif self.state == "single-step":
            pause=0 
      elif self.state == "transition1":
         pause=500
         self.state = self.states["transition2"]
         self.checkered(conway.false_matrix, new_rgb=True)
      elif self.state == "transition2":
         pause=500
         self.state = self.states["transition3"]
         self.checkered(conway.true_matrix, new_rgb=True)
      elif self.state == "transition3":
         pause=500
         self.state = self.states["initialize"]
         self.checkered(conway.false_matrix, new_rgb=True)
      # And arm for the next cycle
      if pause > 0:
         master.after(pause, self.process)

   def initial_all(self):
      if self.change_screen_size():
         self.screen_size()
         self.w.delete("all")
         self.canvas_size()
         conway.initialize_matrixes()
      else:
         conway.clear_matrix()

      self.bCont.config(state = DISABLED)
      self.cycle_count +=1

      conway.initialize_vars()

   def initial_fast(self):
      self.state = self.states["process"]
      conway.init_matrix()

   def initial_by_cols(self):
      conway.init_column(conway.init_column_number)
      conway.init_column_number += 1

      if conway.init_column_number >= con_x:
         self.state = self.states["process"]
         return 1000        # pause value: wait a bit to start so we can view the start matrix.
      else:
         return 1           # pause value: minimum wait to generate next column

   def show_my_status(self):
      my_status = "Cycles: " + str(self.cycle_count) + " Iterations: " + str(conway.iterations) \
                             + " Cell count: " + str(conway.cell_count) \
                             + " (max:" + str(conway.iterations_hw_mark) + ")"
      self.iter_count.set(my_status)    # Show result on screen

   def restart(self):
      self.bCont.config(state=DISABLED)
      start_process = self.state == self.states["single-step"]
      self.state = self.states["transition1"]
      if start_process:
         self.process()

   def single_step(self):
#     On first press, just stop the cycle; After that, single step.
      start_process = self.state == self.states["single-step"]
      self.state = self.states["single-step"]
      if start_process:   # if it was already single-step, then need to rerun process.
         self.process()
      else:
         self.bCont.config(state=NORMAL)   # if new entry to single state, enable the Continue button

   def normal_progress(self):
      self.state = self.states["process"]
      self.bCont.config(state=DISABLED)
      self.process()    # and do another cycle

   def checkered(self, matrix, new_rgb=True):
      self.w.delete("all")
      width = self.min_width
      
      length = disp_x * sq_size 
      height = disp_y * sq_size
      offset_x = (width - length) // 2     # Calculate new offset to centre in the frame.

      if new_rgb:
         self.rgb = next_colour(self.rgb)
      fill = "#" + "%0.2x" % self.rgb[0] + "%0.2x" % self.rgb[1] + "%0.2x" % self.rgb[2]

      self.show_my_status()

      # vertical lines at an interval of "line_distance" pixel
      for x in range(0, disp_x+1):
         start_x = offset_x + x*sq_size
         self.w.create_line(start_x, offset_y, start_x, offset_y+height)

      # horizontal lines at an interval of "line_distance" pixel
      for y in range(0, disp_y+1):
         start_y=offset_y + y*sq_size
         self.w.create_line(offset_x, start_y, offset_x+length, start_y)

      ovalsize = sq_size - 2 * oval_offset
      for x in range(0, disp_x):
         for y in range(0, disp_y):
            if matrix[x][y]:
               start_x = offset_x + x*sq_size + oval_offset
               start_y = offset_y + y*sq_size + oval_offset
               self.w.create_oval(start_x, start_y, start_x+ovalsize, start_y+ovalsize, fill=fill)
      self.w.pack()

#--------------------------------------------------------------------------------------------------
class Config:
   def __init__(self):
      self.conf_window = Toplevel()
      self.conf_window.title("Configure")
      self.conf_window.geometry(str(config_w)+"x"+str(config_h)+"+60+60") 

      self.build_control_frame()

      Button(self.conf_window, text = "Cancel", command=self.conf_window.destroy, font = "Verdana 10", 
           height=1, width=10).grid(row=1, column=0, padx=5)
      Button(self.conf_window, text = "Save", command=self.save_config, font = "Verdana 10", 
           height=1, width=10).grid(row=1, column=1, padx=5)

   def build_control_frame(self):
      global new_w, new_h

      config_f = Frame(self.conf_window,
                 width=200,
                 height=100, bd=2, relief=RAISED)
      config_f.grid(row=0, column=0, columnspan=2, pady=10)

      self.new_width  = Config_but(config_f, myrow=0, label="Width: ", init_val=con_x, limits=None)
      self.new_height = Config_but(config_f, myrow=1, label="Height:", init_val=con_y, limits=None)
      self.new_initp  = Config_but(config_f, myrow=2, label="Init. cell prob.:",
                              init_val=INIT_FILL_PROBABILITY, limits=(1,9))

   def save_config(self):
      global INIT_FILL_PROBABILITY
      global new_w, new_h

      new_w = self.new_width.buttvalue
      new_h = self.new_height.buttvalue

      INIT_FILL_PROBABILITY = self.new_initp.buttvalue

      self.conf_window.destroy()


#--------------------------------------------------------------------------------------------------
class Config_but:
   def __init__(self, config_f, myrow, label, init_val, limits):
      self.label = label
      self.limits = limits
      self.display_val = StringVar()
      Label(config_f,
                 textvariable=self.display_val,
                 fg = "black",
                 font = "Verdana 10").grid(row=myrow, column=0, padx=5, pady=5, sticky="W")
      self.buttvalue = init_val
      self.display_val.set(self.label + str(self.buttvalue))

      Button(config_f, text = "<", command=self.dec, font = "Verdana 10", 
           height=1, width=2).grid(row=myrow, column=1, pady = 5)
      Button(config_f, text = ">", command=self.inc, font = "Verdana 10", 
           height=1, width=2).grid(row=myrow, column=2, pady = 5)

   def dec (self):
      if self.limits is None or self.buttvalue > self.limits[0]:
         self.buttvalue -= 1
      self.display_val.set(self.label + str(self.buttvalue))

   def inc (self):
      if self.limits is None or self.buttvalue < self.limits[1]:
         self.buttvalue += 1
      self.display_val.set(self.label + str(self.buttvalue))


#--------------------------------------------------------------------------------------------------
class Conway:
   def __init__(self):
      self.iterations_hw_mark = 0         # iterations high water mark
      self.initialize_matrixes()
      self.initialize_vars()
      
   def initialize_vars(self):
      self.repeat_count = 0
      self.mh_index = 0
      self.matrix_history = []
      self.iterations = 0
      self.init_column_number = 0
      self.cell_count = 0

   def initialize_matrixes(self):
      self.matrix       = self.set_matrix(False)
      self.false_matrix = self.set_matrix(False)
      self.true_matrix  = self.set_matrix(True)

   def set_matrix(self, Bool):
       matrix = [None] * con_x
       for i in range(0, con_x):
           matrix[i] = [Bool] * con_y
       return matrix

   def clear_matrix(self):
      for i in range(0, con_x):
         for j in range(0, con_y):
            self.matrix[i][j] = False

   def init_matrix(self):
      for col in range(0, con_x):
         self.init_column(col)

   def init_column(self, col):
      for j in range(0, con_y):
         self.matrix[col][j] = random.randrange(10) < INIT_FILL_PROBABILITY
         if self.matrix[col][j]:
             self.cell_count += 1

   def iterate(self):
      self.store_matrix()
      matrix2 = self.conway()

      if matrix2 == self.false_matrix:
         return True, "Empty grid."
      if matrix2 == self.matrix:
         return True, "Steady grid."
      if self.matrix_repeat(matrix2):
         self.repeat_count += 1
         if self.repeat_count >= 5:
            return True, "Repeating grid."

      self.iterations += 1
      self.matrix = matrix2
      return False, ""

   def con_calc(self, me, indexes):
       count = 0
       for i,j in indexes:
           if self.matrix[i][j]:
               count += 1

   # Conway rules    
   #   Any live cell with fewer than two live neighbours dies, as if caused by underpopulation.
   #   Any live cell with two or three live neighbours lives on to the next generation.
   #   Any live cell with more than three live neighbours dies, as if by overpopulation.
   #   Any dead cell with exactly three live neighbours becomes a live cell, as if by reproduction.

       i, j = me
       if self.matrix[i][j]:                 # Me, a live cell
           return count == 2 or count == 3
       else:                            # Me, a dead cell
           return count == 3


   def filter(self, indexes, max_x, max_y):
       index2 = []
       for ind in indexes:
           i, j = ind
           if i < 0 or j < 0 or i >= max_x or j >= max_y:
               continue    
           index2.append(ind)
       return index2

   def conway(self):
       self.cell_count = 0
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

               indexes = self.filter(indexes, con_x, con_y)          # discard entries that don't work
               matrix2[i][j] = self.con_calc((i,j), indexes)
               if matrix2[i][j]:
                   self.cell_count += 1

       return matrix2

   def store_matrix(self):
       max_mhi = 20                 # max matrix history index
     
       if len(self.matrix_history) < max_mhi:
           self.matrix_history.append(self.matrix)
       else:
           self.matrix_history[self.mh_index] = self.matrix

       self.mh_index = (self.mh_index+1) % max_mhi

   def matrix_repeat(self, matrix2):
       for i in range(0, len(self.matrix_history)):
           if matrix2 == self.matrix_history[i]:
               return True
       return False
   
#--------------------------------------------------------------------------------------------------
def signal_handler(signal, other):
#   May not work!
    print("\nKeyboard/kill Interrupt. Iteration count:", conway.iterations, "\n")
    master.destroy()
    sys.exit(0)

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

master = Tk()
master.title("Conway: Game of Life")

conway = Conway()

app = App(master, conway)

signal.signal(signal.SIGTERM, signal_handler)       # kill in background mode

try:
   mainloop()
except KeyboardInterrupt:
   print("\nKeyboard Interrupt")
   master.destroy()
