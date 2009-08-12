#
# Copyright (C) 2009 Brad Howes.
#
# This file is part of Pyslimp3.
#
# Pyslimp3 is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation; either version 3, or (at your option) any later version.
#
# Pyslimp3 is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# Pyslimp3; see the file COPYING. If not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301,
# USA.
#

from KeyProcessor import *

remoteId = 0x0

#
# These values were obtained from Logitech's SLIMP3_Server_v3.1b5/IR/jvc_dvd.ir
# file.
#
mapping = {
    0x0000f776 : kDigit0,
    0x0000f786 : kDigit1,
    0x0000f746 : kDigit2,
    0x0000f7c6 : kDigit3,
    0x0000f726 : kDigit4,
    0x0000f7a6 : kDigit5,
    0x0000f766 : kDigit6,
    0x0000f7e6 : kDigit7,
    0x0000f716 : kDigit8,
    0x0000f796 : kDigit9,
    0x0000f78b : kArrowDown,
    0x0000f74b : kArrowLeft,
    0x0000f7cb : kArrowRight,
    0x0000f70b : kArrowUp,
    0x0000f70e : kRewind,
    0x0000f76e : kFastForward,
    0x0000f78d : kChannelDown,  # this is CH- on this remote
    0x0000f70d : kChannelUp,    # this is CH+ on this remote
    0x0000f703 : kDisplay,      # this is the DISP button this remote
    0x0000f7b6 : kGuide,        # this is the GUIDE button on this remote
    0x0000f783 : kMenuHome,
    0x0000c038 : kMute,
    0x0000c538 : kMute,
    0x0000f72b : kShuffle,
    0x0000f7b2 : kPause,
    0x0000f7f6 : kPIP,          # this is the PIP button on this remote
    0x0000f732 : kPlay,
    0x0000f7d6 : kPlay,
    0x0000f702 : kPower,
    0x0000f743 : kRecord,       # this is the REC button on this remote
    0x0000f7ab : kRepeat,       # this is the RECALL button on this remote
    0x0000f7b3 : kSleep,
    0x0000f7c2 : kStop,
    0x0000c0f8 : kVolumeDown,
    0x0000c5f8 : kVolumeDown,
    0x0000f7f8 : kVolumeDown,
    0x0000c078 : kVolumeUp,
    0x0000c578 : kVolumeUp,
    0x0000f778 : kVolumeUp,
    }
