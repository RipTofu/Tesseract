import pytesseract
import cv2
from matplotlib import pyplot as plt
from pytesseract import Output

myconfig = r"--psm 11 --oem 3 -l spa"

'''
data = 
{ 
level: [1, 2, 3, 4, 5, 5, 5...], 
page_num: []
...
text: ['text', 'text'...]
}
'''


#Lectura de imágen y dimensiones

def encontrar_superior(data, index, tope_categoria, limites_busqueda):
    print("#########buscando palabra sobre:", data['text'][index], "###########")
    ancho_label = data['width'][index]
    altura_label = data['height'][index]
    y_label = data['top'][index]
    x_label = data['left'][index]
    for i in range(len(data['level'])):
        if i in limites_busqueda:
            print("Buscando:", data['text'][i], "\n altura: ", data['top'][i], "| altura_label, : ", y_label - altura_label , "| tope categoria: ", tope_categoria)
            if (data['top'][i] < y_label - altura_label) and (data['top'][i] > tope_categoria): # Busca cualquier palabra entre el límite superior del texto y el límite inferior de la categoría.
                superior = data['text'][i]
    print("Palabra superior a ", data['text'][index], ": ", superior)

def palabras_clave(data):
    datos_solicitud = {
        "SOLICITUD DE INTERCONSULTA O DERIVACIÓN": {
            "N° Folio": ["", 0, 0],
            "N° de Orden": ["", 0, 0],
            "Fecha Solicitud": ["", 0, 0],
            "Servicio de Salud": ["", 0, 0],
            "Establecimiento": ["", 0, 0]
        },
        "DATOS DEL [DE LA] PACIENTE": {
            "Primer Apellido": ["", 0, 0],
            "Segundo Apellido": ["", 0, 0],
            "Nombres": ["", 0, 0],
            "RUN": ["", 0, 0],
            "Si es recién nacido, RUN de padre o madre beneficiario": ["", 0, 0],
            "Número de Ficha": ["", 0, 0],
            "Sexo": ["", 0, 0],
            "Fecha de Nacimiento": ["", 0, 0],
            "Edad": ["", 0, 0],
            "Domicilio (calle, número, número interior, bloque (block), villa, localidad": ["", 0, 0],
            "Comuna de residencia": ["", 0, 0],
            "Teléfono": ["", 0, 0],
            "Teléfono Móvil": ["", 0, 0],
            "Teléfono Laboral": ["", 0, 0],
            "Teléfono Contacto": ["", 0, 0],
            "Nombre Padre": ["", 0, 0],
            "Nombre Madre": ["", 0, 0]
        },
        "DATOS CLINICOS": {
            "Se deriva para atención en": ["", 0, 0],
            "Servicio": ["", 0, 0],
            "Especialidad": ["", 0, 0],
            "Se envía a consulta para": ["", 0, 0],
            "Hipótesis diagnóstica o diagnóstico": ["", 0, 0],
            "Especificar problema": ["", 0, 0],
            "Prioridad": ["", 0, 0],
            "Fundamentos del diagnóstico": ["", 0, 0],
            "Exámenes realizados": ["", 0, 0],
            "Observaciones": ["", 0, 0]
        },
        "DATOS DEL (DE LA) PROFESIONAL": {
            "Primer Apellido": ["", 0, 0],
            "Segundo Apellido": ["", 0, 0],
            "Nombres": ["", 0, 0],
            "RUN": ["", 0, 0]
        }
    }

def mostrar_datos_completos(data):
    indices_palabras_encontradas = [] #Lista de indices de palabras a revisar, todas aquellas con confianza superior a 80.
    for i in range(len(data['text'])):
        if float(data['conf'][i]) > 80:
            print(data['text'][i], " | Coordenadas: ", data['left'][i],"x, ", data['top'][i], "y")
            indices_palabras_encontradas.append(i)
    palabras_encontradas = len(indices_palabras_encontradas) # Total de palabras encontradas
    print("Si")
    for posicion in indices_palabras_encontradas:
        if data['text'][posicion] == 'PACIENTE':
            tope_superior = data['top'][posicion]
        if data['text'][posicion] == 'Primer':
            encontrar_superior(data, posicion, tope_superior, indices_palabras_encontradas)

