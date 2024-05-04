# University of Michigan Lecture Downloads

The scripts included here enable University of Michigan-affiliated individuals to download lectures from the Lecture Capture system ([leccap.engin.umich.edu](https://leccap.engin.umich.edu)). 

As ITS does not make any promises about how long course recordings are retained, downloading content is the best way to ensure that you can access it whenever you want. As of May 2024, course recordings seem to be preserved for at least three years. 

Note that the [CAEN website](https://caen.engin.umich.edu/lecrecording/students/) states that:
> Students who wish to obtain video file downloads of lecture recordings must contact their course instructors directly. Only the instructors of a course may authorize download access.

As such, please contact the instructors of any courses you wish to download before using these scripts. 

## Overview 
The Python script in [`mass-download/`](/mass-download/) enables users to download **any subset** of lectures from **any number of courses**. This script should take no more than five minutes to set up and run (although the actual downloads may take far longer).

Credit goes to [@ajaypillay](https://github.com/ajaypillay) for inspiring this project. A (slightly modified) version of his original script can be found in [`one-off-script/`](/one-off-script/). This script can be run in the browser console and enables users to download all the lectures for a single course.

Note that a single 85-minute lecture video takes about 400 MB to store; please ensure you have enough storage availablle before using these scripts. 

## Usage (Mass Download)
### Python Setup
If you don't have Python installed, you may download it from [here](https://www.python.org/downloads/). 

Navigate to the `mass-download/` directory in your terminal and run
```
$ pip install -r requirements.txt
```
in order to install all necessary packages. You will also need to have Chrome installed. 

### Config Setup
You can configure which courses and lectures to download in `mass-download/config.json`. Please modify this file for your specific coures.

The `start_year` denotes the first year to begin looking for recordings. 

The `directory_path` signifies where you want your recordings saved. Each course will be a separate folder inside this path. For instance:
```
/Volumes/SSD/lectures   // directory_path
    - eecs280
        - links.txt
        - download_output.txt
        - recording1.mp4
        - recording2.mp4
        - ...
    - eecs281
    - eecs376
    - ...
``` 

The `courses` object has information about which courses you want to scrape. Each course is a separate entry in this dictionary. The name of the course (for instance, `eecs 281`) is searched for in the titles of courses. 

### Running the script
Navigate to the `mass-download/` directory in your terminal and run `$ make`. 

The script will open a browser window to the lecture capture website; once you have logged in, the window will automatically minimize and the script will begin scraping the lecture capture website based on your configuration. 




## Usage (One-Off Script)




