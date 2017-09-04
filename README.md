# Ron's Conway Game of Life
![Conway grid](https://github.com/rongrimes/conway/blob/master/Conway.png)  
&nbsp;  
---
Absolutely the world needs another Conway Game of Life implementation. This version is:
* more colourful
* more exotic
* more "yes, absolutely"  
... than any other version ever written.

## Purpose:
I wanted to learn basic tk (windows) progamming in Linux. I used a very simple learning package from:
* http://www.python-course.eu/index.php (free - thanks guys!)  
... which gave me the basics. And then I just added pieces from there. 

## Environment
The program was developed on a (usually) headless Raspberry Pi with MobaXterm software running on a Windows platform. I developed and ran the program in an _ssh_ window, and MobaXterm acted as an X-Server to display the grid in Windows.

The "production environment" is a Raspberry Pi with a Touchscreen Display.

---

## Features
### Restart
This action discards the current cycle and starts a new cycle. Apart from just playing with it, the button is only needed on rare occasions.

The program checks back for the last _20_ iterations to see if the current state has been previously shown. If so, the cycle will end (or end soon), and then restart. There is one pattern that takes over 40 iterations to repeat, and is not being trapped. If this situation occurs, then a <b>Restart</b> is necessary. The condition can be recognized when the <i>Iterations</i> count gets above more than 1000.

### Single step mode
The cycle can be shown in single step mode. Touch the <b>Single Step</b> button, and then touch the button repeatedly to take it through its steps. Touch <b>Continue</b> to resume normal operation.

### Status Display
Self explanatory for most values.  
<b>Max</b>: Highest number of iterations for a cycle since the program began.

---

### Config
![Config window](https://github.com/rongrimes/conway/blob/master/Config.png)  
The _Width_ and _Height_ of the display window are adjustable. This enables runtime sizing for the display (for me, the Raspberry Pi Touchscreen Display).

The <b>Init. cell prob.</b> (initial cell probability) controls the density of the grid at the begining of a cycle. Each cell has a probability (out of 10) of being initialized, with "1" being a low probability while 9 is "high". Heuristic analysis shows that an initial cell probability of 3 or 4 gives the longest run cycles. 
