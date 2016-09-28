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
        add = DialogAdd(self)
        response = add.run()
        
        if response == Gtk.ResponseType.OK:
            print("Ok")
        add.destroy()
    
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

class DialogAdd(Gtk.Dialog):
    def __init__(self, parent):
        Gtk.Dialog.__init__(self, "Add", parent, 0,
            ("Aceptar", Gtk.ResponseType.OK,
             "Cancelar", Gtk.ResponseType.CANCEL))
        self.set_default_size(150, 100)
        self.set_modal(True)
        entry = Gtk.Entry()
        box = self.get_content_area()
        box.add(entry)
        # Se puede poner el Enter como Aceptar: entry.connect("activate", 
        ########TODO########
        # Esto tiene que hacerse despus de darle a Aceptar:
        #new_text = entry.get_text()
        #parent.add_film(parent, new_text)
        self.show_all() # igual no hace falta

class DialogWarning(Gtk.Dialog):

    def __init__(self, parent, text):
        Gtk.Dialog.__init__(self, "Aviso", parent, 0,
            ("Aceptar", Gtk.ResponseType.OK,
             "Cancelar", Gtk.ResponseType.CANCEL))

        self.set_default_size(150, 100)
        self.set_modal(True)

        label = Gtk.Label("¿Seguro que desea eliminar la pelcula ''" + text+ "''?")

        box = self.get_content_area()
        box.add(label)
        self.show_all()

win = TreeViewFilterWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()

