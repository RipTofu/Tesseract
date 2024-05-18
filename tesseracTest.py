import pytesseract
import cv2
# from matplotlib import pyplot as plt
from pytesseract import Output
from fuzzywuzzy import fuzz

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
# palabra, x, y, altura, ancho
oraciones_no_clave = []

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
        "RUN Madre": ["", 0, 0, 0, 0, False],
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
        "Servicio": ["", 0, 0, 0, 0, False],
        "Especialidad": ["", 0, 0, 0, 0, False],
        "Se envía a consulta para": ["", 0, 0, 0, 0, False],
        "Hipótesis diagnóstica o diagnóstico": ["", 0, 0, 0, 0, False],
        "Especificar problema": ["", 0, 0, 0, 0, False],
        "Prioridad": ["", 0, 0, 0, 0, False],
        "Fundamentos del diagnóstico": ["", 0, 0, 0, 0, False],
        "Exámenes realizados": ["", 0, 0, 0, 0, False],
        "Observaciones": ["", 0, 0, 0, 0, False]
    },
    "DATOS DEL (LA) PROFESIONAL": {
        "DATOS DEL (LA) PROFESIONAL": ["", 0, 0, 0, 0, False],
        "Primer Apellido": ["", 0, 0, 0, 0, False],
        "Segundo Apellido": ["", 0, 0, 0, 0, False],
        "Nombres": ["", 0, 0, 0, 0, False],
        "RUN": ["", 0, 0, 0, 0, False]
    }
}


# obtiene el promedio de las distancias del texto. El promedio de separación entre palabras para considerarse una oración.
def distancia_promedio_entre_palabras_x(data):
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

# Encuentra todos los label superiores a "y" y escoge el más cercano como el límite superior para la búsqueda. Retorna la llave del diccionario.
def limite_superior_de_busqueda(y):
    mas_cercano = 9999
    llave = ""
    for categoria in datos_solicitud.values():
        for key, i in categoria.items():
            if i[5]:
                pos_y = i[2] + i[3]
                dist = y - pos_y
                if pos_y < y:
                    if dist < mas_cercano:
                        mas_cercano = pos_y
                        llave = key
    return llave, mas_cercano

# Considera los valores entregados y compara con los valores de las oraciones no clave para encontrar aquellos entre los parámetros definidos.
def encontrar_texto_superior(data, ind, lim_inferior, lim_superior, lim_x1, lim_x2):
    for oracion in oraciones_no_clave:
        #Palabra, x, y, alto, ancho
        if oracion[2] > lim_superior and (oracion[2] + oracion[3]) < lim_inferior: # Límites en Y
            for i in range(oracion[1], (oracion[1] + oracion[4])): # Todas las posiciones dentro de los límites de X
                if (i > lim_x1 and i < lim_x2):
                    return oracion[0]

def encontrar_texto_derecha():
    pass

# (INCOMPLETO)Encuentra la palabra superior. Esta f(x) considera límites definidos. Usar de base para f(x) con dict.
# Debe tomar todas las posiciones Y entre el punto superior del label y el inferior del label que esté arriba.
# Considerar todos los label superiores. Cuando uno esté por encima de la distancia promedio entre palabras en Y, se marca el límite.
def encontrar_contenido(data, distancia_prom_x, ind):
    # Requieren encontrar el texto que está arriba
    categorias_superior = ["DATOS DEL [DE LA] PACIENTE", "DATOS DEL (LA) PROFESIONAL"]
    categorias_derecha = ["DATOS CLINICOS", "DATOS CLINICOS"] # Estos son más jodidos. Varían en formato dentro de la misma categoría.
    for nombre_categoria in categorias_superior:
        categoria = datos_solicitud[nombre_categoria]
        for key, i in categoria.items():
            if i[5]:
                palabra_limite_y, limite_superior = limite_superior_de_busqueda(i[2])
                print("buscando para:", key)
                encontrada = encontrar_texto_superior(data, ind, i[2], limite_superior, i[1], (i[1] + i[4] + distancia_prom_x))
                i[0] = encontrada
                print(i)
    for nombre_categoria in categorias_derecha:
        categoria = datos_solicitud[nombre_categoria]
        for key, i in categoria.items():
            if i[5]:
                pass
# Evalúa si la palabra clave corresponde o no con algún valor. Retorna True si coincide en un 75% con la palabra.
# También modifica el diccionario para almacenar los valores encontrados.
def evaluar_palabra_clave(palabra):
    for categoria in datos_solicitud.values():
        for i in categoria.keys():
            if fuzz.ratio(palabra, i) > 75 and not categoria[i][5]: # Si las palabras coinciden Y no ha sido aún encontrada:
                return i
    return None

