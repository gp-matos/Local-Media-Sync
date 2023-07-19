What does this do?

If you have ever tried to export all your photos from google photos,you know that the files that result from that process are very messy and hard to navigate.
You'll get a bunch of different takeout folder with similar names and multiple copies of folders with the same year, and worst of all, all the folders are littered 
with .json files that correspond to each image/video you have. These .json files contain metadata info about your images. 

This tool helps sort out the mess that is google takeout. It will go through each file in your google takeout, read the date it was taken, and move the files to 
folders sorted my month and year. For instance a photo takin on August 5th, 2016 will be moved to ".../your photos/2016/August/". For files where the tool is unable to 
determine the date, it will be sent to a misc folder so that every file is accounted for, leaving behind only .json files. 

How to use:

Go through the google takeout process like normal. Extract the zip folders from google takeout all into a single folder (you may have multiple zip files depending on 
how many photos you have, the all need to be extracted into a single folder). Simply install the .exe file, and run it. It will prompt you to select the folder in which
you extracted the google takeout files, and the folder where you would like to save your sorted files. Please ensure the destination folder you select is empty; this is 
because if there are any files already in the destination directory, it could cause naming conflicts with the google files, which may result in files being unintentionally 
overridden. Press "GO" and the program will run. A message will pop up notifying you that you're done. And thats it! You should now have a folder with all your photos 
backed up by year and month.