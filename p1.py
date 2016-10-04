
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class FilmFile():
    def getFilmList(fileName):
        filmList = []
        f = open(fileName)
        for line in f:
            name, date, rating = line.split('//')
            filmList.append([name,date,rating[:-1]])
        f.close()
        return filmList
    
    def writeFilmList(fileName, filmList):
        f = open(fileName, 'w')
        list_iter = filmList.get_iter_first()
        while list_iter is not None:
            name = filmList.get_value(list_iter, 0)
            date = filmList.get_value(list_iter, 1)
            rating = filmList.get_value(list_iter, 2)
            f.write((name + '//' + date + '//' + rating + '\n'))
            list_iter = filmList.iter_next(list_iter)
        f.close()

class AppActions():
    def on_add_clicked(widget, parent):
        dialogAdd = Gtk.Dialog("Add", parent,
		                              Gtk.DialogFlags.MODAL,
		                              ("OK", Gtk.ResponseType.OK,
		                              "Cancel", Gtk.ResponseType.CANCEL))
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
        parent.filmListstore.append(list((name, date, rating)))

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
        parent.filmListstore.set_value(iter, 0, name)
        parent.filmListstore.set_value(iter, 1, date)
        parent.filmListstore.set_value(iter, 2, rating)
        
    def on_remove_clicked(widget, parent):
        selection = parent.treeview.get_selection()
        model, iter = selection.get_selected()
        if iter is not None:
            text = model.get_value(iter,0)
            warning = DialogWarning(parent, text)
            response = warning.run()
            
            if response == Gtk.ResponseType.OK:
                model.remove(iter)
            warning.destroy()
            
    def error_dialog_blank(parent):
        dialogError = Gtk.MessageDialog(parent, 0, Gtk.MessageType.ERROR,
            Gtk.ButtonsType.OK, "You must fill in all the fields")
        dialogError.run()
        dialogError.destroy()

class AppWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Lista de peliculas")
        self.set_border_width(10)
        self.resize(400, 300)
        self.set_position(Gtk.WindowPosition.CENTER)

        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.inbox = Gtk.Box()
        self.add(self.box)

        #Creating the ListStore model
        self.filmListstore = Gtk.ListStore(str, str, str)
        
        # Loading stored films
        filmList = FilmFile.getFilmList("films.txt")
        
        # Adding them into filmListstore
        for filmRef in filmList:
            self.filmListstore.append(list(filmRef))

        #creating the treeview and adding the columns
        self.treeview = Gtk.TreeView.new_with_model(self.filmListstore)

        for i, columnTitle in enumerate(["Name","Date","Rating"]):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(columnTitle, renderer, text=i)
            self.treeview.append_column(column)
            

        #setting up the layout and putting the treeview in a scrollwindow
        self.scrollableTreelist = Gtk.ScrolledWindow()
        self.scrollableTreelist.set_vexpand(True)
        self.box.pack_start(self.scrollableTreelist, True, True, 0)
        self.scrollableTreelist.add(self.treeview)
        
        self.box.pack_start(self.inbox, False, True, 0)
        
        # Adding the Add button
        self.addButton = Gtk.Button.new_with_label("Add")
        self.addButton.connect("clicked", AppActions.on_add_clicked, self)
        self.inbox.pack_start(self.addButton, True, True, 0)
        
        # Adding the Edit button
        self.editButton = Gtk.Button.new_with_label("Edit")
        self.editButton.connect("clicked", AppActions.on_edit_clicked, self)
        self.inbox.pack_start(self.editButton, True, True, 0)
        
        # Adding the Remove button
        self.removeButton = Gtk.Button.new_with_label("Remove")
        self.removeButton.connect("clicked", AppActions.on_remove_clicked, self)
        self.inbox.pack_start(self.removeButton, True, True, 0)

        self.connect("delete-event", self.app_quit)
        self.show_all()

    def app_quit(self, parent, widget):
        FilmFile.writeFilmList("films.txt", self.filmListstore)
        Gtk.main_quit()

class DialogEdit(Gtk.Dialog):
    def __init__(self, parent, model, iter):
        Gtk.Dialog.__init__(self, "Edit", parent, Gtk.DialogFlags.MODAL,
            ("OK", Gtk.ResponseType.OK,
             "Cancel", Gtk.ResponseType.CANCEL))
        box = self.get_content_area()
        
        label = Gtk.Label("Name:")
        label.set_justify(Gtk.Justification.LEFT)
        box.pack_start(label, True, True, 0)
        
        self.entryName = Gtk.Entry()
        self.entryName.set_text(model.get_value(iter,0))
        box.pack_start(self.entryName, True, True, 0)
        
        label = Gtk.Label("Date:")
        label.set_justify(Gtk.Justification.LEFT)
        box.pack_start(label, True, True, 0)
        
        self.entryDate = Gtk.Entry()
        self.entryDate.set_text(model.get_value(iter,1))
        box.pack_start(self.entryDate, True, True, 0)
            
        label = Gtk.Label("Rating:")
        label.set_justify(Gtk.Justification.LEFT)
        box.pack_start(label, True, True, 0)
        
        self.entryRating = Gtk.Entry()
        self.entryRating.set_text(model.get_value(iter,2))
        box.pack_start(self.entryRating, True, True, 0)
        self.show_all()
        
class DialogAdd(Gtk.Dialog):
    def __init__(self, parent):
        Gtk.Dialog.__init__(self, "Add", parent, Gtk.DialogFlags.MODAL,
            ("OK", Gtk.ResponseType.OK,
             "Cancel", Gtk.ResponseType.CANCEL))
             
        box = self.get_content_area()
        
        label = Gtk.Label("Name:")
        label.set_justify(Gtk.Justification.LEFT)
        box.pack_start(label, True, True, 0)
        
        self.entryName = Gtk.Entry()
        box.pack_start(self.entryName, True, True, 0)
        
        label = Gtk.Label("Date:")
        label.set_justify(Gtk.Justification.LEFT)
        box.pack_start(label, True, True, 0)
        
        self.entryDate = Gtk.Entry()
        box.pack_start(self.entryDate, True, True, 0)
        self.show_all()
        
        label = Gtk.Label("Rating:")
        label.set_justify(Gtk.Justification.LEFT)
        box.pack_start(label, True, True, 0)
        
        self.entryRating = Gtk.Entry()
        box.pack_start(self.entryRating, True, True, 0)
        self.show_all()

class DialogWarning(Gtk.Dialog):

    def __init__(self, parent, text):
        Gtk.Dialog.__init__(self, "Warning", parent, Gtk.DialogFlags.MODAL,
            ("OK", Gtk.ResponseType.OK,
             "Cancel", Gtk.ResponseType.CANCEL))

        self.set_default_size(150, 100)

        label = Gtk.Label("¿Seguro que desea eliminar la pelcula ''" + text+ "''?")

        box = self.get_content_area()
        box.add(label)
        self.show_all()


win = AppWindow()
Gtk.main()

