# from fastapi import FastAPI, HTTPException
# from datetime import datetime
# from fastapi.responses import Response
# from feedgenerator import Rss201rev2Feed
# import logging
# import re
# from pathlib import Path
# import base64
# from PIL import Image
# from io import BytesIO
# import instaloader
# import shutil

# # Initialize FastAPI app
# app = FastAPI()

# # Configure logging
# logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

# def sanitize_filename(filename):
#     """Sanitizes a filename to be valid on most operating systems."""
#     sanitized = re.sub(r'[\\/*?:"<>|]', '_', filename)
#     return sanitized

# def resize_and_encode_image(image_path, target_size=(800, 800)):
#     """
#     Resize the image while maintaining aspect ratio, convert it to RGB, and encode it as Base64 in WebP format.
#     :param image_path: Path to the image file
#     :param target_size: Tuple (width, height) for resizing
#     :return: Base64 encoded string of the resized image
#     """
#     try:
#         with Image.open(image_path) as img:
#             # Resize the image while maintaining aspect ratio
#             img.thumbnail(target_size)

#             # Convert to RGB before saving to WebP (WebP doesn't support alpha channel)
#             img = img.convert("RGB")

#             # Save the image to a buffer in WebP format
#             buffer = BytesIO()
#             img.save(buffer, format="WEBP")
#             buffer.seek(0)

#             # Encode the image to Base64
#             encoded_string = base64.b64encode(buffer.getvalue()).decode('utf-8')

#             # Return the Base64 HTML img tag for embedding
#             return f'<br><img src="data:image/webp;base64,{encoded_string}">'

#     except Exception as e:
#         logging.error(f"Error processing image: {e}")
#         return None

# def get_instagram_rss(profile_name: str, limit: int = 5, output_dir: str = "."):
#     """
#     Fetches the latest posts from a public Instagram profile and generates an RSS feed.
#     """
#     try:
#         # Sanitize output directory
#         sanitized_output_dir = Path(output_dir) / profile_name
#         sanitized_output_dir.mkdir(parents=True, exist_ok=True)

#         # Initialize Instaloader
#         L = instaloader.Instaloader()

#         # Set up options for Instaloader
#         L.dirname_pattern = str(sanitized_output_dir)  # Convert Path to string for dirname_pattern
#         L.download_metadata = False  # Don't download metadata JSON files
#         L.post_metadata_txt_pattern = "{date_utc}\n{caption}\nhttps://www.instagram.com/p/{shortcode}/"  # Format of metadata text

#         # Load the profile
#         profile = instaloader.Profile.from_username(L.context, profile_name)

#         # Download posts with the limit specified
#         count = 0
#         for post in profile.get_posts():
#             if count >= limit:
#                 break
#             L.download_post(post, target=profile_name)  # Download the post
#             count += 1

#         # Construct path to the text files
#         post_dir = sanitized_output_dir
#         files = list(post_dir.glob('*.txt'))
#         logging.debug(f"Files found: {files}")

#         if not files:
#             logging.warning(f"No txt files found for profile {profile_name}")
#             return None

#         # Create RSS feed
#         feed = Rss201rev2Feed(
#             title=f"Instagram Profile ({profile_name}) Feed",
#             link=f"https://www.instagram.com/{profile_name}/",
#             description=f"RSS feed generated from Instagram profile {profile_name}",
#         )

#         for file in files:
#             with open(file, "r", encoding="utf-8") as f:
#                 content = f.read().strip()
#                 logging.debug(f"Content read from: {file.name}, content: {content}")

#                 if "instagram.com" not in content:
#                     logging.debug(f"Skipping file because it does not contain Instagram URL: {file.name}")
#                     continue  # Skip if no Instagram URL

#                 # Extract data from the caption file
#                 match = re.match(r"^(?P<date>[^\n]+)\n(?P<caption>.+)\n(?P<link>.+)", content, re.DOTALL)
#                 if match:
#                     date_str = match.group("date")
#                     caption = match.group("caption")
#                     post_url = match.group("link")

#                     # Parse date string
#                     try:
#                         date_str = date_str.replace("_UTC", "")
#                         pubdate = datetime.strptime(date_str, "%Y-%m-%d_%H-%M-%S")  # Explicit formatting
#                     except ValueError as e:
#                         logging.error(f"Error parsing date: {date_str} in file {file.name}. Error: {e}")
#                         continue

#                     # Find image (JPG or PNG)
#                     image_path = list(post_dir.glob(f'{file.name[:-4]}*.jpg')) or list(post_dir.glob(f'{file.name[:-4]}*.png'))  
#                     image_base64 = None

#                     if image_path:
#                         # Resize and encode image
#                         image_base64 = resize_and_encode_image(image_path[0], target_size=(800, 800))

