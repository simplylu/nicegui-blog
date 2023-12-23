import os

# Define a class called Post to represent a blog post
class Post:
    # Constructor to initialize Post object with various attributes
    def __init__(self, timestamp: str, author: str, category: str, title: str, summary: str, thumbnail: str, published: str, content: str):
        self.timestamp: str = timestamp
        self.author: str = author
        self.category: list = category
        self.title: str = title
        self.summary: str = summary
        self.thumbnail: str = thumbnail
        self.published: str = True if published == "True" else False
        self.content: str = content

# Function to parse a blog post from a file and create a Post object
def parse_post(name: str) -> Post:
    # Open the file for reading
    with open(os.path.join(os.getcwd(), "posts", name), "r") as f:
        # read the entire file content
        f = f.read()
        # Split the file content into metadata and content using '---' as a separator
        metadata = f.split("---")[0].strip()
        # Create a dictionary from metadata lines
        metadata = {l.split(" = ")[0]: l.split(" = ")[1] for l in metadata.splitlines()}
        # Extract content part after the '---' separator
        content = f.split("---")[1].strip()
        # Create and return a Post object with extracted metadata and content
        return Post(
            timestamp=metadata.get("timestamp", "N/A"),
            author=metadata.get("author", "Anonymous"),
            category=metadata.get("category", "").split(","),
            title=metadata.get("title", ""),
            summary=metadata.get("summary", ""),
            thumbnail=metadata.get("thumbnail", ""),
            published=metadata.get("published", "True"),
            content=content
        )