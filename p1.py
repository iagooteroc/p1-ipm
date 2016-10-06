
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import locale
import gettext
import os

locale.setlocale(locale.LC_ALL,'')
LOCALE_DIR = os.path.join(os.path.dirname(__file__), "locale")
locale.bindtextdomain('p1', LOCALE_DIR)
gettext.bindtextdomain('p1', LOCALE_DIR)
gettext.textdomain('p1')
_ = gettext.gettext
N_ = gettext.ngettext

class FilmFile():
    def getFilmList(fileName):
        filmList = []
        f = open(fileName)
        for line in f:
            name, date, rating, state = line.split('//')
            filmList.append([name,date,rating, state[:-1]])
        f.close()
        return filmList
    
    def writeFilmList(fileName, filmList):
        f = open(fileName, 'w')
        list_iter = filmList.get_iter_first()
        while list_iter is not None:
            name = filmList.get_value(list_iter, 0)
            date = filmList.get_value(list_iter, 1)
            rating = filmList.get_value(list_iter, 2)
            state = filmList.get_value(list_iter, 4)
            f.write((name + '//' + date + '//' + rating + '//' + state + '\n'))
            list_iter = filmList.iter_next(list_iter)
        f.close()

class AppActions():
    def on_add_clicked(widget, parent):
        dialogAdd = Gtk.Dialog(_("Add"), parent,
		                              Gtk.DialogFlags.MODAL,
		                              (_("OK"), Gtk.ResponseType.OK,
		                              _("Cancel"), Gtk.ResponseType.CANCEL))
        dialogAdd = DialogAdd(parent)
        response = dialogAdd.run()
        name = dialogAdd.entryName.get_text()
        date = dialogAdd.entryDate.get_text()
        rating = dialogAdd.entryRating.get_text()
        dialogAdd.destroy()
        
        if (response == Gtk.ResponseType.OK):
                if (name != '') and (date != '') and (rating != ''):
                    AppActions.add_film(parent, widget, name, date, rating)
                else:
                    AppActions.error_dialog_blank(parent)

    def add_film(parent, widget, name, date, rating):
        model = parent.filmModel.get_model()
        model.append(list((name, date, rating, False, "0")))

    def on_edit_clicked(widget, parent):
        selection = parent.treeview.get_selection()
        model, iter = selection.get_selected()
        if iter is not None:
            dialogEdit = DialogEdit(parent, model, iter)
            response = dialogEdit.run()
            newName = dialogEdit.entryName.get_text()
            newDate = dialogEdit.entryDate.get_text()
            newRating = dialogEdit.entryRating.get_text()
            dialogEdit.destroy()
            if (response == Gtk.ResponseType.OK):
                if (newName != '') and (newDate != '') and (newRating != ''):
                    AppActions.edit_film(parent, widget, newName, newDate, newRating, iter)
                else:
                    AppActions.error_dialog_blank(parent)
                    
    def edit_film(parent, widget, name, date, rating, iter):
        parent.filmModel.set_value(iter, 0, name)
        parent.filmModel.set_value(iter, 1, date)
        parent.filmModel.set_value(iter, 2, rating)
        
    def on_remove_clicked(widget, parent):
        selection = parent.treeview.get_selection()    # TreeSelection
        filmModel, iter = selection.get_selected()     # TreeModelFilter, iter
        pathList = selection.get_selected_rows() # GList with paths from TreeModelFilter
        firstPath = pathList[0]    # WHY THE FUCK IS PATHLIST A TUPLE
        #path = pathList.first()  # TreePath IT SHOULD BE
        # WHAT THE FUCK IS GI.OVERRIDES.GTK.TREEMODELFILTER AND WHY FIRSTPATH IS THAT AND NOT A TREEPATH
        path = filmModel.convert_path_to_child_path(firstPath) # path from TreeModel (ListStore?)
        model = filmModel.get_model()    # TreeModel or ListStore?
        model.get_iter(iter, path)    # iter from TreeModel
        if iter is not None:
            text = model.get_value(iter,0)
            warning = DialogWarning(parent, text)
            response = warning.run()
            
            if response == Gtk.ResponseType.OK:
                model.remove(iter)
            warning.destroy()
            
    def error_dialog_blank(parent):
        dialogError = Gtk.MessageDialog(parent, 0, Gtk.MessageType.ERROR,
            Gtk.ButtonsType.OK, _("You must fill in all the fields"))
        dialogError.run()
        dialogError.destroy()
    
    def on_cell_toggled(widget, path, parent):
        parent.filmModel[path][3] = not parent.filmModel[path][3]

    def on_combo_changed(combo, parent):
        treeIter = combo.get_active_iter()
        model = combo.get_model()
        parent.filmModel.refilter()
        print(model[treeIter][0])


class AppWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title=_("Film list"))
        self.set_border_width(10)
        self.resize(400, 300)
        self.set_position(Gtk.WindowPosition.CENTER)

        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.inbox = Gtk.Box()
        self.add(self.box)
        
        # Creating the filterCombo
        self.filterCombo = Gtk.ComboBoxText()
        self.filterCombo.connect("changed", AppActions.on_combo_changed, self)
        self.filterCombo.set_entry_text_column(0)
        
        # Adding the filter names
        filters = ["All movies", "Seen", "Plan to watch"]
        for filterName in filters:
            self.filterCombo.append_text(filterName)

        self.filterCombo.set_active(0)
        self.box.pack_start(self.filterCombo, False, True, 0)

        #Creating the filmListstore model
        self.filmListstore = Gtk.ListStore(str, str, str, bool, str)
        
        # Loading stored films
        filmList = FilmFile.getFilmList("films.txt")
        
        # Adding them into filmListstore
        for filmRef in filmList:
            filmValues = filmRef[:-1] # Name, Date, Rating
            filmValues.append(False)
            filmValues.append(filmRef[-1]) # Status
            print(filmValues)
            self.filmListstore.append(filmValues)

        self.filmModel = self.filmListstore.filter_new()
        self.filmModel.set_visible_func(self.film_filter_func)
        #creating the treeview and adding the columns
        self.treeview = Gtk.TreeView.new_with_model(self.filmModel)

        for i, columnTitle in enumerate([_("Name"),_("Date"),_("Rating")]):
            rendererText = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(columnTitle, rendererText, text=i)
            self.treeview.append_column(column)
            
        
        rendererToggle = Gtk.CellRendererToggle()
        rendererToggle.connect("toggled", AppActions.on_cell_toggled, self)
        columnToggle = Gtk.TreeViewColumn("Toggle", rendererToggle, active=3)
        self.treeview.append_column(columnToggle)
        
        
        #setting up the layout and putting the treeview in a scrollwindow
        self.scrollableTreelist = Gtk.ScrolledWindow()
        self.scrollableTreelist.set_vexpand(True)
        self.box.pack_start(self.scrollableTreelist, True, True, 0)
        self.scrollableTreelist.add(self.treeview)
        
        self.box.pack_start(self.inbox, False, True, 0)
        
        # Adding the Add button
        self.addButton = Gtk.Button.new_with_label(_("Add"))
        self.addButton.connect("clicked", AppActions.on_add_clicked, self)
        self.inbox.pack_start(self.addButton, True, True, 0)
        
        # Adding the Edit button
        self.editButton = Gtk.Button.new_with_label(_("Edit"))
        self.editButton.connect("clicked", AppActions.on_edit_clicked, self)
        self.inbox.pack_start(self.editButton, True, True, 0)
        
        # Adding the Remove button
        self.removeButton = Gtk.Button.new_with_label(_("Remove"))
        self.removeButton.connect("clicked", AppActions.on_remove_clicked, self)
        self.inbox.pack_start(self.removeButton, True, True, 0)

        self.connect("delete-event", self.app_quit)
        self.show_all()
            
    def film_filter_func(self, model, iter, data):
        print("Filtering...")
        treeIter = self.filterCombo.get_active_iter()
        comboModel = self.filterCombo.get_model()
        movieFilter = comboModel[treeIter][0]
        if (movieFilter == "All movies"):
            return True
        if (movieFilter == "Seen"):
            if (model.get_value(iter, 4) == "0"):
                return True
            else:
                return False
        if (movieFilter == "Plan to watch"):
            if (model[iter][4] == "1"):
                return True
        else:
            return False

    def app_quit(self, parent, widget):
        FilmFile.writeFilmList("films.txt", self.filmListstore)
        Gtk.main_quit()

