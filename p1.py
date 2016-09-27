import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

#list of films
film_list = [("Ejemplo1", "Desc1"),
                 ("Ejemplo2", "Desc2"),
                 ("Ejemplo3", "Desc3")]

class TreeViewFilterWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Lista de películas")
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

        for i, column_title in enumerate(["Nombre","Desc"]):
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
        
        # Adding the Remove button
        self.button = Gtk.Button.new_with_label("Eliminar")
        self.button.connect("clicked", self.on_remove_clicked)
        self.grid.attach_next_to(self.button, self.scrollable_treelist, Gtk.PositionType.BOTTOM, 1, 1)

        self.show_all()

    def text_edited(self, widget, path, text, model=None, column=0):
        self.film_liststore[path][column] = text

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
        Gtk.Dialog.__init__(self, "Aviso", parent, 0,
            ("Aceptar", Gtk.ResponseType.OK,
             "Cancelar", Gtk.ResponseType.CANCEL))

        self.set_default_size(150, 100)
        self.set_modal(True)

        label = Gtk.Label("¿Seguro que desea eliminar la película ''" + text+ "''?")

        box = self.get_content_area()
        box.add(label)
        self.show_all()

win = TreeViewFilterWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()
