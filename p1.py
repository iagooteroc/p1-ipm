
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import locale
import gettext
import os
import threading
from tmdb import *

locale.setlocale(locale.LC_ALL,'')
LOCALE_DIR = os.path.join(os.path.dirname(__file__), "locale")
locale.bindtextdomain('p1', LOCALE_DIR)
gettext.bindtextdomain('p1', LOCALE_DIR)
gettext.textdomain('p1')
_ = gettext.gettext
N_ = gettext.ngettext

# State: 0 means just added
#        1 means Seen
#        2 means Plan to Watch
#        3 means Recommended

class FilmFile():
    # devuelve la lista de peliculas desde un archivo de texto
    def getFilmList(fileName):
        filmList = []
        f = open(fileName)
        for line in f:
            #divide cada linea en partes
            name, date, rating, state = line.split('//')
            filmList.append([name,date,rating, state[:-1]])
        f.close()
        return filmList
    
    # escribe en un archivo de texto los cambios realizados en la lista
    def writeFilmList(fileName, filmList):
        f = open(fileName, 'w')
        list_iter = filmList.get_iter_first()
        while list_iter is not None:
            name = filmList.get_value(list_iter, 1)
            date = filmList.get_value(list_iter, 2)
            rating = filmList.get_value(list_iter, 3)
            state = filmList.get_value(list_iter, 4)
            f.write((name + '//' + date + '//' + rating + '//' + state + '\n'))
            list_iter = filmList.iter_next(list_iter)
        f.close()