class DialogEdit(Gtk.Dialog):
    def __init__(self, parent, model, iter):
        Gtk.Dialog.__init__(self, _("Edit"), parent, Gtk.DialogFlags.MODAL,
            (_("OK"), Gtk.ResponseType.OK,
             _("Cancel"), Gtk.ResponseType.CANCEL))
        box = self.get_content_area()
        
        label = Gtk.Label(_("Name:"))
        label.set_justify(Gtk.Justification.LEFT)
        box.pack_start(label, True, True, 0)
        
        self.entryName = Gtk.Entry()
        self.entryName.set_text(model.get_value(iter,0))
        box.pack_start(self.entryName, True, True, 0)
        
        label = Gtk.Label(_("Date:"))
        label.set_justify(Gtk.Justification.LEFT)
        box.pack_start(label, True, True, 0)
        
        self.entryDate = Gtk.Entry()
        self.entryDate.set_text(model.get_value(iter,1))
        box.pack_start(self.entryDate, True, True, 0)
            
        label = Gtk.Label(_("Rating:"))
        label.set_justify(Gtk.Justification.LEFT)
        box.pack_start(label, True, True, 0)
        
        self.entryRating = Gtk.Entry()
        self.entryRating.set_text(model.get_value(iter,2))
        box.pack_start(self.entryRating, True, True, 0)
        self.show_all()
        
class DialogAdd(Gtk.Dialog):
    def __init__(self, parent):
        Gtk.Dialog.__init__(self, _("Add"), parent, Gtk.DialogFlags.MODAL,
            (_("OK"), Gtk.ResponseType.OK,
             _("Cancel"), Gtk.ResponseType.CANCEL))
             
        box = self.get_content_area()
        
        label = Gtk.Label(_("Name:"))
        label.set_justify(Gtk.Justification.LEFT)
        box.pack_start(label, True, True, 0)
        
        self.entryName = Gtk.Entry()
        box.pack_start(self.entryName, True, True, 0)
        
        label = Gtk.Label(_("Date:"))
        label.set_justify(Gtk.Justification.LEFT)
        box.pack_start(label, True, True, 0)
        
        self.entryDate = Gtk.Entry()
        box.pack_start(self.entryDate, True, True, 0)
        self.show_all()
        
        label = Gtk.Label(_("Rating:"))
        label.set_justify(Gtk.Justification.LEFT)
        box.pack_start(label, True, True, 0)
        
        self.entryRating = Gtk.Entry()
        box.pack_start(self.entryRating, True, True, 0)
        self.show_all()

class DialogWarning(Gtk.Dialog):

    def __init__(self, parent, text):
        Gtk.Dialog.__init__(self, _("Warning"), parent, Gtk.DialogFlags.MODAL,
            (_("OK"), Gtk.ResponseType.OK,
             _("Cancel"), Gtk.ResponseType.CANCEL))

        self.set_default_size(150, 100)

        label = Gtk.Label(_("Are you sure you want to delete ''") + text+ "''?")

        box = self.get_content_area()
        box.add(label)
        self.show_all()


win = AppWindow()
Gtk.main()

