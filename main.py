from exif import Image
import os as os
import shutil as shutil
import json as json
import re as re
import argparse as argparse
from pathlib import Path
from datetime import datetime
from tqdm import tqdm


def main(user_in, user_out):

    #---VARIABLES---
    RAW_TAKEOUT_FOLDER = Path(user_in)
    DUMP_FOLDER = Path(user_out)
    all_files = list(RAW_TAKEOUT_FOLDER.rglob('*'))
    total_files = len(all_files)
    completed_files = 0
    number_of_json_files = 0
    number_of_misc_files = 0
    progress_value = 0
   
    """
    item: the path to the file that is to be sorted
    dump_folder: path to where the user wants to send the photos
    """
    def sort_photo(item: Path, dump_folder: Path): #takes a file and sorts it

        nonlocal total_files
        nonlocal completed_files
        nonlocal number_of_json_files
        nonlocal number_of_misc_files
        nonlocal progress_value

        if item.is_file(): #checks if input is actually a file and not a directory
            completed_files += 1
            if item.name.endswith('.json'): #ignore .json files
                number_of_json_files += 1
                return
            elif exif_extension(item): #checks if file has EXIF data
                handle_file(item, dump_folder)
            else: 
                json_list = find_json(item)
                if json_list: #checks if there exists a corresponding .json file
                    json_file = json_list[0]
                    handle_file(item, dump_folder, json_file)
                else: #can't find date, send file to misc folder
                    number_of_misc_files += 1
                    handle_file(item, dump_folder, json_file = None, misc = True)

        
    """
    file: path to the file that is being handled
    dump_folder: path to the location the user wishes to save the photos to
    json_file: path to the .json file corresponding to the file (optional - only passed in when file has no EXIF data)
    misc: boolean to indicate if file is misc
    """
    def handle_file(file: Path, dump_folder: Path, json_file: Path = None, misc: bool = False): #gets the date from file and sends file to appropriate year/month folder
        if misc: #if its a misc file, send to misc folder
            temp_dict = {}
            file_destination = make_new_directory(dump_folder, temp_dict, True)
            shutil.move(str(file), str(file_destination))
        elif json_file is None: #if there is no json file, get the date using EXIF, send to destination
            date_parsed = extract_date(file)
            file_destination = make_new_directory(dump_folder, date_parsed)
            #print(f'HAS EXIF-file: {file.name}, date: {str(date_parsed)}')
            shutil.move(str(file), str(file_destination))
        else: #if there is a json file, use it to get the date, send to destination
            date_parsed = parse_json(json_file)
            file_destination = make_new_directory(dump_folder, date_parsed)
            #print(f'NO EXIF-file: {file.name}, date: {str(date_parsed)}, json file: {str(json_file)}')
            shutil.move(str(file), str(file_destination))
 
    """
    json_file: path to the json file
    """
    def parse_json(json_file: Path): #get date from json file
        with json_file.open('r') as f:
            json_dict = json.load(f)
        date_str = json_dict['photoTakenTime']['formatted']
        date_dict = parse_date(date_str, True)
        return date_dict
        
    """
    file: path to the file we're getting the date from
    """
    def extract_date(file: Path): #extracts the date from files with valid EXIF extensions
        normalized_path = file.resolve() #this normalizes the path name so it works on multiple operating systems' file structures
        with open(str(normalized_path), 'rb') as f:
            image = Image(f)
            date_str = image.datetime_original
        date_dict = parse_date(date_str, False) #False because it is parsing a date string that is NOT from a json file
        return date_dict
    
    """
    date_str: string to be parsed
    is_json: boolean, True = string is from json file, False = string is from EXIF data (they have different formats)
    """
    def parse_date(date_str, is_json: bool): #parses date string into dictionary with year, month, and day
        if is_json: #parses string from json file
            clean_date_str = re.sub(r'[^\x00-\x7F]+', '', date_str)
            datetime_object = datetime.strptime(clean_date_str, "%b %d, %Y, %I:%M:%S%p %Z")
            date_dict = {
                'year': datetime_object.strftime("%Y"),
                'month': datetime_object.strftime("%B-%m"),
                'day': datetime_object.strftime("%d")
            }
            return date_dict
        else: #parses string from EXIF data
            remove_time = date_str.split(' ')[0]
            date_list = remove_time.split(':')
            month = datetime.strptime(date_list[1], "%m")
            formatted_month = month.strftime("%B-%m")
            date_list[1] = formatted_month
            date_keys = ['year', 'month', 'day']
            date_dict = {date_keys[i]: date_list[i] for i in range(len(date_keys))}
            return date_dict
           
    """
    file: path to file to be checked
    """
    def exif_extension(file: Path): #checks if the file has a valid EXIF extension (i.e. .jpg, .heic, etc)
        good_extensions = ['.jpg', '.jpeg', '.JPEG', '.heic', '.HEIC']
        if any(file.suffix.endswith(ext) for ext in good_extensions):
            return True
        else:
            return False

    """
    destination: path to dump folder
    dict: dictionary with the file's date information
    misc: boolean to determine whether we're dealing with misc folder
    """
    def make_new_directory(destination: Path, dict: dict, misc: bool = False): #returns the final destination folder for the file (year/month/misc), create it if it doesn't exist yet
        destination_folder = destination / 'here are your photos'
        if not destination_folder.exists(): #wrapper folder for all the photos
            destination_folder.mkdir()
        if misc: #checks is file is misc
            misc_folder = destination_folder / 'misc'
            if misc_folder.exists():
                return misc_folder
            else:
                misc_folder.mkdir()
                return misc_folder
        else:
            year_folder = destination_folder / dict['year']
            month_folder = None
            if year_folder.exists(): #checks if proper year folder already exists
                month_folder = year_folder / dict['month']
                if not month_folder.exists(): #checks is proper year folder already exists
                    month_folder.mkdir()
            else:
                year_folder.mkdir()
                month_folder = year_folder / dict['month']
                month_folder.mkdir()
            return month_folder #returns final destination folder

    """
    file: path to file that need to find the corresponding json for
    """
    def find_json(file: Path): #finds the corresponding json for a file if it exists
        file_stem = file.stem
        parent_folder = file.parent
        tag_pattern = r'\((\d+)\)'
        check_match = re.search(tag_pattern, file_stem) #checks if file name has tag like (3) - means there's multiple files with same stem
        if check_match: #if file does have tag
            tag = check_match.group(0) #extracts tag from stem
            file_stem = file_stem.replace(tag, "") #remove tag from stem string, makes it easier to find json
            json_match = [file for file in parent_folder.iterdir() if file.is_file() and file.name.endswith('.json') and re.search(file_stem, file.name) and re.search(tag, file.name)] #searches for json
        else: #file does not have tag
            json_match = [file for file in parent_folder.iterdir() if file.is_file() and file.name.endswith('.json') and re.search(file_stem, file.name)] #searches for json
        return json_match

    #runs the program with progress bar (tqdm)
    with tqdm(total= total_files, unit= "files", colour= "green") as pbar:
        for file in all_files:
            sort_photo(file, DUMP_FOLDER)
            pbar.update(1)

    #---display statistics---
    print("Statistics: ")
    print(f"Total files present: {total_files}")
    print(f"Total files processed: {completed_files}")
    print(f"Number of json files: {number_of_json_files}")
    print(f"Number of files in misc folder: {number_of_misc_files}")


"""
THIS PART IS NOT NECESSARY, ITS JUST USEFUL IF YOU WANT TO RUN THE THING FROM THE COMMAND LINE
"""
if __name__ == '__main__':
    user_in = input("please enter the directory where your google takeout photos are located: ")
    user_out = input("please enter the directory where you would like to save your sorted photos: ")
    main(user_in, user_out)