class AppActions():
    # Lo que hace el boton Select/Deselect All cuando se pulsa
    def on_select_all_clicked(widget, parent):
        model = parent.filmModel
        iter = model.get_iter_first()
        if parent.selectedAll is False:
            while iter is not None:
                model.set_value(iter, 0, True)
                iter = model.iter_next(iter)
        else:
            while iter is not None:
                model.set_value(iter, 0, False)
                iter = model.iter_next(iter)
        parent.selectedAll = not parent.selectedAll
    
    # Lo que hace el boton Mark as Seen cuando se pulsa
    def on_seen_clicked(widget, parent):
        iter = AppActions.get_first_selected(parent.filmModel)
        while iter is not None:
            parent.filmModel.set_value(iter, 0, False)
            parent.filmModel.set_value(iter, 4, "1")
            iter = AppActions.get_first_selected(parent.filmModel)
    
    # Lo que hace el boton Mark as Plan to watch cuando se pulsa
    def on_plan_clicked(widget, parent):
        iter = AppActions.get_first_selected(parent.filmModel)
        while iter is not None:
            parent.filmModel.set_value(iter, 0, False)
            parent.filmModel.set_value(iter, 4, "2")
            iter = AppActions.get_first_selected(parent.filmModel)

    # lo que hace el boton Add cuando se pulsa
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
                    AppActions.add_film(parent, name, date, rating, "0")
                else:
                    AppActions.error_dialog(parent, _("You must fill in all the fields"))

    # funcion de anhadir una pelicula
    def add_film(parent, name, date, rating, state):
        result = AppActions.search_film(parent, name)
        if result is None:
            model = parent.filmModel.get_model()
            model.append(list((False, name, date, rating, state)))
        else:
            AppActions.error_dialog(parent, _("There is already one film with that title"))
        parent.filmModel.refilter()
    
    # lo que hace el boton edit cuando se pulsa
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
                    AppActions.edit_film(parent, newName, newDate, newRating, iter)
                else:
                    AppActions.error_dialog(parent, _("You must fill in all the fields"))
    
    # funcion de editar una pelicula                
    def edit_film(parent, name, date, rating, iter):
        parent.filmModel.set_value(iter, 1, name)
        parent.filmModel.set_value(iter, 2, date)
        parent.filmModel.set_value(iter, 3, rating)
    
    # lo que hace el boton remove cuando se pulsa    
    def on_remove_clicked(widget, parent):
        selectedIterators = AppActions.get_cell_selected(parent.filmListstore)
        num = len(selectedIterators)
        if (num == 1):
            name = parent.filmListstore.get_value((selectedIterators[0]), 1)
            warning = DialogWarningSingle(parent, name)
            response = warning.run()
        elif (num > 1):
            warning = DialogWarningMultiple(parent, num)
            response = warning.run()
        else:
            return
        if response == Gtk.ResponseType.OK:
            for iter in selectedIterators:
                parent.filmListstore.remove(iter)
        warning.destroy()
    
    # devuelve los iteradores de las peliculas marcadas    
    def get_cell_selected(model):
        selectedIterators = []
        iter = model.get_iter_first()
        while iter is not None:
            selected = model.get_value(iter, 0)
            if selected:
                selectedIterators.append(iter)
            iter = model.iter_next(iter)
        return selectedIterators
        
    # devuelve el iterador de la primera fila marcada
    def get_first_selected(model):
        iter = model.get_iter_first()
        while iter is not None:
            selected = model.get_value(iter, 0)
            if selected:
                return iter
            iter = model.iter_next(iter)
        return None
    
    # elimina la pelicula con el nombre name
    def remove_film(parent, name):
        iter = AppActions.search_film(parent, name)
        if iter is not None:
            parent.filmListstore.remove(iter)
            return True
        return False
    
    # busca el iterador de la peli en el ListStore por nombre
    def search_film(parent, name):
        iter = parent.filmListstore.get_iter_first()
        while iter is not None:
            storedName = parent.filmListstore.get_value(iter, 1)
            if (storedName == name):
                break
            iter = parent.filmListstore.iter_next(iter)
        return iter
    
    # ventana modal de mensaje de error        
    def error_dialog(parent, text):
        dialogError = Gtk.MessageDialog(parent, 0, Gtk.MessageType.ERROR,
            Gtk.ButtonsType.OK, text)
        dialogError.run()
        dialogError.destroy()
    
    # lo que hace la celda cuando se pulsa
    def on_cell_toggled(widget, path, parent):
        parent.filmModel[path][0] = not parent.filmModel[path][0]
    
    # lo que hace el combo box cuando se pulsa
    def on_combo_changed(combo, parent):
        treeIter = combo.get_active_iter()
        model = combo.get_model()
        if (model[treeIter][0] == _("Recommended")):
            parent.editButton.set_sensitive(False)
            parent.removeButton.set_sensitive(False)
            parent.recommendedThread = ThreadRecommendations(parent)
            parent.recommendedThread.start()
            
        else:
            parent.editButton.set_sensitive(True)
            parent.removeButton.set_sensitive(True)
        parent.filmModel.refilter()
        print(model[treeIter][0])
    
    # Borra las peliculas recomendadas almacenadas
    def clear_recommended(parent):
        iter = parent.filmListstore.get_iter_first()
        while iter is not None:
            storedState = parent.filmListstore.get_value(iter, 4)
            if (storedState == "3"):
                removeIter = iter
                iter = parent.filmListstore.iter_next(iter)
                parent.filmListstore.remove(removeIter)
            else:
                iter = parent.filmListstore.iter_next(iter)
        print(_("Previous recommended erased"))
        

class AppWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title=_("Film list"))
        self.set_border_width(10)
        self.resize(600, 300)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.moviedb = Tmdb()
        
        # Creating all the boxes
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.inbox = Gtk.Box()
        self.treeviewbox = Gtk.Box()
        self.buttonbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        
        # Creating the Select/Deselect All button
        self.selectAllButton = Gtk.Button.new_with_label(_("Select/Deselect All"))
        self.selectAllButton.connect("clicked", AppActions.on_select_all_clicked, self)
        self.selectedAll = False
        
        # Creating the Add button
        self.addButton = Gtk.Button.new_with_label(_("Add"))
        self.addButton.connect("clicked", AppActions.on_add_clicked, self)
        
        # Creating the Edit button
        self.editButton = Gtk.Button.new_with_label(_("Edit"))
        self.editButton.connect("clicked", AppActions.on_edit_clicked, self)
        
        # Creating the Remove button
        self.removeButton = Gtk.Button.new_with_label(_("Remove"))
        self.removeButton.connect("clicked", AppActions.on_remove_clicked, self)
        
        # Creating the Mark as Seen button
        self.seenButton = Gtk.Button.new_with_label(_("Mark as Seen"))
        self.seenButton.connect("clicked", AppActions.on_seen_clicked, self)
        
        # Creating the Mark as Plan to watch button
        self.planButton = Gtk.Button.new_with_label(_("Mark as Plan to watch"))
        self.planButton.connect("clicked", AppActions.on_plan_clicked, self)
        
        # Creating the Loading label and the Spinner
        self.loadingText = Gtk.Label(_("Loading "))
        self.spinner = Gtk.Spinner()
        
        # Creating the filmListstore model
        self.filmListstore = Gtk.ListStore(bool, str, str, str, str)
        
        # Loading stored films
        filmList = FilmFile.getFilmList("films.txt")
        # Adding them into filmListstore
        for filmRef in filmList:
            filmValues = filmRef
            # Adding the checkbox value (False)
            filmValues.insert(0, False)
            print(filmValues)
            self.filmListstore.append(filmValues)

        # Creating the TreeModelFilter from filmListstore
        self.filmModel = self.filmListstore.filter_new()
        self.filmModel.set_visible_func(self.film_filter_func)
        
        # Creating the filterCombo
        self.filterCombo = Gtk.ComboBoxText()
        self.filterCombo.connect("changed", AppActions.on_combo_changed, self)
        self.filterCombo.set_entry_text_column(0)
        
        # Adding the filter names
        filters = [_("All movies"), _("Seen"), _("Plan to watch"), _("Recommended")]
        for filterName in filters:
            self.filterCombo.append_text(filterName)
        self.filterCombo.set_active(0)
        
        # Creating the treeview and adding the columns
        self.treeview = Gtk.TreeView.new_with_model(self.filmModel)
        
        # Creating the checkbox column
        rendererToggle = Gtk.CellRendererToggle()
        rendererToggle.connect("toggled", AppActions.on_cell_toggled, self)
        columnToggle = Gtk.TreeViewColumn(_("Toggle"), rendererToggle, active=0)
        self.treeview.append_column(columnToggle)

        # Creating the Name/Date/Rating columns
        for i, columnTitle in enumerate([_("Name"),_("Date"),_("Rating")]):
            rendererText = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(columnTitle, rendererText, text=(i+1))
            self.treeview.append_column(column)
        
        # Setting up the layout and putting the treeview in a scrollwindow
        self.scrollableTreelist = Gtk.ScrolledWindow()
        self.scrollableTreelist.set_vexpand(True)
        self.scrollableTreelist.add(self.treeview)

        self.connect("delete-event", self.app_quit)
        
        # Adding the box and the widgets to the window
        # Main Box:
        self.add(self.box)
        self.box.pack_start(self.filterCombo, False, True, 0)
        self.box.pack_start(self.treeviewbox, True, True, 0)
        self.box.pack_start(self.inbox, False, True, 0)
        # TreeViewBox:
        self.treeviewbox.pack_start(self.scrollableTreelist, True, True, 0)
        self.treeviewbox.pack_start(self.buttonbox, False, True, 0)
        # ButtonBox:
        self.buttonbox.pack_start(self.selectAllButton, False, False, 0)
        self.buttonbox.pack_start(self.seenButton, False, False, 0)
        self.buttonbox.pack_start(self.planButton, False, False, 0)
        self.buttonbox.pack_start(self.loadingText, False, False, 0)
        self.buttonbox.pack_start(self.spinner, False, False, 0)
        # InBox:
        self.inbox.pack_start(self.addButton, True, True, 0)
        self.inbox.pack_start(self.editButton, True, True, 0)
        self.inbox.pack_start(self.removeButton, True, True, 0)
        
        self.show_all()
        self.loadingText.hide()
        self.spinner.hide()
        
    # funcion de filtrar las peliculas por Todas, Vistas o Por ver        
    def film_filter_func(self, model, iter, data):
        treeIter = self.filterCombo.get_active_iter()
        comboModel = self.filterCombo.get_model()
        movieFilter = comboModel[treeIter][0]
        if (movieFilter == _("All movies")):
            if (model.get_value(iter, 4) != "3"):
                return True
            else:
                return False
        if (movieFilter == _("Seen")):
            if (model.get_value(iter, 4) == "1"):
                return True
            else:
                return False
        if (movieFilter == _("Plan to watch")):
            if (model[iter][4] == "2"):
                return True
            else:
                return False
        if (movieFilter == _("Recommended")):
            if (model.get_value(iter, 4) == "3"):
                return True
        else:
            return False
        
    # funcion que guarda los cambios en el archivo de texto
    def app_quit(self, parent, widget):
        self.moviedb.close_connection()
        AppActions.clear_recommended(self)
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
        self.entryName.set_text(model.get_value(iter,1))
        box.pack_start(self.entryName, True, True, 0)
        
        label = Gtk.Label(_("Date:"))
        label.set_justify(Gtk.Justification.LEFT)
        box.pack_start(label, True, True, 0)
        
        self.entryDate = Gtk.Entry()
        self.entryDate.set_text(model.get_value(iter,2))
        box.pack_start(self.entryDate, True, True, 0)
            
        label = Gtk.Label(_("Rating:"))
        label.set_justify(Gtk.Justification.LEFT)
        box.pack_start(label, True, True, 0)
        
        self.entryRating = Gtk.Entry()
        self.entryRating.set_text(model.get_value(iter,3))
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

