# BSUIR timetable analysis util

```
usage: main.py [-h] [--output OUTPUT] [--skip-check] [--action ACTION]
               cache-path

positional arguments:
  cache-path       path to the cache of a timetable

optional arguments:
  -h, --help       show this help message and exit
  --output OUTPUT  path to the output file, default is <action>.json
  --skip-check     skip loading a timetable, use cache
  --action ACTION  script to run against built info, default is "represent"
```