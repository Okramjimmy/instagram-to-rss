

from fastapi import FastAPI, HTTPException
from fastapi.responses import Response, HTMLResponse
from feedgenerator import Rss201rev2Feed
import logging
import re
import instaloader

# Initialize FastAPI app
app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

def get_instagram_rss(profile_name: str, limit: int = 5):
    """
    Fetches the latest posts from a public Instagram profile and generates an RSS feed.
    """
    try:
        # Initialize Instaloader
        L = instaloader.Instaloader()
        # Set custom user-agent and session settings
        L.context.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        

        # Set up options for Instaloader
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

            # Create image markdown for RSS feed if the post has an image
            image_markdown_tag = f"![Image]({image_url})" if image_url else ""

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

        return rss_content

    except Exception as e:
        logging.exception(f"Failed to generate Instagram feed: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating Instagram feed: {e}")

# Root route
@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <html>
        <head>
            <title>Welcome to Instagram to RSS Feed</title>
        </head>
        <body>
            <h1>Welcome to the Instagram to RSS Feed Generator!</h1>
            <p>To get started, please visit the <a href="/docs">API Documentation</a>.</p>
        </body>
    </html>
    """

# Endpoint to generate RSS feed
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
