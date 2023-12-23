from typing import Optional, Callable, List, Dict
from nicegui import APIRouter, Client, app, ui
from contextlib import contextmanager
from urllib.parse import quote_plus, unquote
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
from methods import *
import os

# Add static files route for assets
app.add_static_files("/assets", "./assets")

# Load environment variables from a .env file
load_dotenv()

# Create an APIRouter instance
router = APIRouter()

# Global dictionaries to store categories, authors, and posts
CATEGORIES: Dict[str, int] = {}
AUTHORS: Dict[str, str] = {}
POSTS: Dict[str, Post] = {}


# Initialization function to load posts, authors, and categories
def init():
    global POSTS, AUTHORS, CATEGORIES
    posts = os.listdir("posts")
    for post in posts:
        post = parse_post(post)
        if post.published:
            POSTS[quote_plus(post.title)] = post
    
    # Extract authors and categories information
    categories = []
    for post in POSTS.values():
        try:
            about_author = open(f"./authors/{post.author}.md", "r").read()
        except:
            about_author = ""
        AUTHORS[post.author] = about_author
            
        for category in post.category:
            categories.append(category)
    
    # Count the occurrences of each category
    CATEGORIES = {c: categories.count(c) for c in set(categories)}


# Search function to find blog posts based on a query
def search(query: str, el: ui.markdown) -> any:
    res = {}
    for link, blog_post in sorted(POSTS.items()):
        if query.lower() in blog_post.content.lower():
            res[link] = blog_post.title
    
    el.content = f"Results ({len(res)}):\n\n" + "\n\n".join(f"[{title}](/post/{link})" for link, title in res.items())


# Context manager for setting up the UI layout
@contextmanager
def layout(pathname: str):
    # Set up UI colors based on environment variables
    ui.colors(
        primary="#"+os.getenv("PRIMARY"),
        secondary="#"+os.getenv("SECONDARY"),
        accent="#"+os.getenv("ACCENT"),
        positive="#"+os.getenv("POSITIVE")
    )
    
    # Create a search dialog and results markdown element
    with ui.dialog() as search_dialog, ui.card().classes("w-6/12"):
        with ui.row().classes("w-full"):
            inp_search = ui.input(label="Search", on_change=lambda: search(inp_search.value, results)).on(type="keydown.enter", handler=lambda: search(inp_search.value, results)).classes("w-11/12")
            ui.label("X").classes("cursor-pointer ml-auto mb-auto").on("click", handler=search_dialog.close)
        ui.separator()
        ui.label("Results:")
        results = ui.markdown()

    # Create a header with navigation buttons
    with ui.header().classes("justify-between text-white bg-dark"):
        with ui.link(target="/"):
            ui.image(source="/assets/logo.png").classes("w-32")
        with ui.row():
            ui.button("Search", icon="search", on_click=search_dialog.open).props("flat")
            ui.button("Categories", icon="category", on_click=lambda: ui.open("/categories")).props("flat")
            ui.button("Authors", icon="people", on_click=lambda: ui.open("/authors")).props("flat")

    # Create breadcrumb navigation
    with ui.element("q-breadcrumbs"):
        ui.element('q-breadcrumbs-el').props('icon=home').on("click", handler=lambda: ui.open("/")).classes("cursor-pointer")
        for idx, path in enumerate(pathname.split("/")[1:]):
            target = '/'.join(pathname.split("/")[:idx+1])
            ui.element("q-breadcrumbs-el").props(f"label={path}").on("click", handler=lambda: ui.open(target)).classes("cursor-pointer")
    
    # Create a main content column
    with ui.column().classes("w-10/12 ml-auto mr-auto"):
        yield
    
    # Create a footer with copyright information
    with ui.footer().classes("text-center bg-dark items-center"):
        ui.label("(c) 2023 - simplylu").classes("text-center")


