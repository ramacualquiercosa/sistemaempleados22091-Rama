from flask import Flask #Importa el framework Flask (una librería de Python que nos permite trabajar con el modelo MVC)
from flask import render_template , request , redirect #Importa el renderizadores de templates de Flask para poder realizar funciones en la vista
from flaskext.mysql import MySQL #Importa la libreria de MySQL para que el controlador se pueda comunicar con la base de datos
from datetime import datetime #Importa el modulo de dia/hora
import os #Importa el modulo del sistema operativo para que podamos a futuro modificar las fotos cargadas
#-----------------------------------------------------------------------------------------------------------------------
app=Flask(__name__)#Inicio de la app
#-----------------------------------------------------------------------------------------------------------------------
#CONFIGURACION DE LA BASE DE DATOS A USAR
mysql = MySQL()#
app.config['MYSQL_DATABASE_HOST'] = 'localhost'#Determina el host de la base de datos
app.config['MYSQL_DATABASE_USER'] = 'root'#Determina el usuario de la base de datos
app.config['MYSQL_DATABASE_PASSWORD'] = ''#Determina la contraseña de acceso a la base de datos
app.config['MYSQL_DATABASE_DB'] = 'sistema22091'#Determina el nombre de la base de datos
mysql.init_app(app)#

CARPETA = os.path.join('uploads') #guarda en una variable el comando del sistema para manipular el archivo guardado en uploads (en este caso, las fotos)
app.config['CARPETA']=CARPETA #Cada vez que hagamos referencia a "CARPETA", vamos a estar hablando de app.config['CARPETA']
#------------------------------------------------------------------------------------------------------------------------
#MUESTRA LOS REGISTRSO DE LA BASE DE DATOS///Enrutamiento de la raiz (Index)
@app.route("/")#Redirige a la ruta asignada. Ej: @app.route(/Juanca), nos redirige al template(vista) de Juanca
def index():#Se suele poner el nombre representativo de la ruta donde va a redireccionar 
    sql = "SELECT * FROM `empleados`;"#Crea un objeto SQL que contiene el Query que queremos realizar//Muestra todos los datos
    conn = mysql.connect()#Abre la conección con la base de datos
    cursor=conn.cursor()#Crea un cursor que lleva dentro el Query para ejecutarlo
    cursor.execute(sql)#Ejecuta el cursor, con el Query que definimos (en este caso SELECT * FROM empleados;) 
    empleados =  cursor.fetchall()#crea en la variable "empleados" y la llena con una tupla general que contiene tuplas individiales por cada registro
    print(empleados)
    conn.commit()#Estabiliza en la base de datos los cambios realizados  
    return render_template('empleados/index.html' , empleados=empleados)#al retornar, se le envía a la vista la varia "empleados", que contine una tupla con todos los datos de la base de datos, para que sean mostrados
    #Retorna renderización de template de la ruta a donde queremos ir, en este caso el INDEX
    #Flask siempre busca los templates en una carpeta que debemos crear con el mismo nombre
    #El comando app.raute() permite que le digamos al controlador a que ruta de la vista queremos que redireccione
#-----------------------------------------------------------------------------------------------------------------------
#CREACION DE REGISTRO///Enrutamiento a la página "Create"
@app.route("/create")#Redirige a la página create
def create():#Define la función que va a cargar cada registro en la base de datos
    return render_template('empleados/create.html')#Retorna renderización de template de la ruta a donde queremos ir, en este caso el CREATE
    #Retorna renderización de template de la ruta a donde queremos ir, en este caso el CREATE

