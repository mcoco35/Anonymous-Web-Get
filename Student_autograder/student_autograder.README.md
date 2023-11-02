This is the student version of the autograder for PA2 in class cs457 

This is given to you as a kindness to both you, and the TAs grading this project. This project is autograded, and this is given to you to make sure that your code can be read by the autograder, and give you a few sanity checks.

# Instructions for use: 

## Prerequisite: 

#### Files:
This autograder contains a few files (you will need all of them in the same directory):
- auto_grader.py
- test_server.py
- the_tests.py
- utils.py

#### sshing:
This code assumes that you are running this on the CSU machines, and it is not austin, or denver
You must have an ssh key set up so from inside the department you can easily ssh from machine to machine. [see here](https://sna.cs.colostate.edu/remote-connection/ssh/keybased/)

#### File setup:
Overall the structure of your directory should look something like:
- outer directory
    - auto_grader.py
    - test_server.py
    - the_tests.py
    - utils.py  
    - ss.py (YOURS)
    - awget.py (YOURS)


# Running:
This expects for you to have working code, and it is mostly complete, please test your own code and DO NOT rely on this. 
To run this the autograder: `python3 auto-grader.py`
It will write out the result to a local text file `awget_project_report.txt`. 


# Notes:
- The tests do not test everything, or all requirments of the program. 
- This JUST tests if it can read your output, and so the main autograder can
- If you cannot pass this autograder you will not pass the main autograder.
- This is a brand new autograder, so if you think there is an issue PLEASE EMAIL/MESSAGE the TAs
