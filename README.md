# button-finder
Button Finder is a tool for finding 88x31 buttons on neocities sites.

# How it works
1. Use python's `requests` library to fetch the html of a page.
2. Use the `beautifulsoup4` library to extract links and images from the html.
3. Look for images that are 88x31.
4. Repeat for all links that haven't already been visited and belong to the same domain* (depth-first search).
*This isn't exactly how it works but is close enough.

# Setup
1. Download the repository.
2.
  - If you have conda/miniconda installed, create a conda environment for the repository based on `environment.yml`.
  - If you don't have those, just install the packages listed in `environment.yml` through pip or similar.
3. Run `button-finder.py`.
