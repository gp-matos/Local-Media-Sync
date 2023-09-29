# Local MediaSync

If you have ever tried to export all your photos from Google Photos, you know that the files that result from that process are very messy and hard to navigate. You'll get a bunch of different Takeout folders with similar names and multiple copies of folders with the same year, and worst of all, all the folders are littered with .json files that correspond to each image/video you have. These .json files contain metadata info about your images.

This tool helps sort out the mess that is Google Takeout. It will go through each file in your Google Takeout, read the date it was taken, and move the files to folders sorted by month and year. For instance, a photo taken on August 5th, 2016, will be moved to ".../your photos/2016/August/". For files where the tool is unable to determine the date, it will be sent to a misc folder so that every file is accounted for, leaving behind only .json files.

Additionally, Local MediaSync will also help you sort large amounts of photos from other sources, assuming the files have date metadata available.

## How to Use (Desktop App)

1. Go through the Google Takeout process like normal.
2. Extract the zip folders from Google Takeout all into a single folder (you may have multiple zip files depending on how many photos you have, they all need to be extracted into a single folder).
3. Simply install the .exe file, and run it.
4. It will prompt you to select the folder in which you extracted the Google Takeout files and the folder where you would like to save your sorted files. Please ensure the destination folder you select is empty; this is because if there are any files already in the destination directory, it could cause naming conflicts with the Google files, which may result in files being unintentionally overridden.
5. Press "GO" and the program will run.
6. A message will pop up notifying you that you're done.
7. That's it! You should now have a folder with all your photos backed up by year and month. You can then delete the old Google Takeout folders.

## How to Use (command line):
1. pull the repo locally
2. run 'python GUI.py' and the app will appear.
3. proceed as normal according to the above instructions.