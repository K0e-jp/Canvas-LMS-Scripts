import csv
import requests
import os
import mimetypes
from PIL import Image

# Configuration
working_path = "./"
log_filename = "failed.txt"
csv_filename = "csv.csv"
images_path = "images/"
output_folder = "converted_images"
CANVAS_DOMAIN = "-"
ACCESS_TOKEN = "-"

header = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
valid_mimetypes = ("image/jpeg", "image/png", "image/bmp")

def convert_bmp_to_jpg(image_path, output_folder):
    if not image_path.lower().endswith(".bmp"):
        return image_path, mimetypes.guess_type(image_path)[0]  # No conversion needed

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    new_filename = os.path.basename(image_path).rsplit(".", 1)[0] + ".jpg"
    new_image_path = os.path.join(output_folder, new_filename)
    try:
        with Image.open(image_path) as img:
            rgb_im = img.convert("RGB")
            rgb_im.save(new_image_path, format="JPEG")
        return new_image_path, "image/jpeg"
    except Exception as e:
        print(f"Failed to convert BMP to JPG for {image_path}: {e}")
        return None, None

with open(f"{working_path}{csv_filename}") as csv_file:
    read_csv = csv.DictReader(csv_file)
    for row in read_csv:
        original_path = os.path.join(working_path, images_path, row["image_filename"])
        if not os.path.isfile(original_path):
            print(f"{original_path} does not exist, skipping to next record")
            with open(log_filename, "a") as f:
                f.write(row["user_id"] + "\n")
            continue

        image_path, mime_type = convert_bmp_to_jpg(original_path, output_folder)

        if not image_path or mime_type not in valid_mimetypes:
            print(f"Invalid or failed file for user {row['user_id']}, skipping.")
            continue

        inform_api_url = f"https://{CANVAS_DOMAIN}/api/v1/users/self/files"
        inform_parameters = {
            "name": os.path.basename(image_path),
            "content_type": mime_type,
            "size": os.path.getsize(image_path),
            "parent_folder_path": "profile pictures",
            "as_user_id": f"sis_user_id:{row['user_id']}"
        }

        try:
            res = requests.post(inform_api_url, headers=header, data=inform_parameters)
            res.raise_for_status()
            data = res.json()

            with open(image_path, "rb") as file_to_upload:
                files = {"file": file_to_upload}
                upload_params = data.get("upload_params")
                upload_url = data.get("upload_url")
                upload_file_res = requests.post(upload_url, data=upload_params, files=files, allow_redirects=False)
                upload_file_res.raise_for_status()

            confirmation_url = upload_file_res.headers["location"]
            confirmation = requests.post(confirmation_url, headers=header)
            confirmation.raise_for_status()

            avatar_options = requests.get(
                f"https://{CANVAS_DOMAIN}/api/v1/users/sis_user_id:{row['user_id']}/avatars", headers=header
            )
            avatar_options.raise_for_status()

            for ao in avatar_options.json():
                if ao.get("display_name") == os.path.basename(image_path):
                    token = ao.get("token")
                    params = {"user[avatar][token]": token}
                    set_avatar_user = requests.put(
                        f"https://{CANVAS_DOMAIN}/api/v1/users/sis_user_id:{row['user_id']}",
                        headers=header,
                        params=params
                    )
                    if set_avatar_user.status_code == 200:
                        print(f"Profile image set for user - {row['user_id']}")
                    else:
                        print(f"Failed to set profile image for user - {row['user_id']}")
                    break
            else:
                print(f"Uploaded image not found in avatar options for user - {row['user_id']}")

        except requests.exceptions.RequestException as e:
            print(f"Error processing user {row['user_id']}: {e}")