# Guarda la posición del label en el diccionario.
def agregar_ubicacion_clave(palabra, x, y, altura, ancho):
    encontrado = False
    for categoria in datos_solicitud.values():
        if palabra in categoria.keys():


            if not(categoria[palabra][5]) and not(encontrado):
                categoria[palabra][1] = x
                categoria[palabra][2] = y
                categoria[palabra][3] = altura
                categoria[palabra][4] = ancho
                categoria[palabra][5] = True
                encontrado = True
                if x < 0 or y < 0 or altura < 0 or ancho < 0:
                    print("Cuidado! Es posible que un valor sea negativo.")
    '''
    print("Agregando al diccionario:", palabra)
    for clave_principal in datos_solicitud:
        if palabra in datos_solicitud[clave_principal]:
            if not datos_solicitud[clave_principal][palabra][5]:
                datos_solicitud[clave_principal][palabra][1] = x
                datos_solicitud[clave_principal][palabra][2] = y
                datos_solicitud[clave_principal][palabra][3] = altura
                datos_solicitud[clave_principal][palabra][4] = ancho
                datos_solicitud[clave_principal][palabra][5] = True
                break
'''
# Encuentra la posición de los labels completos. Los une para generar estas "palabras clave", que corresponden a los 'label'
def encontrar_ubicaciones_clave(data, distancia_prom, ind):
    # Inicialización
    posx_ini = data['left'][0]
    posy_ini = data['top'][0]
    altura = data['height'][0] # Recordar que se considera "Hacia abajo".

    # Recorrido palabras
    campos = 0
    oraciones = []
    oracion_act = []
    for enum, i in enumerate(ind):
        try:
            ultima_pos = data['left'][i] + data['width'][i]
            ultima_pos_sig = data['left'][ind[enum+1]]
            if (ultima_pos_sig - ultima_pos < distancia_prom) and (ultima_pos_sig - ultima_pos > 0):
                oracion_act.append(data['text'][i])
            else:
                oracion_act.append(data['text'][i])
                ancho = ultima_pos - posx_ini
                oracion_act = ' '.join(oracion_act)
                oraciones.append(oracion_act)
                encontrada = evaluar_palabra_clave(oracion_act)
                if encontrada: # Si la oración corresponde:
                    agregar_ubicacion_clave(encontrada, posx_ini, posy_ini, altura, ancho)
                    campos += 1
                else:
                    no_clave = [oracion_act, posx_ini, posy_ini, altura, ancho]
                    oraciones_no_clave.append(no_clave)

                oracion_act = []
                posx_ini = data['left'][ind[enum+1]]
                posy_ini = data['top'][ind[enum+1]]
                altura = data['height'][ind[enum+1]]
        except IndexError:
            pass
    print("encontrados:", campos, "de 40")

def indice_alta_certeza(data):
    indices_palabras_encontradas = [] #Lista de indices de palabras a revisar, todas aquellas con confianza superior a 80.
    for i in range(len(data['text'])):
        if float(data['conf'][i]) > 80:
            indices_palabras_encontradas.append(i)
    return indices_palabras_encontradas

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
    return invertido

def binarizacion(img):
    gris = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cv2.imwrite("temp/gris.jpg", gris)
    imgGris = cv2.imread("temp/gris.jpg")  # Genera la imagen con threshold
    thresh, bnw_img = cv2.threshold(imgGris, 127, 255, cv2.THRESH_BINARY)
    cv2.imwrite("temp/bnw.jpg", bnw_img)

def diagrama_encontrados(img):
    for categoria in datos_solicitud:
        for campo, atributos in datos_solicitud[categoria].items():
            if atributos[-1]:  # Verifica si el campo está marcado como encontrado
                x, y, height, width = atributos[1:5]
                img = cv2.rectangle(img, (x, y), (x+width, y+height), (0, 255, 0), 2)
    cv2.imshow("encontrados", img)
    cv2.waitKey(0)

def diagrama_caja_texto(data, img):  # Recibe el diccionario completo de datos
    for i in range(len(data['text'])):
        if float(data['conf'][i]) > 80: # Limitación del nivel de confianza
            (x, y, width, height) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
            img = cv2.rectangle(img, (x, y), (x+width, y+height), (0,255,0), 2)
            img = cv2.putText(img, data['text'][i], (x, y+height+20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2, cv2.LINE_AA)
            print(data['text'][i])
    cv2.imshow("img", img)
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
img = cv2.imread("alo-_1_.jpeg")
data = pytesseract.image_to_data(img, config=myconfig, output_type=Output.DICT)
distancia_promedio = distancia_promedio_entre_palabras_x(data)
ind = indice_alta_certeza(data)
encontrar_ubicaciones_clave(data, distancia_promedio, ind)
encontrar_contenido(data, distancia_promedio, ind)
diagrama_encontrados(img)

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