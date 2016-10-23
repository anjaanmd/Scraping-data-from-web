for d in ./2*/ ; do (cd "$d" && python scraper.py *.html); done
