
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

#list of films
film_list = [("Ejemplo1", "Desc1"),
                 ("Ejemplo2", "Desc2"),
                 ("Ejemplo3", "Desc3")]

class TreeViewFilterWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Lista de pelculas")
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

        for i, column_title in enumerate(["Nombre","Descripcin"]):
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
        
        # Adding the Remove button
        self.remove_button = Gtk.Button.new_with_label("Eliminar")
        self.remove_button.connect("clicked", self.on_remove_clicked)
        self.grid.attach_next_to(self.remove_button, self.add_button, Gtk.PositionType.RIGHT, 1, 1)

        self.show_all()

    def text_edited(self, widget, path, text, model=None, column=0):
        self.film_liststore[path][column] = text
        
    def on_add_clicked(self, widget): 
        dialogAdd = Gtk.Dialog("Add", self,
		                              Gtk.DialogFlags.MODAL,
		                              ("OK", Gtk.ResponseType.OK,
		                              "Cancel", Gtk.ResponseType.CANCEL))
        dialogAdd.set_default_size(150, 100)
        entry = Gtk.Entry()
        box = dialogAdd.get_content_area()
        box.add(entry)
        dialogAdd.show_all()

        response = dialogAdd.run()
        text = entry.get_text()
        dialogAdd.destroy()
        if (response == Gtk.ResponseType.OK) and (text != ''):
            self.add_film(self, text)
    
    def add_film(self, widget, name):
        self.film_liststore.append(list((name, "SampleDescription")))

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

#class DialogAdd(Gtk.Dialog):
#    def __init__(self, parent):
#        Gtk.Dialog.__init__(self, "Add", parent, Gtk.DialogFlags.MODAL,
#            ("Aceptar", Gtk.ResponseType.OK,
#             "Cancelar", Gtk.ResponseType.CANCEL))
#        self.set_default_size(150, 100)
#        
#        entry = Gtk.Entry()
#        box = self.get_content_area()
#        box.add(entry)
#        self.show_all()

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

