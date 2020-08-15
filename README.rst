============
honorary_gui
============


This repository hosts un bunch of test .py files that I came up with when developing a salary calculator for my mom.


Description
===========
The final file, honorary_calc_message_check.py (all files in //src folder) is the first output of this project, and when called, outputs a GUI that allows the user to enter start and end dates of missions, as well as start and end hours. 

The code is very basic. 

1) It first calculates the number of hours worked.

2) It then looks at the number of hours per day and per night.
Night and day is at the moment hard-wired, with days ranging between 0700 and 2200.

3) It then look at whether the dates (start and end if different) are regular business days or weekend/holidays. 
This is based at the moment on French Calendar.

It then adds up the fees per hour and output it in a simple message box.

I will add more calendars in the future, and allow the user to define the fees to be paid be hour, as well as the day/night shifts.

