
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
            name,description = line.split('//')
            filmList.append([name,description[:-1]])
        f.close()
        return filmList
    
    def writeFilmList(fileName, filmList):
        f = open(fileName, 'w')
        list_iter = filmList.get_iter_first()
        while list_iter is not None:
            name = filmList.get_value(list_iter, 0)
            description = filmList.get_value(list_iter, 1)
            f.write((name + '//' + description + '\n'))
            list_iter = filmList.iter_next(list_iter)
        f.close()


class AppWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Lista de peliculas")
        self.set_border_width(10)

        #Setting up the self.grid in which the elements are to be positionned
        self.grid = Gtk.Grid()
        self.grid.set_column_homogeneous(True)
        self.grid.set_row_homogeneous(True)
        self.add(self.grid)

        #Creating the ListStore model
        self.filmListstore = Gtk.ListStore(str, str)
        
        # Loading stored films
        filmList = FilmFile.getFilmList("films.txt")
        
        # Adding them into filmListstore
        for filmRef in filmList:
            self.filmListstore.append(list(filmRef))

        #creating the treeview and adding the columns
        self.treeview = Gtk.TreeView.new_with_model(self.filmListstore)

        for i, columnTitle in enumerate(["Name","Description"]):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(columnTitle, renderer, text=i)
            self.treeview.append_column(column)
            

        #setting up the layout and putting the treeview in a scrollwindow
        self.scrollableTreelist = Gtk.ScrolledWindow()
        self.scrollableTreelist.set_vexpand(True)
        self.grid.attach(self.scrollableTreelist, 0, 0, 2, 5)
        self.scrollableTreelist.add(self.treeview)
        
        # Adding the Add button
        self.addButton = Gtk.Button.new_with_label("Add")
        self.addButton.connect("clicked", self.on_add_clicked)
        self.grid.attach_next_to(self.addButton, self.scrollableTreelist, Gtk.PositionType.BOTTOM, 1, 1)
        
        # Adding the Edit button
        self.editButton = Gtk.Button.new_with_label("Edit")
        self.editButton.connect("clicked", self.on_edit_clicked)
        self.grid.attach_next_to(self.editButton, self.addButton, Gtk.PositionType.RIGHT, 1, 1)
        
        # Adding the Remove button
        self.removeButton = Gtk.Button.new_with_label("Remove")
        self.removeButton.connect("clicked", self.on_remove_clicked)
        self.grid.attach_next_to(self.removeButton, self.editButton, Gtk.PositionType.RIGHT, 1, 1)

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
        
        label = Gtk.Label("Description:")
        label.set_justify(Gtk.Justification.LEFT)
        box.pack_start(label, True, True, 0)
        
        entryDescription = Gtk.Entry()
        box.pack_start(entryDescription, True, True, 0)
        dialogAdd.show_all()

        response = dialogAdd.run()
        name = entryName.get_text()
        description = entryDescription.get_text()
        dialogAdd.destroy()
        
        if (response == Gtk.ResponseType.OK):
                if (name != '') and (description != ''):
                    self.add_film(self, name, description)
                else:
                    self.error_dialog_blank()
    
    def add_film(self, widget, name, description):
        self.filmListstore.append(list((name, description)))
        
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
        
            label = Gtk.Label("Description:")
            label.set_justify(Gtk.Justification.LEFT)
            box.pack_start(label, True, True, 0)
        
            entryDescription = Gtk.Entry()
            entryDescription.set_text(model.get_value(iter,1))
            box.pack_start(entryDescription, True, True, 0)
            dialogEdit.show_all()
            
            response = dialogEdit.run()
            newName = entryName.get_text()
            newDescription = entryDescription.get_text()
            dialogEdit.destroy()
            if (response == Gtk.ResponseType.OK):
                if (newName != '') and (newDescription != ''):
                    self.edit_film(self, newName, newDescription, iter)
                else:
                    self.error_dialog_blank()
            
    def edit_film(self, widget, name, description, iter):
        self.filmListstore.set_value(iter, 0, name)
        self.filmListstore.set_value(iter, 1, description)

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