@app.route("/store" , methods=['POST'])#Procesa la información del formulario a través del metodo POST
def storage():#Definimos la función para guardar
    _nombre = request.form['txtNombre']#Procesa a través de una peticion el valor "txtNombre" y lo guarda en una variable
    _correo = request.form['txtCorreo']#Procesa a través de una peticion el valor "txtCorreo" y lo guarda en una variable
    _foto   = request.files['txtFoto']#Procesa a través de una peticion el valor "txtFoto" y lo guarda en una variable

    now   =  datetime.now()#Creamos variable donde se guardan todos los datos del tiempo (dias, horas, minutos, etc) 
    ahora =  now.strftime("%Y%H%M%S")#Guardamos en una variable "ahora" el tiempo en formato string
    nuevoNombreFoto = ''#Define el nombre de foto como vació por si no se carga foto al momento de crear el registro
    
    if _foto.filename != '':#Comprobamos que la foto esté cargada, es decir, preguntamos "Si foto.filename es diferente a vacío"
        nuevoNombreFoto = ahora + _foto.filename #Le cambio el nombre a la foto agregando el año/hora/minutos/segundos en que se carga
        _foto.save('uploads/' + nuevoNombreFoto) #Guardo la foto en la carpeta "Uploads" con el nuevo nombre

    sql = "INSERT INTO `empleados` (`id`, `nombre`, `correo`, `foto`) VALUES (NULL,%s,%s,%s );"#defino el Query donde quedan pendiente a través de "%s" los datos que voy a insertar
    datos=(_nombre, _correo, nuevoNombreFoto)#Determina que datos se van a insertar en los parametros que dejamos pendiente en el Query usando "%s"
    #Una vez que defino el Query y los datos que van a llenarlo, posteriormente se vinculan al ejecutar el cursor
                          
    conn = mysql.connect()#Abre la conección con la base de datos
    cursor=conn.cursor()#Crea un cursor que lleva dentro el Query para ejecutarlo
    cursor.execute(sql, datos)#Ejecuta el cursor, con el Query que definimos. Asimismo, vincula los datos que dejamos pendientes del Query (%s) con las que se guardaron en la variable "datos"
    conn.commit()#Estabiliza en la base de datos los cambios realizados  
    return render_template('empleados/index.html')#Retorna renderización de template de la ruta a donde queremos ir, en este caso el INDEX
#-------------------------------------------------------------------------------------------------------------------------
#ELIMINACION DE REGISTRO
@app.route("/destroy/<int:id>")#Elimina registro del modelo y devuelve a la vista el registro actualizado con la modificacion de la base de datos///recibe a traves del parametro "<int:id>" el id del elemento a eliminar
def destroy(id):#Definimos la función//toma el parametro id del enrutamiento previo
    conn = mysql.connect()#Abre la conección con la base de datos
    cursor=conn.cursor()#Crea un cursor que lleva dentro el Query para ejecutarlo
    cursor.execute("SELECT foto FROM empleados WHERE id =%s",id)#Ejecuta el Query en el cual se consulta a la base de datos cual es el nombre de la foto que se relaciona con el id del registro a eliminar
    fila=cursor.fetchall()#Guardamos el Query que ejecuta el cursor en una variable, utilizando el metodo fetchall para que lo convierta en una tupla dentro de otra 
    print(fila[0][0])#Se utiliza de prueba, para ver que nos devuelve "fila" en la terminal. Notese que se hace referencia a la posición 0 de la primera tupla y a la posición 0 de la tupla que la segunda (que se encuentra contenida dentro de la primera)
    os.remove(os.path.join(app.config['CARPETA'],fila[0][0] ))#Metodo que permite borrar la foto a la que hace referencia el nombre contenido en "fila"
    cursor.execute("DELETE FROM empleados WHERE id=%s",(id))#Ejecuta el cursor, con el Query que definimos (en este caso "DELETE FROM empleados WHERE id=%s;". Notese que el parametro de id contiene "%s", quedando pendiente. Esto se resuelve pasandole a continuación el parametro a llenar (en este caso es "(id)", antecedido de una coma y tomandolo del parametro de la propia función) 
    conn.commit()#Estabiliza en la base de datos los cambios realizados 
    return redirect('/')#Redirige a la pagina principal con las modificaciones realizadas
    #el metodo redirect recibe del modelo una respuesta (en este caso una la eliminación de un registro) y refresca el contenido de la página principal y nos redirige a la misma, adviritiendo la acción y mostrando solo los registros existentes en la base de datos
#-------------------------------------------------------------------------------------------------------------------------
#EDICION DE REGISTROS///Enrutamiento a la página "edit" 
#Tiene dos pasos: a) Enviar a un formulario en la vistalos datos del registro a modificar en la base de datos; b) procesar el formulario y guardar en la base de datos los cambios.
#a) CARGA DE FORMULARIO CON DATOS PARA EDITAR
@app.route("/edit/<int:id>")#devuelve a la vista la pagina de carga de datos para que sean modificados///recibe a traves del parametro "<int:id>" el id del elemento a editar
def edit(id):#Definimos la función//toma el parametro id del enrutamiento previo
    conn = mysql.connect()#Abre la conección con la base de datos
    cursor=conn.cursor()#Crea un cursor que lleva dentro el Query para ejecutarlo
    cursor.execute("SELECT * FROM empleados WHERE id =%s", (id))#Ejecuta el cursor, con el Query que definimos (en este caso "SELECT * FROM empleados WHERE id =%s". Notese que el parametro de id contiene "%s", quedando pendiente. Esto se resuelve pasandole a continuación el parametro a llenar (en este caso es "(id)", antecedido de una coma y tomandolo del parametro de la propia función) 
    empleados =  cursor.fetchall()#crea en la variable "empleados" y la llena con una tupla general que contiene tuplas individiales por cada registro
    print(empleados)#Se hace un print para testear si llega la información solamente
    conn.commit()#Estabiliza en la base de datos los cambios realizados 
    return render_template('empleados/edit.html' , empleados=empleados)#Retorna renderización de template de la ruta a donde queremos ir, en este caso el EDIT
