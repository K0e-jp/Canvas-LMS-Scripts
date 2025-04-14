Canvas has issues processing .bmp images for bulk uploads, the script checks for the mimetype of pictures in the "images" folder and creates a .jpg copy of those images in the "converted_images" folder.
.jpg and .png files are uploaded directly without conversion. If you only store images in jpg or png you can skip installing/importing pillow and delete the code blocks that deal with the conversion process.
The file csv.csv has to be filled with the SIS ID of the canvas users and the name of the image in the original folder, this is very convenient for my use case as my institution saves student pictures as "SIS_ID.bmp" so it's very easy to populate the csv file with a formula.
It's possible to use other data (ex. student name and last name) to check for matches between canvas users and pictures in the folder. This requires different Canvas API calls and was not included as it doesn't fit my use case, but should be very easy to implement.
The script can be adjusted to accomodate different image mimetypes, just adjust the convert_bmp_to_jpg function.


