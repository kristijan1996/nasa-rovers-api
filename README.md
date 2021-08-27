NASA rover image query
======================

This project is based on requirements from https://github.com/igno/nasa-images.
It uses Python to query NASA's servers in order to extract photos from different
rovers that are on Mars, and different cameras they are equiped with. Program
also implements a caching layer in order not to violate NASA's requests-per-hour
restrictions, and store server responses that have already been queried.
