![http://pyslimp3.googlecode.com/svn/wiki/TrackRating.jpg](http://pyslimp3.googlecode.com/svn/wiki/TrackRating.jpg)

# Introduction #

Derived from RatingDisplay.

The TrackRatingDisplay class allows the user to view and edit the iTunes rating of a track. The UP and DOWN arrow keys change the rating. Also, the numbers 0 - 5 may be used to specify a rating; pressing the digit a second time will increase the rating by 1/2.

> <b>NOTE:</b> this is derived from the OverlayDisplay class, so it will automatically revert to the previous display after 3 seconds of inactivity by the user.

# Keys Supported #

| UP | Increase the rating |
|:---|:--------------------|
| DOWN | Decrease the rating |
| 0-5 | Set the rating that corresponds to the digit |
| RIGHT, PIP | Show an AlbumRatingDisplay screen to view and edit the rating for the album containing the track |
| LEFT | Return to the parent level and display |