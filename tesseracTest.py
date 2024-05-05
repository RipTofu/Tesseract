import pytesseract
import cv2
# from matplotlib import pyplot as plt
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

# [texto encontrado, x, y, altura, ancho, encontrado_o_no]
datos_solicitud = {
    "SOLICITUD DE INTERCONSULTA O DERIVACIÓN": {
        "SOLICITUD DE INTERCONSULTA O DERIVACIÓN": ["", 0, 0, 0, 0, False],
        "N° Folio": ["", 0, 0, 0, 0, False],
        "N° de Orden": ["", 0, 0, 0, 0, False],
        "Fecha Solicitud": ["", 0, 0, 0, 0, False],
        "Servicio de Salud": ["", 0, 0, 0, 0, False],
        "Establecimiento": ["", 0, 0, 0, 0, False]
    },
    "DATOS DEL [DE LA] PACIENTE": {
        "DATOS DEL [DE LA] PACIENTE": ["", 0, 0, 0, 0, False],
        "Primer Apellido": ["", 0, 0, 0, 0, False],
        "Segundo Apellido": ["", 0, 0, 0, 0, False],
        "Nombres": ["", 0, 0, 0, 0, False],
        "RUN": ["", 0, 0, 0, 0, False],
        "Si es recién nacido, RUN de padre o madre beneficiario": ["", 0, 0, 0, 0, False],
        "Número de Ficha": ["", 0, 0, 0, 0, False],
        "Sexo": ["", 0, 0, 0, 0, False],
        "Fecha de Nacimiento": ["", 0, 0, 0, 0, False],
        "Edad": ["", 0, 0, 0, 0, False],
        "Domicilio (calle, número, número interior, bloque (block), villa, localidad": ["", 0, 0, 0, 0, False],
        "Comuna de residencia": ["", 0, 0, 0, 0, False],
        "Teléfono": ["", 0, 0, 0, 0, False],
        "Teléfono Móvil": ["", 0, 0, 0, 0, False],
        "Teléfono Laboral": ["", 0, 0, 0, 0, False],
        "Teléfono Contacto": ["", 0, 0, 0, 0, False],
        "Nombre Padre": ["", 0, 0, 0, 0, False],
        "Nombre Madre": ["", 0, 0, 0, 0, False]
    },
    "DATOS CLINICOS": {
        "DATOS CLINICOS":["", 0, 0, 0, 0, False],
        "Se deriva para atención en": ["", 0, 0, 0, 0, False],
        "Servicio": ["", 0, 0, 0, 0],
        "Especialidad": ["", 0, 0, 0, 0, False],
        "Se envía a consulta para": ["", 0, 0, 0, 0, False],
        "Hipótesis diagnóstica o diagnóstico": ["", 0, 0, 0, 0, False],
        "Especificar problema": ["", 0, 0, 0, 0, False],
        "Prioridad": ["", 0, 0, 0, 0, False],
        "Fundamentos del diagnóstico": ["", 0, 0, 0, 0, False],
        "Exámenes realizados": ["", 0, 0, 0, 0, False],
        "Observaciones": ["", 0, 0, 0, 0, False]
    },
    "DATOS DEL (DE LA) PROFESIONAL": {
        "DATOS DEL (DE LA) PROFESIONAL": ["", 0, 0, 0, 0, False],
        "Primer Apellido": ["", 0, 0, 0, 0, False],
        "Segundo Apellido": ["", 0, 0, 0, 0, False],
        "Nombres": ["", 0, 0, 0, 0, False],
        "RUN": ["", 0, 0, 0, 0, False]
    }
}


# obtiene el promedio de las distancias del texto. El promedio de separación entre palabras para considerarse una oración conjunta.
def distancia_promedio_entre_palabras(data):
    promedio = 0
    encontrados = 0
    for i in range(len(data['level'])-1): # Por cada elemento de entre todos los datos
        if float(data['conf'][i]) > 80:
            if (data['top'][i] - data['top'][i+1]) < 10:
                promedio_act = 0
                encontrados += 1
                pos_final = data['left'][i+1]
                pos_inicial = data['left'][i] + data['width'][i]
                promedio_act = ((pos_final - pos_inicial) / 2)
                if promedio_act > 0:

                    promedio += promedio_act
    promedio = promedio / encontrados
    return int(promedio)

