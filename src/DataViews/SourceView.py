# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2006  Donald N. Allingham
# Copyright (C) 2008       Gary Burton
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

# $Id$

"""
Source View
"""

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import gen.lib
import Config
from gui.views.listview import ListView
import DisplayModels
import Utils
import Bookmarks
import Errors
from DdTargets import DdTargets
from QuestionDialog import ErrorDialog
from Editors import EditSource, DelSrcQuery
from Filters.SideBar import SourceSidebarFilter

#-------------------------------------------------------------------------
#
# internationalization
#
#-------------------------------------------------------------------------
from gettext import gettext as _


#-------------------------------------------------------------------------
#
# SourceView
#
#-------------------------------------------------------------------------
class SourceView(ListView):

    COLUMN_NAMES = [
        _('Title'),
        _('ID'),
        _('Author'),
        _('Abbreviation'),
        _('Publication Information'),
        _('Last Changed'),
        ]
    
    ADD_MSG = _("Add a new source")
    EDIT_MSG = _("Edit the selected source")
    DEL_MSG = _("Delete the selected source")
    FILTER_TYPE = "Source"

    def __init__(self, dbstate, uistate):

        signal_map = {
            'source-add'     : self.row_add,
            'source-update'  : self.row_update,
            'source-delete'  : self.row_delete,
            'source-rebuild' : self.object_build,
            }

        self.func_list = {
            '<CONTROL>J' : self.jump,
            '<CONTROL>BackSpace' : self.key_delete,
            }

        ListView.__init__(
            self, _('Sources'), dbstate, uistate, 
            SourceView.COLUMN_NAMES, len(SourceView.COLUMN_NAMES), 
            DisplayModels.SourceModel, signal_map,
            dbstate.db.get_source_bookmarks(),
            Bookmarks.SourceBookmarks, multiple=True,
            filter_class=SourceSidebarFilter)

        Config.client.notify_add("/apps/gramps/interface/filter",
                                 self.filter_toggle)

    def column_ord_setfunc(self, clist):
        self.dbstate.db.set_source_column_order(clist)

    def get_bookmarks(self):
        return self.dbstate.db.get_source_bookmarks()

    def drag_info(self):
        return DdTargets.SOURCE_LINK
    
    def define_actions(self):
        ListView.define_actions(self)
        self._add_action('ColumnEdit', gtk.STOCK_PROPERTIES,
                         _('_Column Editor'), callback=self._column_editor)
        self._add_action('FastMerge', None, _('_Merge'),
                         callback=self.fast_merge)
        self._add_action('FilterEdit', None, _('Source Filter Editor'),
                         callback=self.filter_editor,)

    def _column_editor(self, obj):
        import ColumnOrder

        ColumnOrder.ColumnOrder(
            _('Select Source Columns'),
            self.uistate,
            self.dbstate.db.get_source_column_order(),
            SourceView.COLUMN_NAMES,
            self.set_column_order)

    def column_order(self):
        return self.dbstate.db.get_source_column_order()

    def get_stock(self):
        return 'gramps-source'

    def ui_definition(self):
        return '''<ui>
          <menubar name="MenuBar">
            <menu action="FileMenu">
              <placeholder name="LocalExport">
                <menuitem action="ExportTab"/>
              </placeholder>
            </menu>
            <menu action="BookMenu">
              <placeholder name="AddEditBook">
                <menuitem action="AddBook"/>
                <menuitem action="EditBook"/>
              </placeholder>
            </menu>
            <menu action="EditMenu">
              <placeholder name="CommonEdit">
                <menuitem action="Add"/>
                <menuitem action="Edit"/>
                <menuitem action="Remove"/>
              </placeholder>
              <menuitem action="ColumnEdit"/>
              <menuitem action="FilterEdit"/>
              <placeholder name="Merge">
                <menuitem action="FastMerge"/>
              </placeholder>
            </menu>
          </menubar>
          <toolbar name="ToolBar">
            <placeholder name="CommonEdit">
              <toolitem action="Add"/>
              <toolitem action="Edit"/>
              <toolitem action="Remove"/>
            </placeholder>
          </toolbar>
          <popup name="Popup">
            <menuitem action="Add"/>
            <menuitem action="Edit"/>
            <menuitem action="Remove"/>
          </popup>
        </ui>'''

    def add(self, obj):
        EditSource(self.dbstate, self.uistate, [], gen.lib.Source())

    def remove(self, obj):
        self.remove_selected_objects()

    def remove_object_from_handle(self, handle):
        the_lists = Utils.get_source_referents(handle, self.dbstate.db)
        object = self.dbstate.db.get_source_from_handle(handle)
        query = DelSrcQuery(self.dbstate, self.uistate, object, the_lists)
        is_used = any(the_lists)
        return (query, is_used, object)

    def edit(self, obj):
        for handle in self.selected_handles():
            source = self.dbstate.db.get_source_from_handle(handle)
            try:
                EditSource(self.dbstate, self.uistate, [], source)
            except Errors.WindowActiveError:
                pass

    def fast_merge(self, obj):
        mlist = self.selected_handles()
        
        if len(mlist) != 2:
            msg = _("Cannot merge sources.")
            msg2 = _("Exactly two sources must be selected to perform a merge. "
                     "A second source can be selected by holding down the "
                     "control key while clicking on the desired source.")
            ErrorDialog(msg, msg2)
        else:
            import Merge
            Merge.MergeSources(self.dbstate, self.uistate, mlist[0], mlist[1])

    def get_handle_from_gramps_id(self, gid):
        obj = self.dbstate.db.get_source_from_gramps_id(gid)
        if obj:
            return obj.get_handle()
        else:
            return None
