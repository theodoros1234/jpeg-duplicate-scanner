#!/bin/python3
from PIL import Image
from hashlib import sha256
from datetime import datetime
import os, sys, shutil


class MissingExifDataError(Exception):
    pass


def extract_exif_date_time(filename):
    image = Image.open(filename)
    exif_data = image._getexif()
    date_time = exif_data.get(36867)  # Tag ID for the DateTimeOriginal field

    if date_time is not None:
        formatted_date_time = date_time.replace(':', '').replace(' ', '_')
        return formatted_date_time

    raise MissingExifDataError(f"No EXIF Date and Time found in {filename}")


def calculate_sha256(file_path):
    # Create a SHA256 hash object
    sha256_hash = sha256()

    # Open the file in binary mode and read it in chunks
    with open(file_path, 'rb') as file:
        for chunk in iter(lambda: file.read(4096), b''):
            # Update the hash object with the chunk
            sha256_hash.update(chunk)

    # Get the hexadecimal representation of the hash
    sha256_hex = sha256_hash.hexdigest()

    return sha256_hex


def explore(path, all_files, verbose=False):
    if os.path.isfile(path):
        if path.lower().endswith('.jpg'):
            if verbose:
                print(f'Checking JPG file: {path}')
            sha256_digest = calculate_sha256(path)
            if verbose:
                print("sha256 digest:", sha256_digest)
            if sha256_digest in all_files:
                if verbose:
                    print(f"Duplicate of '{all_files[sha256_digest][0]}' found, skipping.")
            else:
                try:
                    all_files[sha256_digest] = (path, extract_exif_date_time(path))
                except MissingExifDataError as e:
                    print("Warning:", e)
                    print("Modified date will be used instead for this file.")
                    timestamp = os.path.getmtime(path)
                    formatted_timestamp = datetime.fromtimestamp(timestamp).strftime("%Y%m%d_%H%M%S")
                    all_files[sha256_digest] = (path, formatted_timestamp)
                if verbose:
                    print('Added to list.')
        elif verbose:
            print(f'Skipping non-JPG file: {path}')
    elif os.path.isdir(path):
        if verbose:
            print(f'Processing directory: {path}')
        for entry in os.listdir(path):
            entry_path = os.path.join(path, entry)
            explore(entry_path, all_files, verbose)
    elif verbose:
        print(f'Invalid path: {path}')


def copy_all(all_files, destination, verbose=False):
    for f in all_files.values():
        counter = 1
        copied = False
        destination_path = None
        while not copied:
            if counter == 1:
                destination_path = f"{destination}/{f[1]}.jpg"
            else:
                destination_path = f"{destination}/{f[1]}_{str(counter)}.jpg"

            if os.path.exists(destination_path):
                counter += 1
                if verbose:
                    print(f"Destination '{destination_path}' already exists, trying a different filename.")
            else:
                shutil.copy(f[0], destination_path)
                timestamp = int(datetime.strptime(f[1], "%Y%m%d_%H%M%S").timestamp())
                os.utime(destination_path, (timestamp, timestamp))
                copied = True
                if verbose:
                    print(f"Copied '{f[0]}' to '{destination_path}'.")



def print_help_page():
    exec_name = os.path.basename(sys.argv[0])
    help_text = f"""
NAME
    JPEG Duplicate Scanner - Find and copy unique JPEG images based on EXIF
    date/time

SYNOPSIS
    python3 {exec_name} [-h] [-v] <source_paths>... <destination_path>

DESCRIPTION
    The JPEG Duplicate Scanner script scans through a set of JPEG images,
    identifies duplicates, and copies only one version of each image to a
    specified destination folder. The copied images are renamed based on their
    EXIF date/time data.

OPTIONS
    -h, --help
        Print this help page.

    -v, --verbose
        Enable verbose mode. The script will provide detailed output while
        scanning and copying the images.

ARGUMENTS
    <source_paths>
        One or more file paths or directory paths to be recursively searched for
        JPEG files.

    <destination_path>
        The destination directory where the unique JPEG images will be copied.

EXAMPLES
    python3 {exec_name} -v /path/to/images /another/path/to/images /path/to/destination
        Scan and copy unique JPEG images from /path/to/images and
        /another/path/to/images to /path/to/destination while providing verbose
        output.

    python3 {exec_name} image1.jpg image2.jpg image3.jpg /path/to/more/images
    /path/to/destination
        Scan and copy unique JPEG images from image1.jpg, image2.jpg, image3.jpg
        and /path/to/more/images to /path/to/destination without verbose output.

AUTHOR
    Theodoros Nicolaou

CREDITS
    This script was developed with the assistance of ChatGPT, an AI language
    model by OpenAI. Visit https://openai.com/ to learn more about ChatGPT.
"""
    print(help_text)


if __name__=="__main__":
    # Print help page if asked for or when given the wrong amount of arguments
    if len(sys.argv) < 3 \
    or sys.argv[1] == '-h' or sys.argv[1] == '--help' \
    or ((sys.argv[1] == '-v' or sys.argv[1] == '--verbose') and len(sys.argv) < 4):
        print_help_page()

    # Abort if destination directory doesn't exist
    elif not os.path.exists(sys.argv[-1]):
        print("Destination directory doesn't exist.")
        print("No files will be copied.")

    else:
        # Scan source files
        file_list = dict()
        verbose = sys.argv[1] == '-v' or sys.argv[1] == '--verbose'

        print("Scanning source files and directories...")
        try:
            if verbose:
                for i in sys.argv[2:-1]:
                    explore(i, file_list, verbose)
            else:
                for i in sys.argv[1:-1]:
                    explore(i, file_list, verbose)
        except OSError as e:
            print("One of the source files/directories could not be read:", e)
            print("No files will be copied.")
        except FileNotFoundError as e:
            print("One of the source files/directories does not exist:", e)
            print("No files will be copied.")
        except Exception as e:
            print("An unexpected error has occurred while processing source files/directories:", e)
            print("No files will be copied.")
            raise e

        # Copy all non-duplicates to destination directory
        print("Copying all non-duplicates to destination directory...")
        try:
            copy_all(file_list, sys.argv[-1], verbose)
        except FileNotFoundError as e:
            print("A source file or the destination directory was moved or deleted before the copying process finished:", e)
            print("The remaining files will not be copied.")
        except PermissionError as e:
            print("Missing permissions to read a source file or to write to the destination directory:", e)
            print("The remaining files will not be copied.")
        except Exception as e:
            print("An unexpected error has occurred while copying files:", e)
            print("The remaining files will not be copied.")
