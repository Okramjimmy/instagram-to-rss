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