def refinar_letra(img):
    import numpy as np
    img = cv2.bitwise_not(img)
    kernel = np.ones((1, 1), np.uint8)
    img = cv2.erode(img, kernel, iterations=1)
    img = cv2.bitwise_not(img)
    cv2.imwrite("temp/erosion.jpg", img)

def expandir_letra(img):
    import numpy as np
    img = cv2.bitwise_not(img)
    kernel = np.ones((1, 1), np.uint8)
    img = cv2.dilate(img, kernel, iterations=1)
    img = cv2.bitwise_not(img)
    cv2.imwrite("temp/expansion.jpg", img)
    return img

def reduccion_de_ruido(img):
    import numpy as np
    kernel = np.ones((1, 1), np.uint8)
    img = cv2.dilate(img, kernel, iterations=1)
    kernel = np.ones((1, 1), np.uint8)
    img = cv2.erode(img, kernel, iterations=1)
    img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)
    img = cv2.medianBlur(img, 3)
    cv2.imwrite("temp/no_ruido.jpg", img)

def inversion(img):
    invertido = cv2.bitwise_not(img)
    cv2.imwrite("temp/inverted.jpg", invertido)

def binarizacion(img):
    gris = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cv2.imwrite("temp/gris.jpg", gris)
    imgGris = cv2.imread("temp/gris.jpg")  # Genera la imagen con threshold
    thresh, bnw_img = cv2.threshold(imgGris, 127, 255, cv2.THRESH_BINARY)
    cv2.imwrite("temp/bnw.jpg", bnw_img)

def diagrama_caja_texto(data, img):  # Recibe el diccionario completo de datos
    palabras_encontradas = 0
    for i in range(len(data['text'])):
        if float(data['conf'][i]) > 80: # Limitación del nivel de confianza
            palabras_encontradas += 1
            (x, y, width, height) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
            img = cv2.rectangle(img, (x, y), (x+width, y+height), (0,255,0), 2)
            img = cv2.putText(img, data['text'][i], (x, y+height+20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2, cv2.LINE_AA)
            print(data['text'][i])
    cv2.imshow("img", img)
    print("encontradas:", palabras_encontradas)
    cv2.waitKey(0)

def diagrama_caja(img):
    h, w, _ = img.shape
    box = pytesseract.image_to_boxes(img, config=myconfig)
    for i in box.splitlines():
        i = i.split(" ")
        img = cv2.rectangle(img, (int(i[1]), h - int(i[2])), (int(i[3]), h - int(i[4])), (0, 255, 0), 2)

    cv2.imshow("img", img)
    cv2.waitKey(0)


# Primera imágen
img = cv2.imread("SICFull.jpeg")
data = pytesseract.image_to_data(img, config=myconfig, output_type=Output.DICT)
diagrama_caja_texto(data, img)
mostrar_datos_completos(data)

# diagrama_caja_texto(data, img)

'''
#Inversión de color
inversion(img)

#Binarización
binarizacion(img)

# Reduccion de ruido (con el bnw)
bnw = cv2.imread("temp/bnw.jpg")
reduccion_de_ruido(bnw)


expandir_letra(bnw)
expansion = cv2.imread("temp/expansion.jpg")

expansion_data = pytesseract.image_to_data(expansion, config=myconfig, output_type=Output.DICT)
diagrama_caja_texto(expansion_data, expansion)


gris_data = pytesseract.image_to_data(imgGris, config=myconfig, output_type=Output.DICT)
thresh_data = pytesseract.image_to_data(imagenbnw, config=myconfig, output_type=Output.DICT)
diagrama_caja_texto(thresh_data, imagenbnw)
diagrama_caja_texto(gris_data, imgGris)
diagrama_caja_texto(data, img)
'''