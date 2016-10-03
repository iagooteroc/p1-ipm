
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

#class FilmStorage():
#    def getFilmList(fileName):
#        raise NotImplementedError("Function getFilmList not implemented")
#    def writeFilmList(fileName, filmList):
#        raise NotImplementedError("Function writeFilmList not implemented")

#class FilmFile(FilmStorage):
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


class AppWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Lista de peliculas")
        self.set_border_width(10)
        self.resize(400, 300)
        self.set_position(Gtk.WindowPosition.CENTER)

        #Setting up the self.grid in which the elements are to be positionned
        #self.grid = Gtk.Grid()
        #self.grid.set_column_homogeneous(True)
        #self.grid.set_row_homogeneous(True)
        #self.add(self.grid)
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.inbox = Gtk.Box()
        self.add(self.box)
        #self.box.set_homogeneous(False)
        #self.inbox.set_homogeneous(False)

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
        #self.grid.attach(self.scrollableTreelist, 0, 0, 3, 5)
        self.scrollableTreelist.add(self.treeview)
        
        self.box.pack_start(self.inbox, False, True, 0)
        
        # Adding the Add button
        self.addButton = Gtk.Button.new_with_label("Add")
        self.addButton.connect("clicked", self.on_add_clicked)
        #self.grid.attach_next_to(self.addButton, self.scrollableTreelist, Gtk.PositionType.BOTTOM, 1, 1)
        self.inbox.pack_start(self.addButton, True, True, 0)
        
        # Adding the Edit button
        self.editButton = Gtk.Button.new_with_label("Edit")
        self.editButton.connect("clicked", self.on_edit_clicked)
        #self.grid.attach_next_to(self.editButton, self.addButton, Gtk.PositionType.RIGHT, 1, 1)
        self.inbox.pack_start(self.editButton, True, True, 0)
        
        # Adding the Remove button
        self.removeButton = Gtk.Button.new_with_label("Remove")
        self.removeButton.connect("clicked", self.on_remove_clicked)
        #self.grid.attach_next_to(self.removeButton, self.editButton, Gtk.PositionType.RIGHT, 1, 1)
        self.inbox.pack_start(self.removeButton, True, True, 0)

        self.show_all()
        
    def on_add_clicked(self, widget): 
        dialogAdd = Gtk.Dialog("Add", self,
		                              Gtk.DialogFlags.MODAL,
		                              ("OK", Gtk.ResponseType.OK,
		                              "Cancel", Gtk.ResponseType.CANCEL))
        #dialogAdd.set_default_size(150, 100)
        box = dialogAdd.get_content_area()
        
        label = Gtk.Label("Name:")
        label.set_justify(Gtk.Justification.LEFT)
        box.pack_start(label, True, True, 0)
        
        entryName = Gtk.Entry()
        box.pack_start(entryName, True, True, 0)
        
        label = Gtk.Label("Date:")
        label.set_justify(Gtk.Justification.LEFT)
        box.pack_start(label, True, True, 0)
        
        entryDate = Gtk.Entry()
        box.pack_start(entryDate, True, True, 0)
        dialogAdd.show_all()
        
        label = Gtk.Label("Rating:")
        label.set_justify(Gtk.Justification.LEFT)
        box.pack_start(label, True, True, 0)
        
        entryRating = Gtk.Entry()
        box.pack_start(entryRating, True, True, 0)
        dialogAdd.show_all()

        response = dialogAdd.run()
        name = entryName.get_text()
        date = entryDate.get_text()
        rating = entryRating.get_text()
        dialogAdd.destroy()
        
        if (response == Gtk.ResponseType.OK):
                if (name != '') and (date != '') and (rating != ''):
                    self.add_film(self, name, date, rating)
                else:
                    self.error_dialog_blank()
    
    def add_film(self, widget, name, date, rating):
        self.filmListstore.append(list((name, date, rating)))
        
    def on_edit_clicked(self, widget):
        selection = self.treeview.get_selection()
        model, iter = selection.get_selected()
        if iter is not None:
            dialogEdit = Gtk.Dialog("Add", self,
		                              Gtk.DialogFlags.MODAL,
		                              ("OK", Gtk.ResponseType.OK,
		                              "Cancel", Gtk.ResponseType.CANCEL))
            box = dialogEdit.get_content_area()
        
            label = Gtk.Label("Name:")
            label.set_justify(Gtk.Justification.LEFT)
            box.pack_start(label, True, True, 0)
        
            entryName = Gtk.Entry()
            entryName.set_text(model.get_value(iter,0))
            box.pack_start(entryName, True, True, 0)
        
            label = Gtk.Label("Date:")
            label.set_justify(Gtk.Justification.LEFT)
            box.pack_start(label, True, True, 0)
        
            entryDate = Gtk.Entry()
            entryDate.set_text(model.get_value(iter,1))
            box.pack_start(entryDate, True, True, 0)
            dialogEdit.show_all()
            
            label = Gtk.Label("Rating:")
            label.set_justify(Gtk.Justification.LEFT)
            box.pack_start(label, True, True, 0)
        
            entryRating = Gtk.Entry()
            entryRating.set_text(model.get_value(iter,2))
            box.pack_start(entryRating, True, True, 0)
            dialogEdit.show_all()
            
            response = dialogEdit.run()
            newName = entryName.get_text()
            newDate = entryDate.get_text()
            newRating = entryRating.get_text()
            dialogEdit.destroy()
            if (response == Gtk.ResponseType.OK):
                if (newName != '') and (newDate != '') and (newRating != ''):
                    self.edit_film(self, newName, newDate, newRating, iter)
                else:
                    self.error_dialog_blank()
            
    def edit_film(self, widget, name, date, rating, iter):
        self.filmListstore.set_value(iter, 0, name)
        self.filmListstore.set_value(iter, 1, date)
        self.filmListstore.set_value(iter, 2, rating)

    def on_remove_clicked(self, widget):
        selection = self.treeview.get_selection()
        model, iter = selection.get_selected()
        if iter is not None:
            text = model.get_value(iter,0)
            warning = DialogWarning(self, text)
            response = warning.run()
            
            if response == Gtk.ResponseType.OK:
                model.remove(iter)
            warning.destroy()
    
    def error_dialog_blank(self):
        dialogError = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR,
            Gtk.ButtonsType.OK, "You must fill in all the fields")
        dialogError.run()
        dialogError.destroy()

    def app_quit(self, parent, widget):
        FilmFile.writeFilmList("films.txt", self.filmListstore)
        Gtk.main_quit()


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
win.connect("delete-event", win.app_quit)
win.show_all()

Gtk.main()

