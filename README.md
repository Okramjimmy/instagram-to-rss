# Instagram RSS Feed Generator

This Python-based tool fetches the latest posts from public Instagram profiles and generates an RSS feed. It automates the extraction of Instagram posts, including captions, images, and links, and converts them into a structured RSS format. Features include media embedding, profile clean-up, and customization options.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [API Endpoint](#api-endpoint)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Dependencies](#dependencies)
- [License](#license)

## Features

- **Automated Post Fetching:** Fetches the latest posts from public Instagram profiles.
- **RSS Feed Generation:** Converts Instagram posts into a valid RSS feed.
- **Media Embedding:** Includes images in the RSS feed descriptions (using markdown).
- **Profile Clean-up:** Removes temporary folders created during post processing.
- **Customizable:** Allows specifying the number of posts to fetch.
- **API Endpoint:** Exposes an HTTP endpoint for feed generation.

## Prerequisites

- Python 3.13 or higher.
- `pip` package manager (or `uv` for a faster experience)

## Installation

1.  **Clone the repository (if you have one):**

    ```bash
    git clone <repository_url>
    cd rss-feed-project
    ```

2.  **Create a virtual environment (recommended):**

    ```bash
    python -m venv .venv
    ```

    or using `uv`

    ```bash
    uv venv .venv
    ```

3.  **Activate the virtual environment:**

    - **On Linux/macOS:**

      ```bash
      source .venv/bin/activate
      ```

    - **On Windows:**

      ```bash
      .venv\Scripts\activate
      ```

4.  **Install dependencies:**

    - Using `pip`:

      ```bash
      pip install -r requirements.txt
      ```

    - Using `uv` (faster):
      ```bash
      uv pip install -r requirements.txt
      ```

    or individually

        ```bash
        uv add fastapi feedgenerator google-api-python-client instaloader pillow requests uvicorn
        ```

    **Note:**

    - You may need to manually install `spire.doc` if you are using it in other parts of your project.
    - `uv` provides better and faster dependency management

## Usage

The application exposes an API endpoint that generates an RSS feed based on an Instagram profile.

### API Endpoint

- **`GET /generate_rss`:**

  - **Query parameters:**

    - `profile_name` (required): The username of the Instagram profile.
    - `limit` (optional, default: 5): The number of latest posts to include in the RSS feed.

  - **Response:**

    - Returns a `200 OK` response with the generated RSS feed as an XML file. The file is sent as a download with `instagram_feed.xml` as name.
    - Returns a `404 Not Found` if there are no posts or if the profile does not exist.
    - Returns a `500 Internal Server Error` if there is any issue during feed generation

### Example Usage

Send a GET request to the API endpoint with a `profile_name` and optionally `limit` parameter to generate a custom RSS feed.

Example using `curl`:

```bash
 curl -o instagram_feed.xml "http://localhost:8000/generate_rss?profile_name=nasa&limit=10"
```

This will save the generated file as `instagram_feed.xml`

## Configuration

- **`profile_name`:** This parameter specifies which Instagram profile the application will fetch posts from.
- **`limit`:** This parameter controls how many of the latest posts will be included in the generated RSS feed.
- **Output directory:** The generated files will be in a directory called `output`

## Running the Application

1.  **Navigate to the project directory:**

    ```bash
    cd rss-feed-project
    ```

2.  **Start the FastAPI server:**

    ```bash
    uvicorn main:app --reload
    ```

    This starts the application. You can then access the API endpoint at http://localhost:8000/docs

## Dependencies

The following dependencies are required for this project:

- `fastapi`: Web framework
- `feedgenerator`: For generating RSS feed
- `instaloader`: For downloading posts from instagram
- `pillow`: For image processing
- `requests`: For HTTP requests, including future API calls for other platforms
- `uvicorn`: For running FastAPI

All dependencies are specified in the `pyproject.toml`

## License

This project is open source and does not have any license.
