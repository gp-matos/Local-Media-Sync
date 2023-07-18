experiment.py is where youre just testing things to see how they work in code, not part of app
main.py is where all the code is at
test folder is the folder you made that holds a bunch of pictures youre using to test the program
dump folder is a temporary folder you made to test being able to move the pictures

you were able to extract date from all the files with exif data (photos) and prompt the user to select where they want to save their stuff and move them there, now you need to:
1. figure out how to find matching json files for files that dont have exif data (account for weird naming anomalies (duplictes, odd extensions, etc))
2. figure out how to read the date in the json file and parse it the same way as the others
3. dump any files that are still unaccounted for in a misc folder
4. prompt user to pick where they extracted their google photos (instead of using test folder)
5. check for bugs
6. make a GUI so user doesnt have to fuck with command line
7. turn it into an .exe
8. make code and files pretty and organize and post to github (learn git)