# Define the main page at "/"
@ui.page("/")
def index() -> None:
    with layout("/"):
        ui.label("Welcome to NiceBlog").classes("text-bold text-2xl")
        with ui.grid(columns=3):
            for link, blog_post in sorted(POSTS.items()):
                with ui.link(target=f"/post/{link}"):
                    with ui.card().classes("items-center"):
                        ui.label(text=blog_post.title).classes("font-bold")
                        ui.image(source=f"assets/{blog_post.thumbnail}").classes("w-32")
                        ui.label(f"By {blog_post.author} on {blog_post.timestamp}").classes("italic")

# Redirect from "/post" to "/"
@ui.page("/post")
def post():
    return RedirectResponse(url="/")


# Define the "/categories" page
@ui.page("/categories")
def categories() -> None:
    with layout("/categories"):
        ui.label("Categories").classes("text-2xl font-bold")
        for category, count in sorted(CATEGORIES.items()):
            ui.link(text=f"{category} ({count})", target=f"/categories/{category}")


# Define a dynamic route for "/categories/{category}"
@router.page("/categories/{category}")
async def category(category: str, client: Client) -> None:
    await client.connected()
    pathname = await ui.run_javascript("window.location.pathname;")
    found = False
    with layout(pathname):
        ui.label(f"Category {category}").classes("text-2xl font-bold")
        for link, blog_post in sorted(POSTS.items()):
            if category in blog_post.category:
                found = True
                ui.link(text=blog_post.title, target=f"/post/{link}")
        if not found:
            ui.chat_message(text="There are no blog entries with that category")


# Define the "/authors" page
@ui.page("/authors")
def authors() -> None:
    with layout("/authors"):
        ui.label("These are our lovely authors:").classes("text-2xl font-bold")
        with ui.element("div").classes("text-center items-center"):
            with ui.grid(columns=2).classes("w-full"):
                for author in AUTHORS:
                    with ui.column():
                        ui.label(author).classes("font-bold text-2xl text-center align-center")
                        with ui.link(target=f"/authors/{author}"):
                            ui.image(f"/assets/{author}.png").classes("w-64")


# Define a dynamic route for "/authors/{name}"
@router.page("/authors/{name}")
async def author(name: str, client: Client) -> None:
    await client.connected()
    pathname = await ui.run_javascript("window.location.pathname;")
    with layout(pathname):
        ui.label(f"About {name}").classes("text-2xl font-bold")
        if name not in AUTHORS:
            ui.chat_message("There is no known author with this name")
        else:
            ui.image(f"/assets/{name}.png").classes("w-64")
            ui.markdown(content=AUTHORS[name])
            ui.label(f"Blog posts by {name}").classes("text-2xl font-bold")
            for link, blog_post in sorted(POSTS.items()):
                if blog_post.author == name:
                    ui.link(text=blog_post.title, target=f"/post/{link}")


# Define a dynamic route for "/post/{title}"
@router.page("/post/{title}")
async def posts(title: str, client: Client) -> None:
    await client.connected()
    pathname = await ui.run_javascript("window.location.pathname;")
    with layout(pathname):
        if not title in POSTS:
            ui.chat_message(text="This page does not exist... Go back to the main page.")
            ui.link(text="Main page", target="/")
        else:
            with ui.element("div").classes("content").classes("w-full"):
                blog_post = POSTS[title]
                ui.add_head_html(f"""<meta name="description" content="{blog_post.summary}">""")
                ui.label(blog_post.title).classes("text-2xl font-bold")
                with ui.label(f"Created on {blog_post.timestamp} by ").classes("italic"):
                    ui.link(text=blog_post.author, target=f"/authors/{blog_post.author}")
                ui.image(source=f"assets/{blog_post.thumbnail}").classes("w-96")
                ui.markdown(content=blog_post.content).classes("mt-4")
                ui.element("hr").classes("mt-4 mb-4")
                ui.label("Categories").classes("font-bold")
                with ui.row():
                    for category in blog_post.category:
                        ui.link(text=f"#{category}", target=f"/categories/{category}")


# Run the UI application
if __name__ in {'__main__', '__mp_main__'}:
    # Initialize data on script execution
    init()
    app.include_router(router)
    ui.run(dark=True, storage_secret=os.urandom(128))