![http://pyslimp3.googlecode.com/svn/wiki/ArtistListBrowser.jpg](http://pyslimp3.googlecode.com/svn/wiki/ArtistListBrowser.jpg)

# Introduction #

The ArtistListBrowser class allows the user to browse a set of Artist objects. The display shows the artist name (**Aimee Mann**) on the first line, and the album count (**2**) for the artist, artist index (**3**) and total artist count (**284**) on the second.

## Keys Supported ##

| UP | Show the next artist in the collection |
|:---|:---------------------------------------|
| DOWN | Show the previous artist in the collection |
| RIGHT | Show an AlbumListBrowser for the albums associated with the current artist |
| LEFT | Return to the parent level and display |
| REC | Append all of the tracks of all of the albums for the current artist to the target playlist |
| PLAY | Play all of the tracks of the albums of the current artist, starting with the first track |