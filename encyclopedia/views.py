import random as rand

import markdown2
from django.shortcuts import redirect, render

from . import util


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def entry(request, title):
    content = util.get_entry(title)

    if content is None:
        return render(request, "encyclopedia/error.html", {
            "title": title
        }, status=404)

    return render(request, "encyclopedia/entry.html", {
        "title": title,
        "content": markdown2.markdown(content)
    })


def search(request):
    query = request.GET.get("q", "").strip()
    entries = util.list_entries()

    # Exact (case-insensitive) match -> go straight to the entry page.
    for entry_name in entries:
        if query and entry_name.lower() == query.lower():
            return redirect("entry", title=entry_name)

    # Otherwise show every entry that contains the query as a substring.
    results = [e for e in entries if query.lower() in e.lower()] if query else []

    return render(request, "encyclopedia/search.html", {
        "query": query,
        "results": results
    })


def new_page(request):
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        content = request.POST.get("content", "")

        if not title:
            return render(request, "encyclopedia/new.html", {
                "error": "Please provide a title.",
                "content": content
            })

        if util.get_entry(title) is not None:
            return render(request, "encyclopedia/new.html", {
                "error": f'An entry titled "{title}" already exists.',
                "title": title,
                "content": content
            })

        util.save_entry(title, content)
        return redirect("entry", title=title)

    return render(request, "encyclopedia/new.html")


def edit(request, title):
    content = util.get_entry(title)

    if content is None:
        return render(request, "encyclopedia/error.html", {
            "title": title
        }, status=404)

    if request.method == "POST":
        new_content = request.POST.get("content", "")
        util.save_entry(title, new_content)
        return redirect("entry", title=title)

    return render(request, "encyclopedia/edit.html", {
        "title": title,
        "content": content
    })


def random_page(request):
    entries = util.list_entries()
    if not entries:
        return redirect("index")
    return redirect("entry", title=rand.choice(entries))
