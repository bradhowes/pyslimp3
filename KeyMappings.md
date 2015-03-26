<table cellspacing='15'>
<tr>
<td><img src='http://pyslimp3.googlecode.com/svn/wiki/RMV201.png' /></td>
<td>
<h1>Introduction</h1>
The following maps refer to the keys found on the original SLiMP3 remote control from Sony (model RMV201). I don't know if the SlimDevices remote operates with the same key codes or functionality. So, your results may vary.<br>
<br>
<h2>Always Available Keys</h2>

<table><thead><th> <b>Key</b> </th><th> <b>Description</b> </th></thead><tbody>
<tr><td> MENU </td><td> Shows the top-level browser menu </td></tr>
<tr><td> DISP </td><td> Shows the playback display if possible. If already showing the playback display, this button will cycle through the various track info displays </td></tr>
<tr><td> VOL+ </td><td> Increases iTunes volume </td></tr>
<tr><td> VOL- </td><td> Decreases iTunes volume </td></tr>
<tr><td> CH+ </td><td> Increases the SLiMP3 brightness </td></tr>
<tr><td> CH- </td><td> Decreases the SLiMP3 brightness </td></tr>
<tr><td> MUTING </td><td> Toggle iTunes mute setting </td></tr>
<tr><td> OK </td><td> Toggle shuffling mode for current playlist </td></tr>
<tr><td> RECALL </td><td> Cycle repeat mode for current playlist (off, all, song) </td></tr>
<tr><td> POWER </td><td> Toggle SLiMP3 "power", where ON allows iTunes control and OFF shows the current date/time. </td></tr>
<tr><td> SLEEP </td><td> Enable the screen saver. If enabled, and button press will disable it. </td></tr>
<tr><td> REC </td><td> Show the current "target" playlist if not showing an artist, album, or track browswer. Otherwise, add the artist, album or track to the "target" playlist. </td></tr>
<tr><td> STOP </td><td> Stop iTunes playback and rewind to the start of the current track. </td></tr>
<tr><td> PAUSE</td><td> Stop iTunes playback and leave the playback position alone. </td></tr></tbody></table>

</td>
</tr>
</table>

## DisplayGenerator ##

| **Key** | **Description** |
|:--------|:----------------|
| LEFT | Exit the current browser and show a prior higher-level browser display |

## PlaybackDisplay ##

Inherits from [#DisplayGenerator](#DisplayGenerator.md).

| **Key** | **Description** |
|:--------|:----------------|
| UP | Show the next track in the active playlist |
| DOWN | Show the previous track in the active playlist |
| RIGHT | Show a ratings editor for the current track |
| PIP | Show a ratings editor for the current track |
| PLAY | Begin/resume playing the current track |
| RWD | Rewind the playback position when held down, otherwise move to the previous track. |
| FFWD | Fast-forward the playback position when held down, otherwise move to the next track. |
| DISP | Cycle through the various track info displays: track index (eg. 3/10); elapsed time (eg. +0:23); remaining time (eg -3:33); track duration (eg: 4:56); and blank |

## TextEntry ##

Inherits from [#DisplayGenerator](#DisplayGenerator.md)

| **Key** | **Description** |
|:--------|:----------------|
| UP | cycle the current character to the next value |
| DOWN | cycle the current character to the previous value |
| RIGHT | move to the next character position. Twice in a row will validate and accept the text entry |
| OK | Validate and accept the text entry |
| 1 | cycle through the characters 1,2,3,4,5,6,7,8,9,0 |
| 2 | cycle through the characters A,B,C,2 |
| 3 | cycle through the characters D,E,F,3 |
| 4 | cycle through the characters G,H,I,4 |
| 5 | cycle through the characters J,K,L,5 |
| 6 | cycle through the characters M,N,O,6 |
| 7 | cycle through the characters P,Q,R,S,7 |
| 8 | cycle through the characters T,U,V,8 |
| 9 | cycle through the characters W,X,Y,Z,9 |

## RatingDisplay ##

Inherits from [#DisplayGenerator](#DisplayGenerator.md).

| **Key** | **Description** |
|:--------|:----------------|
| PIP | show the display that was active prior to this one (same as LEFT) |
| UP | increase the rating of the current item |
| DOWN | decrease the rating of the current item |
| 0-5 | set the rating to 20x the digit pressed (0-100). If the same digit is pressed twice in a row, add 10 to the current rating (half-star) |

## TrackRatingDisplay ##

Inherits from [#RatingDisplay](#RatingDisplay.md).

| **Key** | **Description** |
|:--------|:----------------|
| PIP | Show a ratings editor for the album of the current track |
| RIGHT | Show a ratings editor for the album of the current track |

## [Browser](Browser.md) ##

Inherits from [#DisplayGenerator](#DisplayGenerator.md).

| **Key** | **Description** |
|:--------|:----------------|
| UP | Show the next element in the browser collection |
| DOWN | show the previous element in the browser collection |
| RIGHT | show a more-detailed (child) display |
| 0-9 | if there are 10 items or less, treat the digit as an index (0 being 10) and show that item in the browser. Otherwise, treat the digit in a manner similar to that of TextEntry, where a digit maps to the letters of a telephone keypad. This letter is then used in a binary search of the items being browsed, and the first entry found that starts with that character is then shown. |

## ChoiceSetting ##

Inherits from [#Browser](#Browser.md).

| **Key** | **Description** |
|:--------|:----------------|
| RIGHT | Use the current value as the value of a particular setting |
| OK | Use the current value as the value of a particular setting |

## PlaylistBrowser ##

Inherits from [#Browser](#Browser.md).

| **Key** | **Description** |
|:--------|:----------------|
| PLAY | start playing the first track in the current playlist |
| REC | create a new playlist |
| 0 (zero) | clear the current playlist if it contains tracks, or delete it if it is empty |
| OK | Make the current playlist the "target" playlist for REC operations. If it is already the "target" playlist, make MBJB the target playlist |

## PlayableBrowser ##

Inherits from [#Browser](#Browser.md).

| **Key** | **Description** |
|:--------|:----------------|
| REC | add the browsed collection to the target playlist |
| PLAY | copy the browsed collection to the MBJB playlist and begin playback |

## AlbumListBrowser ##

Inherits from [#PlayableBrowser](#PlayableBrowser.md).

| **Key** | **Description** |
|:--------|:----------------|
| PIP | Show a ratings editor for the current album. |

## TrackListBrowser ##

Inherits from [#PlayableBrowser](#PlayableBrowser.md).

| **Key** | **Description** |
|:--------|:----------------|
| PIP | show a ratings editor for the current track |
| RIGHT | show a ratings editor for the current track |