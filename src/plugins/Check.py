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

"Database Processing/Check and repair database"

import RelLib
import utils
import intl
_ = intl.gettext

import os

import gnome.ui
import libglade

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def runTool(database,active_person,callback):

    checker = CheckIntegrity(database)
    checker.check_for_broken_family_links()
    checker.cleanup_missing_photos()
    checker.check_parent_relationships()
    checker.cleanup_empty_families(0)
    checker.report()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------

class CheckIntegrity:
    
    #-------------------------------------------------------------------------
    #
    #
    #
    #-------------------------------------------------------------------------
    def __init__(self,db):
        self.db = db
        self.bad_photo = []
        self.empty_family = []
        self.broken_links = []
        self.fam_rel = []

    #-------------------------------------------------------------------------
    #
    #
    #
    #-------------------------------------------------------------------------
    def check_for_broken_family_links(self):
        self.broken_links = []
        family_list = self.db.getFamilyMap().values()[:]
        for family in family_list:
            for child in family.getChildList():
                if family == child.getMainFamily():
                    continue
                for family_type in child.getAltFamilyList():
                    if family_type[0] == family:
                        break
                else:
                    family.removeChild(child)
                    utils.modified()
                    self.broken_links.append((child,family))

    #-------------------------------------------------------------------------
    #
    #
    #
    #-------------------------------------------------------------------------
    def cleanup_missing_photos(self):
        for photo in self.db.getObjectMap().values():
            if not os.path.isfile(photo.getPath()):
                self.bad_photo.append(photo)

    #-------------------------------------------------------------------------
    #
    #
    #
    #-------------------------------------------------------------------------
    def cleanup_empty_families(self,automatic):

        family_list = self.db.getFamilyMap().values()[:]
        for family in family_list:
            if family.getFather() == None and family.getMother() == None:
                utils.modified()
                self.empty_family.append(family)
                self.delete_empty_family(family)

    def delete_empty_family(self,family):
        for child in self.db.getPersonMap().values():
            if child.getMainFamily() == family:
                child.setMainFamily(None)
            else:
                child.removeAltFamily(family)
        self.db.deleteFamily(family)

    #-------------------------------------------------------------------------
    #
    #
    #
    #-------------------------------------------------------------------------
    def check_parent_relationships(self):

        for family in self.db.getFamilyMap().values():
            father = family.getFather()
            mother = family.getMother()
            type = family.getRelationship()

            if father == None or mother == None:
                continue
            if type != "Partners":
                if father.getGender() == mother.getGender():
                    family.setRelationship("Partners")
                    self.fam_rel.append(family)
                elif father.getGender() != RelLib.Person.male or \
                     mother.getGender() != RelLib.Person.female:
                    family.setFather(mother)
                    family.setMother(father)
                    self.fam_rel.append(family)
            else:
                if father.getGender() != mother.getGender():
                    family.setRelationship("Unknown")
                    self.fam_rel.append(family)
                    if father.getGender() == RelLib.Person.female:
                        family.setFather(mother)
                        family.setMother(father)

    #-------------------------------------------------------------------------
    #
    #
    #
    #-------------------------------------------------------------------------
    def report(self):
        photos = len(self.bad_photo)
        efam = len(self.empty_family)
        blink = len(self.broken_links)
        rel = len(self.fam_rel)
        
        errors = blink + efam + photos + rel
        
        if errors == 0:
            gnome.ui.GnomeOkDialog(_("No errors were found"))
            return

        text = ""
        if blink > 0:
            if blink == 1:
                text = text + _("1 broken family link was fixed\n")
            else:
                text = text + _("%d broken family links were found\n") % blink
            for c in self.broken_links:
                cn = c[0].getPrimaryName().getName()
                f = c[1].getFather()
                m = c[1].getMother()
                if f and m:
                    pn = _("%s and %s") % (f.getPrimaryName().getName(),\
                                           m.getPrimaryName().getName())
                elif f:
                    pn = f.getPrimaryName().getName()
                else:
                    pn = m.getPrimaryName().getName()
                text = text + '\t' + \
                       _("%s was removed from the family of %s\n") % (cn,pn)
        if efam == 1:
            text = text + _("1 empty family was found\n")
        elif efam > 1:
            text = text + _("%d empty families were found\n") % efam
        if rel == 1:
            text = text + _("1 corrupted family relationship fixed\n")
        elif rel > 1:
            text = text + _("%d corrupted family relationship fixed\n") % rel
        if photos == 1:
            text = text + _("1 media object was referenced, but not found\n")
        elif photos > 1:
            text = text + _("%d media objects were referenced, but not found\n") % photos

        base = os.path.dirname(__file__)
        glade_file = base + os.sep + "summary.glade"
        topDialog = libglade.GladeXML(glade_file,"summary")
        topDialog.signal_autoconnect({
            "destroy_passed_object" : utils.destroy_passed_object,
            })
        title = _("Check Integrity")
        top = topDialog.get_widget("summary")
        textwindow = topDialog.get_widget("textwindow")
        topDialog.get_widget("summaryTitle").set_text(title)
        textwindow.show_string(text)
        top.show()

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
from Plugins import register_tool

register_tool(
    runTool,
    _("Check and repair database"),
    category=_("Database Processing"),
    description=_("Checks the database for integrity problems, fixing the problems that it can")
    )
    
