
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

#list of films
film_list = [("Ejemplo1", "Desc1"),
                 ("Ejemplo2", "Desc2"),
                 ("Ejemplo3", "Desc3")]

#class FilmList():
#    def __init__(self):
#        self.filmList = Gtk.ListStore(str, str)
#        for film_ref in film_list:
#            self.filmList.append(list(film_ref))
        

class TreeViewFilterWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Lista de peliculas")
        self.set_border_width(10)

        #Setting up the self.grid in which the elements are to be positionned
        self.grid = Gtk.Grid()
        self.grid.set_column_homogeneous(True)
        self.grid.set_row_homogeneous(True)
        self.add(self.grid)

        #Creating the ListStore model
        self.film_liststore = Gtk.ListStore(str, str)
        for film_ref in film_list:
            self.film_liststore.append(list(film_ref))

        #creating the treeview and adding the columns
        self.treeview = Gtk.TreeView.new_with_model(self.film_liststore)

        for i, column_title in enumerate(["Nombre","Descripcion"]):
            renderer = Gtk.CellRendererText()
            renderer.set_property("editable",True)
            column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            self.treeview.append_column(column)
            renderer.connect("edited",self.text_edited, self.film_liststore, i)
            

        #setting up the layout and putting the treeview in a scrollwindow
        self.scrollable_treelist = Gtk.ScrolledWindow()
        self.scrollable_treelist.set_vexpand(True)
        self.grid.attach(self.scrollable_treelist, 0, 0, 2, 5)
        self.scrollable_treelist.add(self.treeview)
        
        # Adding the Add button
        self.add_button = Gtk.Button.new_with_label("Añadir")
        self.add_button.connect("clicked", self.on_add_clicked)
        self.grid.attach_next_to(self.add_button, self.scrollable_treelist, Gtk.PositionType.BOTTOM, 1, 1)
        
        # Adding the Edit button
        self.edit_button = Gtk.Button.new_with_label("Editar")
        self.edit_button.connect("clicked", self.on_edit_clicked)
        self.grid.attach_next_to(self.edit_button, self.add_button, Gtk.PositionType.RIGHT, 1, 1)
        
        # Adding the Remove button
        self.remove_button = Gtk.Button.new_with_label("Eliminar")
        self.remove_button.connect("clicked", self.on_remove_clicked)
        self.grid.attach_next_to(self.remove_button, self.edit_button, Gtk.PositionType.RIGHT, 1, 1)

        self.show_all()

    def text_edited(self, widget, path, text, model=None, column=0):
        self.film_liststore[path][column] = text
        
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
        
        entry_name = Gtk.Entry()
        box.pack_start(entry_name, True, True, 0)
        
        label = Gtk.Label("Description:")
        label.set_justify(Gtk.Justification.LEFT)
        box.pack_start(label, True, True, 0)
        
        entry_description = Gtk.Entry()
        box.pack_start(entry_description, True, True, 0)
        dialogAdd.show_all()

        response = dialogAdd.run()
        name = entry_name.get_text()
        description = entry_description.get_text()
        dialogAdd.destroy()
        if (response == Gtk.ResponseType.OK) and (name != '') and (description != ''):
            self.add_film(self, name, description)
    
    def add_film(self, widget, name, description):
        self.film_liststore.append(list((name, description)))
        
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
        
            entry_name = Gtk.Entry()
            entry_name.set_text(model.get_value(iter,0))
            box.pack_start(entry_name, True, True, 0)
        
            label = Gtk.Label("Description:")
            label.set_justify(Gtk.Justification.LEFT)
            box.pack_start(label, True, True, 0)
        
            entry_description = Gtk.Entry()
            entry_description.set_text(model.get_value(iter,1))
            box.pack_start(entry_description, True, True, 0)
            dialogEdit.show_all()
            
            response = dialogEdit.run()
            new_name = entry_name.get_text()
            new_description = entry_description.get_text()
            dialogEdit.destroy()
            if (response == Gtk.ResponseType.OK) and (new_name != '') and (new_description != ''):
                self.edit_film(self, new_name, new_description, iter)
            
    def edit_film(self, widget, name, description, iter):
        self.film_liststore.set_value(iter, 0, name)
        self.film_liststore.set_value(iter, 1, description)

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

class DialogWarning(Gtk.Dialog):

    def __init__(self, parent, text):
        Gtk.Dialog.__init__(self, "Aviso", parent, Gtk.DialogFlags.MODAL,
            ("Aceptar", Gtk.ResponseType.OK,
             "Cancelar", Gtk.ResponseType.CANCEL))

        self.set_default_size(150, 100)

        label = Gtk.Label("¿Seguro que desea eliminar la pelcula ''" + text+ "''?")

        box = self.get_content_area()
        box.add(label)
        self.show_all()

win = TreeViewFilterWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()