class DialogWarningSingle(Gtk.Dialog):

    def __init__(self, parent, text):
        Gtk.Dialog.__init__(self, _("Warning"), parent, Gtk.DialogFlags.MODAL,
            (_("OK"), Gtk.ResponseType.OK,
             _("Cancel"), Gtk.ResponseType.CANCEL))

        self.set_default_size(150, 100)

        label = Gtk.Label(_("Are you sure you want to delete ''") + text+ "''?")

        box = self.get_content_area()
        box.add(label)
        self.show_all()

class DialogWarningMultiple(Gtk.Dialog):

    def __init__(self, parent, num):
        Gtk.Dialog.__init__(self, _("Warning"), parent, Gtk.DialogFlags.MODAL,
            (_("OK"), Gtk.ResponseType.OK,
             _("Cancel"), Gtk.ResponseType.CANCEL))

        self.set_default_size(150, 100)

        label = Gtk.Label(_("Are you sure you want to delete ") + str(num) + _(" films?"))

        box = self.get_content_area()
        box.add(label)
        self.show_all()

class ThreadRecommendations(threading.Thread):
    def __init__(self, parent):
        threading.Thread.__init__(self)
        self.parent = parent
        
    def run(self):
        self.parent.loadingText.show()
        self.parent.spinner.show()
        self.parent.spinner.start()
        self.recommended_function(self.parent)
        self.parent.loadingText.hide()
        self.parent.spinner.stop()
        self.parent.spinner.hide()
        print(_("Ending thread..."))
    
    # Manages the recommendation of films
    def recommended_function(self, parent):
        AppActions.clear_recommended(parent)
        iter = parent.filmListstore.get_iter_first()
        id_list = []
        while iter is not None:
            storedState = parent.filmListstore.get_value(iter, 4)
            if (storedState == "1"):
                name = parent.filmListstore.get_value(iter, 1)
                print(_("Name: ") + name)
                id = parent.moviedb.get_movie_id(name)
                if id is not None:
                    id_list.append(id)
            iter = parent.filmListstore.iter_next(iter)
        self.load_recommended(id_list, parent)
    
    # Obtiene peliculas recomendadas en funcion de una lista de ids y las anhade
    def load_recommended(self, id_list, parent):
        print(_("Getting recommendations..."))
        filmList = parent.moviedb.get_recommendations(id_list)
        print(filmList)
        for film in filmList:
            name = film[0]
            result = AppActions.search_film(parent, name)
            if result is not None:
                continue
            date = film[1]
            rating = film[2]
            print(_("Adding ") + film[0])
            AppActions.add_film(parent, name, date, rating, "3")
            parent.filmModel.refilter()
        
        

win = AppWindow()
Gtk.main()

