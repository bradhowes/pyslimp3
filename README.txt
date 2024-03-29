Pyslimp3: the Python SLiMP3-iTunes Interface
--------------------------------------------

The original SLiMP3 device from SlimDevices (now Logitech) provided a nice,
compact interface for accessing and playing a collection of MP3 music files on
a computer. One would connect the device to the network, install and start the
included server software on a computer, and connect the SLiMP3 device to an
audio system. Using a provided remote control, one could browse a music library
and control music playback, all without having to physically be at the computer
hosting the music.

I had one of the first SLiMP3 devices. I thought it was a great piece of
engineering for its time, and it met a need I had, namely how to access my
music collection without having to be in a room with a computer. In 2009, I
finally decided that as much as I liked the SLiMP3 device, I was growing weary
of the included server software, especially with having to transcode Apple's
iTunes Store files into the MP3 format so that the SLiMP3 device could
understand the bit stream. As an alternative, I envisioned using the SLiMP3 and
its remote conntrol as a means by which I could programmatically control the
iTunes application running on my G4 Mac Mini that hosted all of my music files.
And so, Pyslimp3 was born.


Project Info
------------

All of the Pyslimp3 source is released under the GPL (Version 3). Its project
home is at http://code.google.com/p/pyslimp3/. Though I have written all of the
code myself, I have relied on SlimDevices documentation and Perl code for
guidance on how to interact with the SLiMP3 device. All of the screens
generated by the Python code for display on the SLiMP3 device are my own
creation, though the top-level menu borrows heavily from that found in the
SlimDevices code. Many of the remote control keys operate in a similar manner,
though there are notable differences. Currently documentation on screen
operations and key functionality is sorely lacking.


Installation
------------

You need Apple's iTunes application.

You need to have Python installed. I do most of my testing and development
using Python 2.5.1 on an Apple MacBook Pro.

You also need to install the appscript Python library that provides a wonderful
bridge between Python and AppleScript. Keep in mind that working with
AppleScript from inside Python can be a bit of an arcane science.

Finally, you need a SLiMP3 device. I only have the original version, so I
cannot say whether the software would work with other SlimDevices (I would
guess not).


Running
-------

To run the server:

    % python Server.py

To run the basic simulator:

    % python sim.py

There is a graphical simulator now that requires Nokia's Qt library. It is
found in the qtsim directory. See qtsim/README for more information.
