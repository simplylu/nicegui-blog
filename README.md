# NiceBlog - A simple sample blog application using NiceGUI
This is just a simple explanation on how to work with this piece of NiceGUI code. Using markdown and NiceGUI it is easy to create a simple blog in less time. The focus was on simplicity, not design. So just change the color theme in the `.env` file or the tailwind classes in the code itself. You may not touch the logic on how to parse Posts into the system, as it is easy to break things here. Everything else should be self explanatory and is no magic, since every information that was needed to create this was taken from official NiceGUI samples or the NiceGUI documentation.

## Create a blog post

New posts need to be stored in `./posts` and follow the below structure:

> timestamp = The timestamp
>
> author = your name
>
> category = comma,separated,categories
>
> title = A promising title
>
> summary = SEO summary that will be put into a meta description tag
>
> thumbnail = name of the thumbnail image that needs to be stored in ./assets
>
> published = True if this should be shown, False if not
>
> 
> \-\-\-
>
> 
> Your markdown content goes here.

Your markdown content goes below the three dashes. This is the part that will be rendered. The above metadata is just for the system to recognize the article, etc.

The app needs then to be reloaded to recognize changes or new posts.

New posts will appear on the index page, in the profile of the author of that post, or in the respective category. The link consists of the title which was quoted to make it URL safe.

## Authors
To have the authors properly shown in the blog, you need to create a `name.md` file in the `./authors` directory, as well as a `name.png` file in the `./assets` directory. The name needs to be the same as in the author variable in the post metadata to make it all work.


## General
Just check the existing config / directories and you'll see how it works. The code is no magic itself, it's just a basic sample on how to utilize NiceGUI and markdown to create a simple blog.

To run this sample, just call `python3 app.py` from your Terminal.