def encontrar_superior(data, index, limite_superior, limites_busqueda):
    contenido_encontrado = ""
    print("#########buscando palabra sobre:", data['text'][index], "###########")
    ancho_label = data['width'][index]
    altura_label = data['height'][index]
    limite_inferior = data['top'][index] - altura_label
    x_label = data['left'][index]
    for i in range(len(data['level'])):
        if i in limites_busqueda:
            if (data['top'][i] < limite_inferior) and (data['top'][i] > limite_superior): # Busca cualquier palabra entre el límite superior del texto y el límite inferior de la categoría.
                # if (data['left'][i]... (Entre el rango determinado para eje x))
                contenido_encontrado = data['text'][i]
    print("Palabra superior a ", data['text'][index], ": ", contenido_encontrado)

def encontrar_ubicaciones_clave(data, distancia_prom):
    texto = 0
    pos_x = 1
    pos_y = 2
    # Recorrido palabras
    ind = indice_alta_certeza(data)
    oraciones = []
    oracion_act = []
    for i in ind:
        ultima_pos = data['left'][i] + data['width'][i]
        ultima_pos_sig = data['left'][i+1]
        if ultima_pos_sig - ultima_pos < distancia_prom and ultima_pos_sig - ultima_pos > 0:
            oracion_act.append(data['text'][i])
        else:
            oracion_act.append(data['text'][i])
            oraciones.append(oracion_act)
            print(oracion_act)
            oracion_act = []

        '''
        if (data['top'][i] - data['top'][i+1]) < 10: # Si están en la misma línea:
             # Inicializa distancia en cero
            cont_palabras = 0 # Inicializa conteo en cero
            act = i # Establece la posicion actual
            ultima_pos_x = data['left'][i] + data['width'][i] # Establece la ubicación en X de la última palabra
            palabra_act = data['text'][i] # Guarda la palabra actual encontrada.
            while distancia < distancia_prom: # Mientras la distancia sea menor a la distancia promedio entre campos (Palabras contiguas):
                cont_palabras += 1 
                 # Nueva distancia: toma la posicion final de la ultima palabra encontrada.
                if distancia < distancia_prom: # Si la distancia es menor a la distancia promedio:
                    palabra_act = palabra_act + data['text'][act + 1] # Concatena la palabra siguiente al campo.
                act += 1 # Aumenta el indice de la palabra actual.


            if distancia < distancia_prom:
                palabra_act = data['text'][i] + data['text'][i+1]
                ultima_pos_x = data['left'][i + 1] + data['width'][i + 1]


            else:
                palabra_act = data['text'][i]
'''

    # Recorrido de llaves del diccionario
    for id, elem in datos_solicitud.items():
        print("id: ", id)
        for key in elem: # Recorrido de los elementos de cada categoría.
            # Por cada elemento queremos encontrar su valor. Para esto, primero se buscan las dimensiones de la palabra completa (Y rezamos para que se encuentre).
            for e in data['text']:
                pass
                '''
                if data['conf']:
                encontrada = e
                print(encontrada)
'''





def indice_alta_certeza(data):
    indices_palabras_encontradas = [] #Lista de indices de palabras a revisar, todas aquellas con confianza superior a 80.
    for i in range(len(data['text'])):
        if float(data['conf'][i]) > 80:
            indices_palabras_encontradas.append(i)
    return indices_palabras_encontradas

def mostrar_datos_completos(data):
    for posicion in indices_palabras_encontradas:
        if data['text'][posicion] == 'PACIENTE':
            tope_superior = data['top'][posicion]
        if data['text'][posicion] == 'Primer':
            encontrar_superior(data, posicion, tope_superior, indices_palabras_encontradas)

'''
Funciones de preprocesamiento
'''
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
        if float(data['conf'][i]) > 80:
            print(data['text'][i], " | Coordenadas: ", data['left'][i],"x, ", data['top'][i], "y | ", data['width'][i], "ancho, ", data['height'][i], "alto.")
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
distancia_promedio = distancia_promedio_entre_palabras(data)
encontrar_ubicaciones_clave(data, distancia_promedio)

'''

mostrar_datos_completos(data)



encontrar_ubicaciones_clave(data)
# diagrama_caja_texto(data, img)


# Preprocesamiento

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