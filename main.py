from exif import Image
import os as os
import shutil as shutil
import json as json
import re as re
import argparse as argparse
from pathlib import Path
from datetime import datetime
from tkinter import Tk
from tkinter.filedialog import askdirectory

def main(user_in, user_out):

    """
    input: path to the input folder where google takeout folders are
    dump_folder: path to the location the user wishes to save the photos to
    """
    def iterate_through(input: Path, dump_folder: Path): #iterates through the folders/files passed in
        nonlocal number_of_files
        nonlocal number_of_misc_files
        for item in input.iterdir():
            if item.is_dir(): #recursively itirates through folders
                iterate_through(item, dump_folder)
            elif item.is_file() and item.name.endswith('.json'): #ignore .json files
                number_of_files += 1
                continue
            else:
                number_of_files += 1
                if exif_extension(item): #checks if file has EXIF data
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
            shutil.copy2(str(file), str(file_destination))
        elif json_file is None: #if there is no json file, get the date using EXIF, send to destination
            date_parsed = extract_date(file)
            file_destination = make_new_directory(dump_folder, date_parsed)
            print(f'HAS EXIF-file: {file.name}, date: {str(date_parsed)}')
            shutil.copy2(str(file), str(file_destination))
        else: #if there is a json file, use it to get the date, send to destination
            date_parsed = parse_json(json_file)
            file_destination = make_new_directory(dump_folder, date_parsed)
            print(f'NO EXIF-file: {file.name}, date: {str(date_parsed)}, json file: {str(json_file)}')
            shutil.copy2(str(file), str(file_destination))
 
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
        good_extensions = ['.jpg', '.jpeg', '.JPEG' '.png', '.PNG', '.webp', '.WEBP', '.tif', '.TIF', '.tiff', '.TIFF', '.svg', '.SVG', '.heic', '.HEIC']
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

    RAW_TAKEOUT_FOLDER = Path(user_in)
    DUMP_FOLDER = Path(user_out)
    number_of_files = 0
    number_of_misc_files = 0

    iterate_through(RAW_TAKEOUT_FOLDER, DUMP_FOLDER)
    print(f'number of files processed: {number_of_files}')
    print(f'number of misc files processed: {number_of_misc_files}')

if __name__ == '__main__':
    user_in = './test'
    user_out = './dump folder'
    main(user_in, user_out)