#                     # Prepare feed item
#                     item = {
#                         "title": f"Instagram Post by {profile_name}",
#                         "link": post_url,
#                         "description": f"{caption if caption else ''} ",
#                         "pubdate": pubdate,
#                     }
#                     feed.add_item(**item)

#         logging.debug(f"RSS feed generation completed for profile {profile_name}")
#         rss_content = feed.writeString("utf-8")

#         # Remove profile directory after generating RSS feed
#         if sanitized_output_dir.exists():
#             logging.debug(f"Removing profile directory: {sanitized_output_dir}")
#             shutil.rmtree(sanitized_output_dir)

#         return rss_content

#     except Exception as e:
#         logging.exception(f"Failed to generate Instagram feed: {e}")
#         raise HTTPException(status_code=500, detail=f"Error generating Instagram feed: {e}")

# @app.get("/generate_rss")
# async def generate_instagram_rss(profile_name: str, limit: int = 5):
#     """
#     Endpoint to generate RSS feed from Instagram profile.
#     """
#     try:
#         rss_content = get_instagram_rss(profile_name, limit)
#         if rss_content:
#             # Return the RSS feed content as an XML file in the response
#             return Response(content=rss_content, media_type="application/rss+xml", headers={"Content-Disposition": "attachment; filename=instagram_feed.xml"})
#         else:
#             raise HTTPException(status_code=404, detail="No posts found or unable to generate feed.")
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

from fastapi import FastAPI, HTTPException
from datetime import datetime
from fastapi.responses import Response
from feedgenerator import Rss201rev2Feed
import logging
import re
from pathlib import Path
import instaloader
import shutil

# Initialize FastAPI app
app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

def sanitize_filename(filename):
    """Sanitizes a filename to be valid on most operating systems."""
    sanitized = re.sub(r'[\\/*?:"<>|]', '_', filename)
    return sanitized

def get_instagram_rss(profile_name: str, limit: int = 5, output_dir: str = "."):
    """
    Fetches the latest posts from a public Instagram profile and generates an RSS feed.
    """
    try:
        # Sanitize output directory
        sanitized_output_dir = Path(output_dir) / profile_name
        sanitized_output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize Instaloader
        L = instaloader.Instaloader()

        # Set up options for Instaloader
        L.dirname_pattern = str(sanitized_output_dir)  # Convert Path to string for dirname_pattern
        L.download_metadata = False  # Don't download metadata JSON files
        L.post_metadata_txt_pattern = "{date_utc}\n{caption}\nhttps://www.instagram.com/p/{shortcode}/"  # Format of metadata text

        # Load the profile
        profile = instaloader.Profile.from_username(L.context, profile_name)

        # Create RSS feed
        feed = Rss201rev2Feed(
            title=f"Instagram Profile ({profile_name}) Feed",
            link=f"https://www.instagram.com/{profile_name}/",
            description=f"RSS feed generated from Instagram profile {profile_name}",
        )

        # Download posts with the limit specified
        count = 0
        for post in profile.get_posts():
            if count >= limit:
                break

            # Extract post details
            caption = post.caption
            date = post.date
            post_url = f"https://www.instagram.com/p/{post.shortcode}"
            image_url = post.url  # Get the main image URL for the post
            likes = post.likes

            # Create image markdown for RSS feed if the post has an image
            image_markdown_tag = f"![Image]({image_url})" if image_url else ""
            #  {image_markdown_tag}
            # Prepare feed item
            item = {
                "title": f"Instagram Post by {profile_name}",
                "link": post_url,
                "description": f"{caption if caption else ''}",
                "pubdate": date,
            }
            feed.add_item(**item)
            count += 1

        logging.debug(f"RSS feed generation completed for profile {profile_name}")
        rss_content = feed.writeString("utf-8")

        # Remove profile directory after generating RSS feed
        if sanitized_output_dir.exists():
            logging.debug(f"Removing profile directory: {sanitized_output_dir}")
            shutil.rmtree(sanitized_output_dir)

        return rss_content

    except Exception as e:
        logging.exception(f"Failed to generate Instagram feed: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating Instagram feed: {e}")

@app.get("/generate_rss")
async def generate_instagram_rss(profile_name: str, limit: int = 5):
    """
    Endpoint to generate RSS feed from Instagram profile.
    """
    try:
        rss_content = get_instagram_rss(profile_name, limit)
        if rss_content:
            # Return the RSS feed content as an XML file in the response
            return Response(content=rss_content, media_type="application/rss+xml", headers={"Content-Disposition": "attachment; filename=instagram_feed.xml"})
        else:
            raise HTTPException(status_code=404, detail="No posts found or unable to generate feed.")
    except Exception as e:
        logging.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