#b) POCESADOR DE FORMULARIO CON MODIFICACIONES
@app.route("/update" , methods=['POST'])#Procesa el formulario que viene desde la vista para poder EDITAR los registros existentes, por medio del metodo POST
def update():#Definimos la función para editar
    _nombre = request.form['txtNombre']#Procesa a través de una peticion el valor "txtNombre" y lo guarda en una variable
    _correo = request.form['txtCorreo']#Procesa a través de una peticion el valor "txtCorreo" y lo guarda en una variable
    _foto   = request.files['txtFoto']#Procesa a través de una peticion el valor "txtFoto" y lo guarda en una variable
    _id     = request.form['txtId']#Procesa a través de una peticion el valor "txtId" y lo guarda en una variable
 
    sql = "UPDATE empleados SET nombre=%s , correo=%s WHERE id=%s;"#defino el Query para actualizar el registro, donde quedan pendiente a través de "%s" los datos que voy a modificar
    datos = (_nombre ,_correo,_id)#Determina que datos se van a insertar en los parametros que dejamos pendiente en el Query usando "%s"
    conn = mysql.connect()#Abre la conección con la base de datos
    cursor=conn.cursor()#Crea un cursor que lleva dentro el Query para ejecutarlo

    now   =  datetime.now()#Creamos variable donde se guardan todos los datos del tiempo (dias, horas, minutos, etc)
    ahora =  now.strftime("%Y%H%M%S")#Guardamos en una variable "ahora" el tiempo en formato string
    nuevoNombreFoto = ''#Define el nombre de foto como vació por si no se carga foto al momento de crear el registro
    
    if _foto.filename != '':#Comprobamos que la foto esté cargada, es decir, preguntamos "Si foto.filename es diferente a vacío"
        nuevoNombreFoto = ahora + _foto.filename#Le cambio el nombre a la foto agregando el año/hora/minutos/segundos en que se carga
        _foto.save('uploads/' + nuevoNombreFoto)#Guardo la foto en la carpeta "Uploads" con el nuevo nombre

        cursor.execute("SELECT foto FROM empleados WHERE id =%s",_id)#Ejecuta el Query en el cual se consulta a la base de datos cual es el nombre de la foto que se relaciona con el id del registro a modificar
        fila=cursor.fetchall()#Guardamos el Query que ejecuta el cursor en una variable, utilizando el metodo fetchall para que lo convierta en una tupla dentro de otra 

        print(fila[0][0])#Se utiliza de prueba, para ver que nos devuelve "fila" en la terminal. Notese que se hace referencia a la posición 0 de la primera tupla y a la posición 0 de la tupla que la segunda (que se encuentra contenida dentro de la primera)
        os.remove(os.path.join(app.config['CARPETA'],fila[0][0] ))#Metodo que permite borrar la foto a la que hace referencia el nombre contenido en "fila"
        cursor.execute("UPDATE empleados SET foto=%s WHERE id=%s ",(nuevoNombreFoto , _id))#Actualizo en la base de datos el nombre de la nueva foto, correspondiente al id proporcionado por la variable "_id"
        conn.commit()#Estabiliza en la base de datos los cambios realizados

    cursor.execute(sql, datos)#Ejecuta el cursor, con el Query que definimos. Asimismo, vincula los datos que dejamos pendientes del Query (%s) con las que se guardaron en la variable "datos"
    conn.commit()#Estabiliza en la base de datos los cambios realizados
    return redirect('/')#Redirige a la pagina principal con las modificaciones realizadas



if __name__ =='__main__':#Punto de entrada de la app
    app.run(debug=True)#Corre la app en modo debug, redirigiendo a app=Flask(__name__), donde inicia el programa