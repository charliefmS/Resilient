import sqlite3
import gi
import shutil 
import os
from os import path
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository.GdkPixbuf import Pixbuf

db=sqlite3.connect('AguasMachala.db')


class MyWindow:
    
    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file("IngresarForm.glade")
        self.builder.connect_signals(self)

        #Get Info para filtrar    
        self.Busqueda_entry = self.builder.get_object("Busqueda_entry")
        self.Busqueda_entry.set_placeholder_text("Escriba nombre de equipo...")
        self.Busqueda_entry.connect("changed", self.refresh_filter)
      
        
        # the liststore Condicion
        self.name_store_condicion = Gtk.ListStore(str)
        cursor_condicion=db.cursor()
        cursor_condicion.execute('''SELECT Condicion FROM Condicion''')
        self.all_rows_condicion=cursor_condicion.fetchall()
        for row in self.all_rows_condicion:
            self.name_store_condicion.append([row[0]])
 

        # the liststore Lugar
        self.name_store = Gtk.ListStore(str)
        cursor=db.cursor()
        cursor.execute('''SELECT Lugar FROM Lugar''')
        self.all_rows_lugar=cursor.fetchall()
        for row in self.all_rows_lugar:
            self.name_store.append([row[0]])

        #the liststore DataBase
        self.name_store_databaseB = Gtk.ListStore(int, str, str, str, str, str)
        self.cursor_databaseB=db.cursor()
        self.cursor_databaseB.execute('''SELECT ID, Item, Manufacturer, NSerie, Cantidad, Lugar FROM Tablas''')
        all_rows=self.cursor_databaseB.fetchall()
        for row in all_rows:
            self.name_store_databaseB.append([row[0], row[1], row[2], row[3], row[4], row[5]])

        #Models 
        self.filter_Bodega = self.name_store_databaseB.filter_new()
        self.filter_Bodega.set_visible_func(self.visible_cb)

        self.filter_item = self.name_store_databaseB.filter_new()
        self.filter_item.set_visible_func(self.visible_item)
        
        #self.filter_Quimico.set_visible_func(self.visible_lugar)

        #self.filter_NSerie = self.name_store_databaseB.filter_new()
        #self.filter_NSerie.set_visible_func(self.visible_serie)
        
        
        #the combobox Condicion
        self.combobox_condicion = self.builder.get_object("Condicion_combobox")
        self.combobox_condicion.set_model(self.name_store_condicion)
        self.cell = Gtk.CellRendererText()
        self.combobox_condicion.pack_start(self.cell, True)
        self.combobox_condicion.add_attribute(self.cell, "text", 0)


        #the combobox Condicion1 para Actualizar Datos
        self.combobox_condicion1 = self.builder.get_object("Condicion_combobox1")
        self.combobox_condicion1.set_model(self.name_store_condicion)
        self.cell = Gtk.CellRendererText()
        self.combobox_condicion1.pack_start(self.cell, True)
        self.combobox_condicion1.add_attribute(self.cell, "text", 0)

        #the combobox Lugar
        self.combobox_lugar = self.builder.get_object("Lugar_combobox")
        self.combobox_lugar.set_model(self.name_store)
        self.cell = Gtk.CellRendererText()
        self.combobox_lugar.pack_start(self.cell, True)
        self.combobox_lugar.add_attribute(self.cell, "text", 0)


        #the combobox Lugar1 para Actualizar Datos
        self.combobox_lugar1 = self.builder.get_object("Lugar_combobox1")
        self.combobox_lugar1.set_model(self.name_store)
        self.cell = Gtk.CellRendererText()
        self.combobox_lugar1.pack_start(self.cell, True)
        self.combobox_lugar1.add_attribute(self.cell, "text", 0)     
        
        self.Ventana_Principal()

    
    def refresh_treeview(self):

        self.name_store_databaseB.clear()
        self.cursor_databaseB=db.cursor()
        self.cursor_databaseB.execute('''SELECT ID, Item, Manufacturer, NSerie, Cantidad, Lugar FROM Tablas''')
        all_rows=self.cursor_databaseB.fetchall()
        for row in all_rows:
            self.name_store_databaseB.append([row[0], row[1], row[2], row[3], row[4], row[5]])
        

    def Ingresar_ventanaP(self, widget, data = None):
        
        self.ventana_ingreso = self.builder.get_object("Ventana_Ingreso")
        self.ventana_ingreso.show_all() 
         
    def Editar_ventana(self, widget, data = None):
        
        self.ventana_editar = self.builder.get_object("Ventana_Edicion")
        self.ventana_editar.show_all()

    def Guardar_db(self, widget, data = None):

        #Get the data from Form EntryText
        self.Item_entry = self.builder.get_object("Item_entry")
        self.Marca_entry = self.builder.get_object("Marca_entry")
        self.Tipo_entry = self.builder.get_object("Tipo_entry")
        self.Modelo_entry = self.builder.get_object("Modelo_entry")
        self.NSerie_entry = self.builder.get_object("NSerie_entry")
        self.Cantidad_entry = self.builder.get_object("Cantidad_entry")
        self.Specs_entry = self.builder.get_object("Specs_entry")

        #Get the data from Combobox Condicion
        index = self.combobox_condicion.get_active()
        model_condicion = self.combobox_condicion.get_model()
        item=model_condicion[index]
        #print item[0]

        #Get the data from Combobox Lugar
        index_lugar = self.combobox_lugar.get_active()
        model_lugar = self.combobox_lugar.get_model()
        item_lugar=model_lugar[index_lugar]
        #print item_lugar[0]
        
        #Get text from Form
        Item_text = self.Item_entry.get_text()
        Marca_text = self.Marca_entry.get_text()
        Tipo_text = self.Tipo_entry.get_text()
        Modelo_text = self.Modelo_entry.get_text()
        NSerie_text = self.NSerie_entry.get_text()
        Cantidad_text = self.Cantidad_entry.get_text()
        Specs_text = self.Specs_entry.get_text()

        #copiar foto a la carpeta de Imagenes de la base de datos y ubicandola en el lugar donde pertenece
        if  self.Image_area.get_children() != []:
            dst_dir = 'C:\\msys64\\home\\charl\\Imagenes\\' + item_lugar[0] + '\\' + Item_text + '.jpg'
            shutil.copy(self.path, dst_dir)

            #Fill New Record with info typed 
            cursor_Guardar=db.cursor()
            sql = "INSERT Into Tablas (Item, Manufacturer, Tipo, Modelo, NSerie, Cantidad, Condicion, Lugar, Attachments, Descripcion) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (Item_text, Marca_text, Tipo_text, Modelo_text, NSerie_text, Cantidad_text, item[0], item_lugar[0], dst_dir, Specs_text)
            cursor_Guardar.execute(sql)
            db.commit() 


        else:

            #Fill New Record with info typed 
            cursor_Guardar=db.cursor()
            sql = "INSERT Into Tablas (Item, Manufacturer, Tipo, Modelo, NSerie, Cantidad, Condicion, Lugar, Attachments, Descripcion) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', NULL, '%s')" % (Item_text, Marca_text, Tipo_text, Modelo_text, NSerie_text, Cantidad_text, item[0], item_lugar[0], Specs_text)
            cursor_Guardar.execute(sql)
            db.commit() 

        self.Item_entry.set_text("")
        self.Marca_entry.set_text("")
        self.Tipo_entry.set_text("")
        self.Modelo_entry.set_text("")
        self.NSerie_entry.set_text("")
        self.Cantidad_entry.set_text("")

        #Mensaje de confirmacion al cargar archivos
        self.aceptarwindow = self.builder.get_object("VentanaAceptar")
        self.aceptarwindow.show()

        #Remover la imagen
        for children in self.Image_area.get_children():
                self.Image_area.remove(children)    
        #except:

            #Mensaje de error
            #self.errorwindow = self.builder.get_object("VentanaError")
            #self.errorwindow.show()
        #self.name_store_databaseB.clear()
        #self.name_store_databaseB.create_model_checks()
        #self.treeview_ventanaP.set_model(self.name_store_databaseB)
        self.refresh_treeview()
    
    def Actualizar_boton(self, widget, data = None):
        
        self.Image_area1 = self.builder.get_object("Image_area1")
        
        
        #Get the data from Form EntryText
        self.Item_entry = self.builder.get_object("Item_entry1")
        self.Marca_entry = self.builder.get_object("Marca_entry1")
        self.Tipo_entry = self.builder.get_object("Tipo_entry1")
        self.Modelo_entry = self.builder.get_object("Modelo_entry1")
        self.NSerie_entry = self.builder.get_object("NSerie_entry1")
        self.Cantidad_entry = self.builder.get_object("Cantidad_entry1")
        self.Specs_b = self.builder.get_object("Specs_textview")
        self.Specs = self.Specs_b.get_buffer()


        #Get the data from Combobox Condicion
        index = self.combobox_condicion1.get_active()
        model_condicion = self.combobox_condicion1.get_model()
        item=model_condicion[index]
        #print item[0]

        #Get the data from Combobox Lugar
        index_lugar = self.combobox_lugar1.get_active()
        model_lugar = self.combobox_lugar1.get_model()
        item_lugar=model_lugar[index_lugar]
        #print item_lugar[0]
        
        #Get text from Form
        Item_text = self.Item_entry.get_text()
        Marca_text = self.Marca_entry.get_text()
        Tipo_text = self.Tipo_entry.get_text()
        Modelo_text = self.Modelo_entry.get_text()
        NSerie_text = self.NSerie_entry.get_text()
        Cantidad_text = self.Cantidad_entry.get_text()
        
        Specs_text = self.Specs.get_text(self.Specs.get_start_iter(),self.Specs.get_end_iter(), False)
        #print Specs_text

        
        
        
        #copiar foto a la carpeta de Imagenes de la base de datos y ubicandola en el lugar donde pertenece
        if  self.Image_area1.get_children() != []:
            dst_dir = 'C:\\msys64\\home\\charl\\Imagenes\\' + item_lugar[0] + '\\' + Item_text + '.jpg'
            if path.exists(dst_dir):
                #Fill New Record with info typed
                # corregir esta vaina 
                cursor_Guardar1=db.cursor()
                #if id != null condicion para hacer update en un field y usar solo la funcion guardar
                sql1 = """UPDATE Tablas SET Item = '%s', Manufacturer = '%s', Tipo = '%s', Modelo = '%s', NSerie = '%s', Cantidad = '%s', Condicion = '%s', Lugar = '%s', Attachments = '%s', Descripcion = '%s' WHERE ID = '%d' """ % (Item_text, Marca_text, Tipo_text, Modelo_text, NSerie_text, Cantidad_text, item[0], item_lugar[0], dst_dir, Specs_text, self.valor)
                #sql = "INSERT Into Tablas (Item, Manufacturer, Tipo, Modelo, NSerie, Cantidad, Condicion, Lugar, Attachments, Descripcion) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (Item_text, Marca_text, Tipo_text, Modelo_text, NSerie_text, Cantidad_text, item[0], item_lugar[0], dst_dir, Specs_text)
                cursor_Guardar1.execute(sql1)
                db.commit() 

            else:
            
                #dst_dir = 'C:\\msys64\\home\\charl\\Imagenes\\' + item_lugar[0] + '\\' + Item_text + '.jpg'
                shutil.copy(self.path, dst_dir)

                #Fill New Record with info typed 
                cursor_Guardar1=db.cursor()
                #if id != null condicion para hacer update en un field y usar solo la funcion guardar
                sql1 = """UPDATE Tablas SET Item = '%s', Manufacturer = '%s', Tipo = '%s', Modelo = '%s', NSerie = '%s', Cantidad = '%s', Condicion = '%s', Lugar = '%s', Attachments = '%s', Descripcion = '%s' WHERE ID = '%d' """ % (Item_text, Marca_text, Tipo_text, Modelo_text, NSerie_text, Cantidad_text, item[0], item_lugar[0], dst_dir, Specs_text, self.valor)
                #sql = "INSERT Into Tablas (Item, Manufacturer, Tipo, Modelo, NSerie, Cantidad, Condicion, Lugar, Attachments, Descripcion) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (Item_text, Marca_text, Tipo_text, Modelo_text, NSerie_text, Cantidad_text, item[0], item_lugar[0], dst_dir, Specs_text)
                cursor_Guardar1.execute(sql1)
                db.commit() 

        else:
            
            #Fill New Record with info typed 
            cursor_Guardar1=db.cursor()
            #if id != null condicion para hacer update en un field y usar solo la funcion guardar
            sql1 = """UPDATE Tablas SET Item = '%s', Manufacturer = '%s', Tipo = '%s', Modelo = '%s', NSerie = '%s', Cantidad = '%s', Condicion = '%s', Lugar = '%s', Attachments = NULL, Descripcion = '%s' WHERE ID = '%d' """ % (Item_text, Marca_text, Tipo_text, Modelo_text, NSerie_text, Cantidad_text, item[0], item_lugar[0], Specs_text, self.valor)
            #sql = "INSERT Into Tablas (Item, Manufacturer, Tipo, Modelo, NSerie, Cantidad, Condicion, Lugar, Attachments, Descripcion) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (Item_text, Marca_text, Tipo_text, Modelo_text, NSerie_text, Cantidad_text, item[0], item_lugar[0], dst_dir, Specs_text)
            cursor_Guardar1.execute(sql1)
            db.commit() 


        #Mensaje de confirmacion al cargar archivos
        self.aceptarwindow = self.builder.get_object("VentanaAceptar")
        self.aceptarwindow.show()
   
        #except:

            #Mensaje de error
            #self.errorwindow = self.builder.get_object("VentanaError")
            #self.errorwindow.show()
        #self.name_store_databaseB.clear()
        #self.name_store_databaseB.create_model_checks()
        #self.treeview_ventanaP.set_model(self.name_store_databaseB)
        self.refresh_treeview()
        
    def refresh_filter(self,widget):
        self.filter_item.refilter()
        #self.filter_NSerie.refilter()    
    
    def visible_cb(self, model, iter, data=None):
        
        #searcg_query_NSerie = self.NSerieB_entry.get_text().lower()

        self.value1 = model.get_value(iter, 5)
        if self.value1 == "Edificio Quimico":
            return False
        else:
            return True
        

        #if search_query_Item == "":
            #return True
        #else:
            #if search_query_Item:
                #self.value = model.get_value(iter, 1).lower()
                #return True if self.value.startswith(search_query_Item) in x else False
        

    def visible_item(self, model, iter, data=None):
       
        search_query_Item = self.Busqueda_entry.get_text().lower()
        if search_query_Item == "":
            return True
        else:
            if search_query_Item:
                self.value = model.get_value(iter, 1).lower()
                return True if self.value.startswith(search_query_Item) else False
        

    def Siguiente_boton(self, widget, data = None):
        self.ventana_ingreso = self.builder.get_object("Ventana_Ingreso")
        self.ventana_ingreso.show_all() 
   
    def Anadir_imagen(self, widget, data = None):
        
        self.escoger_imagen = self.builder.get_object("Escoger_Imagen")
        self.ventana_ingresar = self.builder.get_object("Ventana_Ingreso")
        self.vetnana_editar = self.builder.get_object("Ventana_Edicion")
        

        filter = Gtk.FileFilter()
        filter.set_name("Images")
        filter.add_mime_type("image/png")
        filter.add_mime_type("image/jpeg")
        filter.add_pattern("*.png")
        filter.add_pattern("*.jpg")
        filter.add_pattern("*.jpeg")
        self.escoger_imagen.add_filter(filter)
        
        #if self.ventana_editar.has_toplevel_focus() == True:
            #self.Image_area = self.builder.get_object("Image_area1")


        if self.ventana_ingresar.has_toplevel_focus() == True:
            self.Image_area = self.builder.get_object("Image_area")

        self.response = self.escoger_imagen.run()   
    
    def Respuesta_Boton(self, widget, response):
        
        
        #self.Image_area = self.builder.get_object("Image_area1")

        
        
        
        if response == 1:
            #Remueve Imagen Previa 
            for children in self.Image_area.get_children():
                self.Image_area.remove(children)
            
            try:
                #Escoger Imagen desde un directorio
                self.path = self.escoger_imagen.get_filename()
                self.pixbuf = Pixbuf.new_from_file_at_size(self.path, 350, 350)
                self.image = Gtk.Image()
                self.image.set_from_pixbuf(self.pixbuf)
                #Colocar Imagen en su lugar
                self.Image_area.add(self.image)
                self.Image_area.show_all()
                self.escoger_imagen.hide()


            except:
                #Mensaje de error
                self.errorwindow = self.builder.get_object("VentanaError")
                self.errorwindow.show() 

        elif response == 2:
            self.escoger_imagen.hide() #Mensaje de Error para busqueda

    def Detalle_boton(self, widget):
        
        self.ventanaD = self.builder.get_object("Ventana_Detalle")
        self.ImageD_area = self.builder.get_object("ImageD_area")
        self.label1 = self.builder.get_object("label1")
        self.label2 = self.builder.get_object("label2")
        self.label3 = self.builder.get_object("label3")
        self.label4 = self.builder.get_object("label4")
        self.label5 = self.builder.get_object("label5")
        self.label6 = self.builder.get_object("label6")
        self.label7 = self.builder.get_object("label7")
        self.label8 = self.builder.get_object("label8")
        self.label9_b = self.builder.get_object("SpecsD_textview")
        self.label9 = self.label9_b.get_buffer() 
        self.ventanaD.show_all()
    

        self.dumb_array = Gtk.ListStore(int, str, str, str, str, str, str, str, str, str, str)
        self.cursor_uno=db.cursor()
        sql1 = """SELECT ID, Item, Manufacturer, Tipo, Modelo, NSerie, Cantidad, Condicion, Lugar, Descripcion, Attachments FROM Tablas WHERE ID = '%d' """ % (self.valor)
        self.cursor_uno.execute(sql1)
        self.one_row=self.cursor_uno.fetchone()
        
        for i in range(1, 10):
            if self.one_row[i]!= None:
                getattr(self, 'label%s' %i).set_text(self.one_row[i])

        
            
        for children in self.ImageD_area.get_children():
            self.ImageD_area.remove(children)
                
        if self.one_row[10] != None:
            #Escoger Imagen desde un directorio
            self.pathD = self.one_row[10]
            self.pixbufD = Pixbuf.new_from_file_at_size(self.pathD, 350, 350)
            self.imageD = Gtk.Image()
            self.imageD.set_from_pixbuf(self.pixbufD)
            #Colocar Imagen en su lugar
            self.ImageD_area.add(self.imageD)
            self.ImageD_area.show_all()
        
                


        #Get data from one cell 
        #for data_cell in cursor_item:
            #if data_cell[0] == self.valor:
                #print data_cell[0]

    def onSelectionChanged(self, tree_selection):
        
        (model_1, pathlist) = tree_selection.get_selected()

        if pathlist != None:
            self.botonD.set_sensitive(True)
            self.botonE.set_sensitive(True)
            self.botonR.set_sensitive(True)
            self.botonElim.set_sensitive(True)
            self.valor = model_1.get_value(pathlist, 0)
            #print self.valor
                
        #para el metodo get_selected_rows()   
        #for path in pathlist :
            #tree_iter = model_1.get_iter(path)
            #if tree_iter != None:
                #self.botonD.set_sensitive(True)
                #self.valor = model_1.get_value(tree_iter,0)
                #print self.valor
    
    def Editar_boton(self, widget):
        
        self.ventana_editar = self.builder.get_object("Ventana_Edicion")
        self.ventana_editar.show_all()



        self.label1 = self.builder.get_object("Item_entry1")
        self.label2 = self.builder.get_object("Marca_entry1")
        self.label3 = self.builder.get_object("Tipo_entry1")
        self.label4 = self.builder.get_object("Modelo_entry1")
        self.label5 = self.builder.get_object("NSerie_entry1")
        self.label6 = self.builder.get_object("Cantidad_entry1")
        self.label7_b = self.builder.get_object("Specs_textview")
        self.label7 = self.label7_b.get_buffer()

        self.dumb_array = Gtk.ListStore(int, str, str, str, str, str, str, str, str, str, str)
        self.cursor_uno=db.cursor()
        sql1 = """SELECT ID, Item, Manufacturer, Tipo, Modelo, NSerie, Cantidad, Descripcion, Attachments, Condicion, Lugar FROM Tablas WHERE ID = '%d' """ % (self.valor)
        self.cursor_uno.execute(sql1)
        self.one_row=self.cursor_uno.fetchone()

        for i in range(1, 8):
            if self.one_row[i]!= None:
                getattr(self, 'label%s' %i).set_text(self.one_row[i])
        


        #Colocar la Condicion desde item seleccionado
        for i in self.all_rows_condicion:
            if self.one_row[9] == i[0]:
                index = self.all_rows_condicion.index(i) 
                self.combobox_condicion1.set_active(index)

        #Colocar  en Lugar desde item seleccionado
        for i in self.all_rows_lugar:
            if self.one_row[10] == i[0]:
                index = self.all_rows_lugar.index(i) 
                self.combobox_lugar1.set_active(index)
        
        
        self.ImageA_area = self.builder.get_object("Image_area1")
        for children in self.ImageA_area.get_children():
            self.ImageA_area.remove(children)

        #Colocar la Imagen en su lugar        
        
             
        if self.one_row[8] != None:
            #Escoger Imagen desde un directorio
            self.pathD = self.one_row[8]
            self.pixbufA = Pixbuf.new_from_file_at_size(self.pathD, 350, 350)
            self.imageA = Gtk.Image()
            self.imageA.set_from_pixbuf(self.pixbufA)
            #Colocar Imagen en su lugar
            self.ImageA_area.add(self.imageA)
            self.ImageA_area.show_all()
        else:
            self.pathD = None

    def Reemplazar_boton(self, widget):
        self.ventana_reemplazar = self.builder.get_object("VentanaReemplazar")

        self.ImageR_area = self.builder.get_object("ImageR_area")
        self.label1 = self.builder.get_object("label12")
        self.label2 = self.builder.get_object("label13")
        self.label3 = self.builder.get_object("label14")
        self.label4 = self.builder.get_object("label15")
        self.label5 = self.builder.get_object("label16")
        self.label6 = self.builder.get_object("label17")
        self.label7 = self.builder.get_object("label18")
        self.label8 = self.builder.get_object("label19")
        #self.label9 = self.builder.get_object("label20")
        self.ventana_reemplazar.show_all()
    

        self.dumb_array = Gtk.ListStore(int, str, str, str, str, str, str, str, str, str)
        self.cursor_uno=db.cursor()
        sql1 = """SELECT ID, Item, Manufacturer, Tipo, Modelo, NSerie, Cantidad, Condicion, Lugar, Attachments FROM Tablas WHERE ID = '%d' """ % (self.valor)
        self.cursor_uno.execute(sql1)
        self.one_row=self.cursor_uno.fetchone()
        
        for i in range(1, 9):
            if self.one_row[i]!= None:
                getattr(self, 'label%s' %i).set_text(self.one_row[i])

        
            
        for children in self.ImageR_area.get_children():
            self.ImageR_area.remove(children)
                
        if self.one_row[9] != None:
            #Escoger Imagen desde un directorio
            self.pathR = self.one_row[9]
            self.pixbufR = Pixbuf.new_from_file_at_size(self.pathR, 350, 350)
            self.imageR = Gtk.Image()
            self.imageR.set_from_pixbuf(self.pixbufR)
            #Colocar Imagen en su lugar
            self.ImageR_area.add(self.imageR)
            self.ImageR_area.show_all()

    def Eliminar_boton(self, widget):

        self.cursor_eliminar=db.cursor()
        sql1 = """ delete FROM Tablas WHERE ID = '%d' """ % (self.valor)
        self.cursor_eliminar.execute(sql1)
        db.commit() 
        self.refresh_treeview()

    def fecha_reemplazo(self, widget):

        self.fechas = []
        self.calendario_fecha = self.builder.get_object("calendar1")
        self.fecha_entry = self.builder.get_object("fecha_entry")
        self.fecha = self.calendario_fecha.get_date()
        for date in self.fecha:
            self.fechas.append(date)
        self.fecha_completa = str(self.fechas[2]) + "/" + str(self.fechas[1]) + "/" + str(self.fechas[0])
        self.fecha_entry.set_text(self.fecha_completa)

    def Ventana_Principal(self):

        self.botonE = self.builder.get_object("button1")
        self.botonE.set_sensitive(False)

        self.botonD = self.builder.get_object("Detalle2_button")
        self.botonD.set_sensitive(False)

        self.botonR = self.builder.get_object("Reemplazar_button")
        self.botonR.set_sensitive(False)

        self.botonElim = self.builder.get_object("Eliminar_button")
        self.botonElim.set_sensitive(False)


        #Logo Empresa
        self.Logo_area = self.builder.get_object("Logo_Area")
        self.pixbuf1 = Pixbuf.new_from_file_at_size('C:\\Users\\charl\\Documents\\Aguas Machala\\Inventario\\Base de Datos\\Aguas_Logo.png', 200, 100)
        self.image1 = Gtk.Image()
        self.image1.set_from_pixbuf(self.pixbuf1)
        #Colocar Imagen en su lugar
        self.Logo_area.add(self.image1)
        self.Logo_area.show_all()

        #Desplegar Datos
        self.treeview_ventanaP = self.builder.get_object("ventanaP_treeview")
        #self.filter_item
        self.treeview_ventanaP.set_model(self.filter_item)
        
        self.render_text = Gtk.CellRendererText()
        self.render_text_item = Gtk.CellRendererText()
        column_Item = Gtk.TreeViewColumn("Item", self.render_text_item, text = 1)
        self.treeview_ventanaP.append_column(column_Item)

        column_Marca = Gtk.TreeViewColumn("Marca", self.render_text, text = 2)
        self.treeview_ventanaP.append_column(column_Marca)

        column_NSerie = Gtk.TreeViewColumn("NSerie", self.render_text, text = 3)
        self.treeview_ventanaP.append_column(column_NSerie)

        column_Cantidad = Gtk.TreeViewColumn("Cantidad", self.render_text, text = 4)
        self.treeview_ventanaP.append_column(column_Cantidad)

        column_Lugar = Gtk.TreeViewColumn("Lugar", self.render_text, text = 5)
        self.treeview_ventanaP.append_column(column_Lugar)

        
        
        #text_dumb = 1
        #cursor_headers_databaseB = db.cursor()
        #cursor_headers_databaseB.execute('''SELECT Item, Manufacturer, NSerie, Cantidad, Lugar FROM Tablas''')
        #for row in cursor_headers_databaseB.description:
            #column_catalog = Gtk.TreeViewColumn(row[0], self.render_text, text=text_dumb)   
            #self.treeview_ventanaP.append_column(column_catalog)
            #text_dumb += 1
       
         
        

        #Ventana
        self.window = self.builder.get_object("Ventana_Principal")
        self.window.show()


        #Seleccionar un equipo para ver detalles, editar, eliminar o mandar a bodega
        tree_selection_ventanaP = self.treeview_ventanaP.get_selection()
        tree_selection_ventanaP.connect("changed", self.onSelectionChanged)
    
    def Aceptar_cerrar(self, widget):
        self.aceptarwindow.hide()

    def Error_cerrar(self, widget):
        self.errorwindow.hide()  #better to use hide

    def Cerrar_boton(self, widget):
        Gtk.main_quit()
        db.close()

    def cerrar_ventanaI(self, object, data = None):
        self.ventana_ingreso.hide()
        return True

    def cerrar_ventanaD(self, object, data = None):
        self.ventanaD.hide()
        return True
    
    def cerrar_ventanaE(self, object, data = None):
        self.ventana_editar.hide()
        return True
    def cerrar_ventanaR(self, object, data = None):
        self.ventana_reemplazar.hide()
        return True

    def Cerrar_ventana_principal(self, object, data=None):
        Gtk.main_quit()
        db.close()
if __name__=="__main__":
    main=MyWindow()
    Gtk.main()