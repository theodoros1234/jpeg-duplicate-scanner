# JPEG Duplicate Scanner

The JPEG Duplicate Scanner is a Python script that scans through a set of JPEG images, identifies duplicates, and copies only one version of each image to a specified destination folder. The copied images are renamed based on their EXIF date/time data.

## Description

The script recursively searches through the specified source paths for JPEG files and identifies duplicate images based on their content. Only one version of each unique image is copied to the destination directory, ensuring that no duplicate images are present in the copied set. The copied images are renamed using their EXIF date/time data.

## Usage

To run the script, use the following command:

```
python3 jpeg-duplicate-scanner.py [-h] [-v] <source_paths>... <destination_path>
```

### Options

- `-h, --help`: Print the help page.
- `-v, --verbose`: Enable verbose mode to display detailed output during the scanning and copying process.

### Arguments

- `<source_paths>`: One or more file paths or directory paths to be recursively searched for JPEG files.
- `<destination_path>`: The destination directory where the unique JPEG images will be copied.

## Examples

Example command to scan and copy unique JPEG images from source paths to the destination path while providing verbose output:

```
python3 jpeg-duplicate-scanner.py -v /path/to/images /another/path/to/images /path/to/destination
```

Example command to scan and copy unique JPEG images from specific files and source paths to the destination path without verbose output:

```
python3 jpeg-duplicate-scanner.py image1.jpg image2.jpg image3.jpg /path/to/more/images /path/to/destination
```

## Author

Theodoros Nicolaou

## Credits

This script was developed with the assistance of ChatGPT, an AI language model by OpenAI. Visit [https://openai.com/](https://openai.com/) to learn more about ChatGPT.
