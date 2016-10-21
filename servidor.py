# -*- coding: utf-8 -*-
import sys
from random import randint
from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtGui import *
from PyQt4.QtCore import *

from xmlrpc.server import SimpleXMLRPCServer
clase = uic.loadUiType("servidor.ui")[0]
		
class Servidor(QtGui.QMainWindow, clase): 
	def __init__(self, parent= None):

		#Al principio escondemos el boton terminar_juego
		#Declaramos KeyPressEvent para los controles
		#Asociamos las acciones del boton termina_juego con el metodo fin que termina el juego
		#Asociamos las acciones del boton inicia_juego con el metodo inicia que se basa en el texto del boton inicia_juego
		#Tomamos los valores de spin_column y spin_fila para modificar la tableWidget
		#Tomamos el valor spin_espera para asegurar la velocidad/tiempo de espera
		QtGui.QMainWindow.__init__(self)  
		self.setupUi(self)
		self.tableWidget.horizontalHeader().setResizeMode(QHeaderView.Stretch)
		self.tableWidget.verticalHeader().setResizeMode(QHeaderView.Stretch)  
		self.termina_juego.hide()
		self.tableWidget.keyPressEvent= self.keyPressEvent
		self.termina_juego.clicked.connect(self.fin)
		self.inicia_juego.clicked.connect(self.inicia)
		self.spin_fila.valueChanged.connect(self.tam_filas)
		self.spin_column.valueChanged.connect(self.tam_columnas)
		self.spin_espera.valueChanged.connect(self.espera_ms)
		self.btn_iniciaserv.clicked.connect(self.serv)
		self.id=0
		self.color=[0,0,0]
		self.lista_snakes=[]
		self.origin_snake_creada=False		

	def serv(self):		
		self.servidr= SimpleXMLRPCServer((self.line_url.text(), self.spin_puerto.value()), allow_none= True)
		self.servidr.register_function(self.ping)
		self.servidr.register_function(self.yo_juego)
		self.servidr.register_function(self.estado_juego)
		self.servidr.register_function(self.camba_direccion)
		self.servidr.timeout= 0
		
		#Usamos timer_serv para marcar el timepo de espera, evitando que se lagee ._.)""7
		self.timer_serv= QTimer(self)
		self.timer_serv.timeout.connect(self.recibe_orden)
		self.timer_serv.start(99)

	#Usamos recibe_orden para recibir mas de una funciones
	def recibe_orden(self):
		self.servidr.handle_request()
	
	def ping(self):
		return "¡pong!"

	#Devolvemis la id, y el color del snake principal(el que aparece)
	def yo_juego(self):
		self.crea_snake()
		return {"id": self.id, "color":{"r": self.color[0], "g": self.color[1], "b": self.color[2]}}

	#Cambiamos la direccion a partir de la lista de snakes, la busca y si la encuentra hace el cambio
	def camba_direccion(self, num, x):
		for i in range(len(self.lista_snakes)):
			if self.lista_snakes[i][0]==x:
				self.lista_snakes[i][0]=int(num)
	#Devuelve toda la lista de snakes, el tamanio de filas y columnas, y el tiempo de espera
	def estado_juego(self):
		return {"espera": self.spin_espera.value(), "tamX": self.tableWidget.columnCount(), "tamY": self.tableWidget.rowCount(), "viboras": self.lista_snakes} 

	def espera_ms(self, n):
		self.timer.setInterval(n)

	#Modifica tamanio de filas
	def tam_filas(self, x):
		self.tableWidget.setRowCount(x)

	#Modifica tamanio de columnas
	def tam_columnas(self, y):
		self.tableWidget.setColumnCount(y)  


	#Metodo inicia, se basa en el texto del boton de inicio, si inciamos un nuevo juego, si se va a pausar o se va a reanudar
	def inicia(self):									
		if self.inicia_juego.text()=="Inicia Juego":
			self.inicia_juego.setText("Pausa")
			self.termina_juego.show() 
			self.apunta_arriba=False
			self.apunta_abajo=True
			self.apunta_derecha=True
			self.apunta_izquierda=True

			self.crea_snake()

			self.ruta="Abajo"

			self.timer= QTimer(self)
			self.timer.timeout.connect(self.chunche_mover_snake)
			self.timer.start(100)

		elif self.inicia_juego.text()=="Pausa":
			self.timer.stop()			
			self.inicia_juego.setText("Reanuda")
		else:			
			self.timer.start(self.spin_espera.value())
			self.inicia_juego.setText("Pausa")

	#Para crear una vivora nos basamos en si la primera ya fue creada, si ya lo ha sido solo hacemos las propiedades de otro snake que no aparezca en la tablewidget(por ahora "._.)
	def crea_snake(self):
		if not self.origin_snake_creada:			
			self.color[0]=randint(0,255)
			self.color[1]=randint(0,255)
			self.color[2]=randint(0,255)
			self.snake_1=QTableWidgetItem()
			self.snake_2=QTableWidgetItem()
			self.snake_3=QTableWidgetItem()
			self.snake_4=QTableWidgetItem()
			self.snake_1.setBackgroundColor(QtGui.QColor(self.color[0], self.color[1], self.color[2]))
			self.snake_2.setBackgroundColor(QtGui.QColor(self.color[0], self.color[1], self.color[2]))
			self.snake_3.setBackgroundColor(QtGui.QColor(self.color[0], self.color[1], self.color[2]))
			self.snake_4.setBackgroundColor(QtGui.QColor(self.color[0], self.color[1], self.color[2]))			
			self.tableWidget.setItem(3,0,self.snake_1)
			self.tableWidget.setItem(2,0,self.snake_2)
			self.tableWidget.setItem(1,0,self.snake_3)  	
			self.tableWidget.setItem(0,0,self.snake_4)
			self.origin_snake_creada=True

			#Posicion inicial de la vibora
			self.snake1=[3,0]
			self.snake2=[2,0]
			self.snake3=[1,0]
			self.snake4=[0,0]	

			self.id+=1		
			self.dir=2				

			self.lista_snakes.append((self.id, {"dir": self.dir, "color":self.color, "camino":[self.snake1, self.snake2, self.snake3, self.snake4]}))

		else:
			self.color2=[0,0,0]
			self.color2[0]=randint(0,255)
			self.color2[1]=randint(0,255)
			self.color2[2]=randint(0,255)
			self.id+=1
			self.dir=2

			self.snake1x=[randint(0,self.tableWidget.rowCount()),     randint(0,self.tableWidget.columnCount())]
			self.snake2x=[(self.snake1x[0]-1)%self.tableWidget.rowCount(), randint(0,self.tableWidget.columnCount())]
			self.snake3x=[(self.snake1x[0]-2)%self.tableWidget.rowCount(), randint(0,self.tableWidget.columnCount())]
			self.snake4x=[(self.snake1x[0]-3)%self.tableWidget.rowCount(), randint(0,self.tableWidget.columnCount())]
			self.lista_snakes.append((self.id, {"dir":self.dir, "color":self.color2, "camino":[self.snake1x, self.snake2x, self.snake3x, self.snake4x]}))

			
	#Metodo para mover la vibora, se basa en el string ruta, ademas de ver si podemos ir arriba, a bajo, derecha o izquierda en
	#la direccion en la que estamos
	#Para aparecer del otro lado si se sale del tableWidget usamos la reasignacion en base al modulo del numero de columnas o filas
	#Para ver si podemos movernos hacia donde queremos checamos los valores apunta_derecha, apunta_izquierda, apunta_arriba_ apunta_abajo 
	def chunche_mover_snake(self):		

		if self.ruta=="Arriba":
			self.tableWidget.takeItem(self.snake1[0],self.snake1[1])
			self.tableWidget.takeItem(self.snake2[0],self.snake2[1])
			self.tableWidget.takeItem(self.snake3[0],self.snake3[1])
			self.tableWidget.takeItem(self.snake4[0],self.snake4[1])

			self.snake_1=QTableWidgetItem()
			self.snake_2=QTableWidgetItem()
			self.snake_3=QTableWidgetItem()
			self.snake_4=QTableWidgetItem()

			self.snake_1.setBackgroundColor(QtGui.QColor(self.color[0], self.color[1], self.color[2]))
			self.snake_2.setBackgroundColor(QtGui.QColor(self.color[0], self.color[1], self.color[2]))
			self.snake_3.setBackgroundColor(QtGui.QColor(self.color[0], self.color[1], self.color[2]))
			self.snake_4.setBackgroundColor(QtGui.QColor(self.color[0], self.color[1], self.color[2]))
		
			if self.apunta_arriba==True:
				self.snake4[0]=self.snake3[0]
				self.snake3[0]=self.snake2[0]
				self.snake2[0]=self.snake1[0]
				self.snake1[0]=(self.snake1[0]-1)%self.tableWidget.rowCount()

				self.apunta_derecha=True
				self.apunta_izquierda=True
				self.apunta_abajo=False

				self.snake4[1]=self.snake3[1]
				self.snake3[1]=self.snake2[1]
				self.snake2[1]=self.snake1[1]

				self.dir=0	

			self.tableWidget.setItem(self.snake1[0],self.snake1[1], self.snake_1)
			self.tableWidget.setItem(self.snake2[0],self.snake2[1], self.snake_2)
			self.tableWidget.setItem(self.snake3[0],self.snake3[1], self.snake_3)  	
			self.tableWidget.setItem(self.snake4[0],self.snake4[1], self.snake_4)

		elif self.ruta=="Abajo":
			self.tableWidget.takeItem(self.snake1[0],self.snake1[1])
			self.tableWidget.takeItem(self.snake2[0],self.snake2[1])
			self.tableWidget.takeItem(self.snake3[0],self.snake3[1])
			self.tableWidget.takeItem(self.snake4[0],self.snake4[1])

			if self.apunta_abajo==True:
				self.snake4[0]=self.snake3[0]
				self.snake3[0]=self.snake2[0]
				self.snake2[0]=self.snake1[0]
				self.snake1[0]=(self.snake1[0]+1)%self.tableWidget.rowCount() 

				self.apunta_derecha=True
				self.apunta_izquierda=True
				self.apunta_arriba=False

				self.snake4[1]=self.snake3[1]
				self.snake3[1]=self.snake2[1]
				self.snake2[1]=self.snake1[1]	

				self.dir=2

			self.snake_1=QTableWidgetItem()
			self.snake_2=QTableWidgetItem()
			self.snake_3=QTableWidgetItem()
			self.snake_4=QTableWidgetItem()

			self.snake_1.setBackgroundColor(QtGui.QColor(self.color[0], self.color[1], self.color[2]))
			self.snake_2.setBackgroundColor(QtGui.QColor(self.color[0], self.color[1], self.color[2]))
			self.snake_3.setBackgroundColor(QtGui.QColor(self.color[0], self.color[1], self.color[2]))
			self.snake_4.setBackgroundColor(QtGui.QColor(self.color[0], self.color[1], self.color[2]))

			self.tableWidget.setItem(self.snake1[0],self.snake1[1], self.snake_1)
			self.tableWidget.setItem(self.snake2[0],self.snake2[1], self.snake_2)  		
			self.tableWidget.setItem(self.snake3[0],self.snake3[1], self.snake_3)  	
			self.tableWidget.setItem(self.snake4[0],self.snake4[1], self.snake_4)

		elif self.ruta=="Derecha":
			self.tableWidget.takeItem(self.snake1[0],self.snake1[1])
			self.tableWidget.takeItem(self.snake2[0],self.snake2[1])
			self.tableWidget.takeItem(self.snake3[0],self.snake3[1])
			self.tableWidget.takeItem(self.snake4[0],self.snake4[1])
			if self.apunta_derecha==True:
				self.snake4[1]=self.snake3[1]
				self.snake3[1]=self.snake2[1]
				self.snake2[1]=self.snake1[1]
				self.snake1[1]=(self.snake1[1]+1)%self.tableWidget.columnCount()

				self.apunta_arriba=True
				self.apunta_abajo=True				
				self.apunta_izquierda=False

				self.snake4[0]=self.snake3[0]
				self.snake3[0]=self.snake2[0]
				self.snake2[0]=self.snake1[0]

				self.dir= 1

			self.snake_1=QTableWidgetItem()
			self.snake_2=QTableWidgetItem()
			self.snake_3=QTableWidgetItem()
			self.snake_4=QTableWidgetItem()

			self.snake_1.setBackgroundColor(QtGui.QColor(self.color[0], self.color[1], self.color[2]))
			self.snake_2.setBackgroundColor(QtGui.QColor(self.color[0], self.color[1], self.color[2]))
			self.snake_3.setBackgroundColor(QtGui.QColor(self.color[0], self.color[1], self.color[2]))
			self.snake_4.setBackgroundColor(QtGui.QColor(self.color[0], self.color[1], self.color[2]))

			self.tableWidget.setItem(self.snake1[0],self.snake1[1], self.snake_1)
			self.tableWidget.setItem(self.snake2[0],self.snake2[1], self.snake_2)  		
			self.tableWidget.setItem(self.snake3[0],self.snake3[1], self.snake_3)  	
			self.tableWidget.setItem(self.snake4[0],self.snake4[1], self.snake_4)
		else:
			self.tableWidget.takeItem(self.snake1[0],self.snake1[1])
			self.tableWidget.takeItem(self.snake2[0],self.snake2[1])
			self.tableWidget.takeItem(self.snake3[0],self.snake3[1])
			self.tableWidget.takeItem(self.snake4[0],self.snake4[1])

			if self.apunta_izquierda==True:
				self.snake4[1]=self.snake3[1]
				self.snake3[1]=self.snake2[1]
				self.snake2[1]=self.snake1[1]
				self.snake1[1]=(self.snake1[1]-1)%self.tableWidget.columnCount()
				
				self.snake4[0]=self.snake3[0]
				self.snake3[0]=self.snake2[0]
				self.snake2[0]=self.snake1[0]				
				
				self.apunta_arriba=True
				self.apunta_abajo=True
				self.apunta_derecha=False

				self.dir=3						

			self.snake_1=QTableWidgetItem()
			self.snake_2=QTableWidgetItem()
			self.snake_3=QTableWidgetItem()
			self.snake_4=QTableWidgetItem()

			self.snake_1.setBackgroundColor(QtGui.QColor(self.color[0], self.color[1], self.color[2]))
			self.snake_2.setBackgroundColor(QtGui.QColor(self.color[0], self.color[1], self.color[2]))
			self.snake_3.setBackgroundColor(QtGui.QColor(self.color[0], self.color[1], self.color[2]))
			self.snake_4.setBackgroundColor(QtGui.QColor(self.color[0], self.color[1], self.color[2]))

			self.tableWidget.setItem(self.snake1[0],self.snake1[1], self.snake_1)
			self.tableWidget.setItem(self.snake2[0],self.snake2[1], self.snake_2)  		
			self.tableWidget.setItem(self.snake3[0],self.snake3[1], self.snake_3)  	
			self.tableWidget.setItem(self.snake4[0],self.snake4[1], self.snake_4)

	#Metodo keyPressEvent para asignar la direccion de la vibora, nos basamos en la tecla presionada y en que direccion puede 
	#moverse la vibora
	def keyPressEvent(self, k):
		if k.key()== QtCore.Qt.Key_Right and self.apunta_derecha:
			self.ruta="Derecha"
			self.chunche_mover_snake()			
	
		elif k.key()== QtCore.Qt.Key_Left and self.apunta_izquierda:
			self.ruta="Izquierda"
			self.chunche_mover_snake()				

		elif k.key()== QtCore.Qt.Key_Up and self.apunta_arriba:
			self.ruta="Arriba"
			self.chunche_mover_snake()				

		elif k.key()== QtCore.Qt.Key_Down and self.apunta_abajo:
			self.ruta="Abajo"
			self.chunche_mover_snake()				

	#Metodo para ver si la vibora esta viva,
	#aunque en una vibora de 4 o menos celdas nunca pueda matarse ._.)7 (pobres u-u)
	def vive(self):
		#Si la cola y la cabeza chocan
		 return not(self.snake1[1]==self.snake4[1] and self.snake1[0]==snake4[0])		
		 
	#Metodo para finalizar el juego, toma las celdas, detiene el timer, cambia el texto del boton de inicio y esconde el 
	#boton termina_juego de nuevo
	def fin(self):
		self.tableWidget.takeItem(self.snake1[0], self.snake1[1])
		self.tableWidget.takeItem(self.snake2[0], self.snake2[1])
		self.tableWidget.takeItem(self.snake3[0], self.snake3[1])
		self.tableWidget.takeItem(self.snake4[0], self.snake4[1])
		self.timer.stop()
		self.termina_juego.hide()
		self.inicia_juego.setText("Inicia Juego")
		self.id=0	
		self.dir=2
		self.origin_snake_creada=False
	

app= QtGui.QApplication(sys.argv)
Ventana= Servidor()
Ventana.show()
app.exec_()