#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000  Donald N. Allingham
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

"Names with same SoundEx code as ..."

import Filter
import soundex
import RelLib

class MatchSndEx(Filter.Filter):
    "Names with same SoundEx code as ..."

    def __init__(self,text,invert):
        self.sndex = soundex.soundex(text)
        Filter.Filter.__init__(self,text)
        
    def match(self,person):
        return self.sndex == soundex.soundex(person.getPrimaryName().getSurname())

def create(text):
    return MatchSndEx(text)

def need_qualifier():
    return 1
