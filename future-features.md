1. Before fetching content for a given URL, check whether URL is already in the database. If it is, re-fetch the document and update the database.
2. Allow users to update a URL and re-fetch the document and update the database. (e.g. python recursive_url_loader.py --url https://docs.python.org/3/whatsnew/index.html --update)
3. Store docs for a given parent URL in a separate collection.
4. Allow users to delete a collection.
5. Allow users to delete a document.
6. Allow users to delete a parent URL, thus deleting its collection and all of its children.

Would you like me to implement a mechanism to:

1. Check if a URL has already been processed
2. Skip processing if it exists (unless explicitly told to update)
3. Optionally update existing entries instead of duplicating them?
