#Practica 7: Analizador lexico y sintactico del lenguaje Romance (gramatica de la practica 6)
import tkinter as tk
from tkinter import ttk, filedialog
import difflib
import re
import unicodedata

RESERVADAS = ["comezo", "inteiro", "real", "cadeia", "fie", "llegeix", "scrivi",
              "si", "sino", "etiquette", "allera", "quand"]
SIMBOLOS = "+-*/%<>=(){};:,"
COMPUESTOS = ["==", "!=", "<=", ">="]
OP_ARIT = ["+", "-", "*", "/", "%"]
OP_REL = ["==", "!=", "<", ">", "<=", ">="]
TIPOS = ["inteiro", "real", "cadeia"]
INICIO_SENTENCIA = TIPOS + ["fie", "llegeix", "scrivi", "si", "etiquette", "allera"]

#Palabras de otros lenguajes y su equivalente en Romance
OTROS = {"if": "si", "else": "sino", "elif": "sino si", "while": "etiquette ... allera ... quand",
         "for": "etiquette ... allera ... quand", "do": "etiquette", "repeat": "etiquette",
         "until": "quand", "goto": "allera", "print": "scrivi", "printf": "scrivi",
         "write": "scrivi", "writeln": "scrivi", "cout": "scrivi", "read": "llegeix",
         "readln": "llegeix", "scanf": "llegeix", "input": "llegeix", "cin": "llegeix",
         "int": "inteiro", "float": "real", "double": "real", "string": "cadeia",
         "char": "cadeia", "var": "inteiro / real / cadeia", "let": "fie", "set": "fie",
         "begin": "comezo", "program": "comezo", "main": "comezo", "end": "}", "then": "{"}

EJEMPLO = """// Factorial, media y paridad de un entero
comezo Ejemplo {
    inteiro n, i = 1, f = 1;
    real m;
    cadeia par = "y ademas es par";

    scrivi("Dame un entero:");
    llegeix(n);

    si (n < 0) {
        scrivi("No hay factorial para negativos");
    } sino {
        etiquette ciclo:
        fie f = (* f i);
        fie i = (+ i 1);
        allera ciclo quand (i <= n);

        fie m = (/ (+ n 1) 2.0);
        scrivi(n, "! = ", f, ", media de 1 a n = ", m);
        si ((% n 2) == 0) {
            scrivi(par);
        }
    }
}
"""


#Analisis lexico

def es_letra(c):
    return ("a" <= c <= "z") or ("A" <= c <= "Z") or c == "_"


def es_digito(c):
    return "0" <= c <= "9"


def sin_acentos(palabra):
    return "".join(c for c in unicodedata.normalize("NFD", palabra) if unicodedata.category(c) != "Mn")


def analisis_lexico(codigo, solo_primero=False):
    tokens = []  #[texto, tipo, linea]
    errores = []  #[linea, fase, error, solucion]
    i = 0
    linea = 1
    n = len(codigo)
    while i < n:
        if solo_primero and errores:
            break
        c = codigo[i]
        if c == "\n":
            linea += 1
            i += 1
        elif c in " \t\r":
            i += 1
        elif codigo[i:i + 2] == "//":
            while i < n and codigo[i] != "\n":
                i += 1
        elif es_letra(c) or c.isalpha():
            inicio = i
            while i < n and (es_letra(codigo[i]) or es_digito(codigo[i]) or codigo[i].isalpha()):
                i += 1
            palabra = codigo[inicio:i]
            limpia = sin_acentos(palabra)
            if limpia != palabra or not all(es_letra(x) or es_digito(x) for x in palabra):
                tokens.append([palabra, "Error", linea])
                errores.append([linea, "Léxico", "'" + palabra + "' tiene letras con acento o ñ",
                                "Los nombres solo usan letras sin acento: escribe '" + limpia + "'"])
            elif palabra in RESERVADAS:
                tokens.append([palabra, "PR", linea])
            else:
                tokens.append([palabra, "Var", linea])
        elif es_digito(c):
            inicio = i
            while i < n and (es_digito(codigo[i]) or es_letra(codigo[i]) or codigo[i] == "."):
                i += 1
            numero = codigo[inicio:i]
            if re.fullmatch(r"[0-9]+(\.[0-9]+)?", numero):
                tokens.append([numero, "Num", linea])
            else:
                tokens.append([numero, "Error", linea])
                if numero.endswith(".") and numero.count(".") == 1 and numero[:-1].isdigit():
                    errores.append([linea, "Léxico", "El número '" + numero + "' está incompleto",
                                    "Pon un dígito después del punto: " + numero + "0, o quita el punto"])
                elif numero.count(".") > 1:
                    errores.append([linea, "Léxico", "El número '" + numero + "' tiene más de un punto",
                                    "Un número real lleva un solo punto, por ejemplo 2.5"])
                else:
                    letras = "".join(x for x in numero if es_letra(x))
                    errores.append([linea, "Léxico", "'" + numero + "' no es número ni variable",
                                    "Una variable no puede empezar con número: escribe '" + letras + numero.replace(letras, "") + "' o separa el número y la variable con un espacio"])
        elif c == '"' or c == "“" or c == "”":
            inicio = i
            i += 1
            while i < n and codigo[i] not in '"“”\n':
                i += 1
            if i < n and codigo[i] != "\n":
                i += 1
                cadena = codigo[inicio:i]
                if "“" in cadena or "”" in cadena:
                    tokens.append([cadena, "Error", linea])
                    errores.append([linea, "Léxico", "La cadena " + cadena + " usa comillas curvas “ ”",
                                    "Usa comillas rectas: " + '"' + cadena[1:-1] + '"'])
                else:
                    tokens.append([cadena, "Cad", linea])
            else:
                cadena = codigo[inicio:i]
                tokens.append([cadena, "Error", linea])
                errores.append([linea, "Léxico", "La cadena " + cadena + " no se cerró",
                                "Agrega la comilla \" al final de la cadena, en la misma línea"])
        elif c == "'":
            inicio = i
            i += 1
            while i < n and codigo[i] not in "'\n":
                i += 1
            if i < n and codigo[i] == "'":
                i += 1
            cadena = codigo[inicio:i]
            tokens.append([cadena, "Error", linea])
            errores.append([linea, "Léxico", "Las comillas simples no existen en Romance: " + cadena,
                            "Las cadenas van entre comillas dobles: \"" + cadena.strip("'") + "\""])
        elif codigo[i:i + 2] in COMPUESTOS:
            tokens.append([codigo[i:i + 2], "SimC", linea])
            i += 2
        elif c in SIMBOLOS:
            tokens.append([c, "Simb", linea])
            i += 1
        else:
            if codigo[i:i + 2] in ["&&", "||"]:
                simbolo = codigo[i:i + 2]
                solucion = "Romance no tiene operadores lógicos, usa un si dentro de otro si"
            else:
                simbolo = c
                if c == "!":
                    solucion = "Para 'diferente de' se escribe != (junto)"
                elif c == "[":
                    solucion = "Usa paréntesis ( ) en lugar de corchetes"
                elif c == "]":
                    solucion = "Usa paréntesis ( ) en lugar de corchetes"
                elif c == ".":
                    solucion = "Si es un número escribe el 0 antes del punto, por ejemplo 0.5"
                elif c == "&" or c == "|":
                    solucion = "Romance no tiene operadores lógicos, usa un si dentro de otro si"
                else:
                    solucion = "Borra el carácter '" + c + "', no forma parte del lenguaje"
            tokens.append([simbolo, "Error", linea])
            errores.append([linea, "Léxico", "Carácter no válido: '" + simbolo + "'", solucion])
            i += len(simbolo)
    return tokens, errores


#Analisis sintactico, cada no terminal de la gramatica es una funcion

class ErrorSintactico(Exception):
    pass


toks = []
pos = 0
errores_sin = []
lineas_codigo = []
sospechoso = None
primer_error = False


def actual():
    return toks[pos]


def siguiente():
    if pos + 1 < len(toks):
        return toks[pos + 1]
    return toks[-1]


def anterior():
    if pos > 0:
        return toks[pos - 1]
    return toks[0]


def ve(texto):
    return toks[pos][0] == texto and toks[pos][1] != "Cad"


def avanza():
    global pos
    pos += 1


def error(mensaje, solucion, linea=None):
    if linea is None:
        linea = actual()[2]
    raise ErrorSintactico(linea, mensaje, solucion)


def encontrado():
    if actual()[1] == "FIN":
        return "el fin del archivo"
    return "'" + actual()[0] + "'"


def come(esperado, solucion, linea_anterior=False):
    if ve(esperado):
        avanza()
    else:
        if linea_anterior:
            error("Falta '" + esperado + "' después de '" + anterior()[0] + "'", solucion, anterior()[2])
        error("Se esperaba '" + esperado + "' pero se encontró " + encontrado(), solucion)


def punto_y_coma():
    if ve(";"):
        avanza()
        return
    t = actual()
    if t[0] in OP_ARIT:
        error("Operación escrita en infijo ('" + anterior()[0] + " " + t[0] + " ...')",
              "Romance usa notación polaca entre paréntesis: (" + t[0] + " " + anterior()[0] + " " + siguiente()[0] + ")")
    if t[0] in OP_REL:
        error("No se puede usar '" + t[0] + "' aquí",
              "Las comparaciones solo van en la condición de si ( ) o de quand ( )")
    linea = anterior()[2]
    if t[2] == linea and t[1] != "FIN":
        error("Falta ';' al final de la sentencia", "Agrega ';' después de '" + anterior()[0] + "'", linea)
    texto = lineas_codigo[linea - 1].split("//")[0].strip()
    error("Falta ';' al final de la sentencia", "Agrega ';' al final de la línea: " + texto + ";", linea)


def es_operando(t):
    return t[1] == "Var" or t[1] == "Num"


def identificador(que, solucion):
    t = actual()
    if t[1] == "Var":
        avanza()
    elif t[1] == "PR":
        error("'" + t[0] + "' es palabra reservada y no se puede usar como " + que,
              "Cámbiale el nombre, por ejemplo '" + t[0] + "1'")
    else:
        error("Se esperaba " + que + " pero se encontró " + encontrado(), solucion)


# <programa> := comezo <id> { <sentencias> }
def programa():
    global sospechoso
    if ve("comezo"):
        avanza()
    else:
        t = actual()
        try:
            if t[0].lower() in OTROS:
                error("'" + t[0] + "' no es de Romance", "El programa empieza con: comezo Nombre { ... }")
            if t[1] == "Var" and difflib.get_close_matches(t[0].lower(), ["comezo"], 1, 0.6):
                error("'" + t[0] + "' no es palabra reservada",
                      "¿Quisiste decir 'comezo'? El programa empieza con: comezo Nombre { ... }")
            error("El programa debe empezar con 'comezo'", "Escribe al inicio: comezo Nombre { ... }")
        except ErrorSintactico as e:
            if primer_error:
                raise
            errores_sin.append([e.args[0], "Sintáctico", e.args[1], e.args[2]])
            #se sigue revisando si solo esta mal escrito o falta el comezo
            if t[1] == "Var" and siguiente()[1] == "Var":
                avanza()
            elif not (t[1] == "Var" and siguiente()[0] == "{"):
                return
    identificador("el nombre del programa", "Ponle nombre al programa: comezo Ejemplo {")
    if not ve("{"):
        error("Se esperaba '{' después del nombre del programa", "Abre el programa con llave: comezo " + anterior()[0] + " {", anterior()[2])
    linea_abre = actual()[2]
    avanza()
    sentencias()
    if not ve("}"):
        if sospechoso is not None:
            linea_abre = sospechoso
        error("Falta una '}' de cierre", "Cada '{' necesita su '}'. Revisa el bloque que abre en la línea " + str(linea_abre), anterior()[2])
    avanza()
    if actual()[1] != "FIN":
        error("Hay código después de la '}' que cierra el programa",
              "Sobra una '}' antes de esta línea o el código quedó fuera del programa; todo va dentro de comezo { }")


# <sentencias> := <sentencia> <sentencias> | ε
def sentencias():
    while not ve("}") and actual()[1] != "FIN":
        inicio = pos
        try:
            sentencia()
        except ErrorSintactico as e:
            #si solo se quiere el primer error, ya no se sigue revisando
            if primer_error:
                raise
            errores_sin.append([e.args[0], "Sintáctico", e.args[1], e.args[2]])
            recuperar(inicio)


#modo panico, se salta hasta el ';' o hasta la siguiente sentencia
def recuperar(inicio):
    global pos
    nivel = 0
    linea_error = toks[inicio][2]
    if pos == inicio:
        avanza()
    while actual()[1] != "FIN":
        t = actual()
        if t[0] == "{" and nivel == 0:
            #si el error fue en la condicion de un si, el bloque se revisa de todos modos
            try:
                bloque("si")
                if ve("sino"):
                    avanza()
                    if ve("si"):
                        condicional()
                    else:
                        bloque("sino")
            except ErrorSintactico as e:
                errores_sin.append([e.args[0], "Sintáctico", e.args[1], e.args[2]])
            return
        elif t[0] == "{":
            nivel += 1
        elif t[0] == "}":
            if nivel == 0:
                return
            nivel -= 1
        elif t[0] == ";" and nivel == 0:
            avanza()
            return
        elif t[0] in INICIO_SENTENCIA and nivel == 0 and t[2] > linea_error:
            return
        avanza()


# <sentencia> := <declaracion> | <asignacion> | <lectura> | <escritura> | <condicional> | <etiqueta> | <salto>
def sentencia():
    t = actual()
    if t[0] in TIPOS:
        declaracion()
    elif t[0] == "fie":
        asignacion()
    elif t[0] == "llegeix":
        lectura()
    elif t[0] == "scrivi":
        escritura()
    elif t[0] == "si":
        condicional()
    elif t[0] == "etiquette":
        etiqueta()
    elif t[0] == "allera":
        salto()
    elif t[0] == "sino":
        error("'sino' sin un 'si' antes", "sino va justo después de la '}' del bloque de un si: si (...) { } sino { }")
    elif t[0] == "quand":
        error("'quand' fuera de un salto", "quand solo va después de allera: allera etiqueta quand (condicion);")
    elif t[0] == "comezo":
        error("'comezo' solo puede ir una vez, al inicio del programa", "Borra este 'comezo'")
    elif t[1] == "Var":
        variable_suelta()
    elif t[0] == ";":
        error("Sobra un ';'", "Borra el ';' que está de más")
    elif t[0] == "{":
        error("Bloque '{' sin instrucción", "Un bloque solo puede ir después de si, sino o del nombre del programa")
    else:
        error("No se esperaba " + encontrado() + " al inicio de una sentencia",
              "Una sentencia empieza con inteiro, real, cadeia, fie, llegeix, scrivi, si, etiquette o allera")


#la sentencia empieza con un nombre, se busca que quiso escribir
def variable_suelta():
    t = actual()
    s = siguiente()
    if s[0] == "=":
        error("Asignación sin 'fie'", "En Romance se asigna así: fie " + t[0] + " = valor;")
    if s[0] == ":" and toks[pos + 2][0] == "=":
        error("':=' no existe en Romance", "Escribe la asignación así: fie " + t[0] + " = valor;")
    if s[0] == ":":
        error("Etiqueta sin 'etiquette'", "Escribe: etiquette " + t[0] + ":")
    if t[0].lower() in RESERVADAS:
        error("'" + t[0] + "' no es palabra reservada", "Las palabras reservadas van en minúsculas: escribe '" + t[0].lower() + "'")
    if t[0].lower() in OTROS:
        error("'" + t[0] + "' no existe en Romance", "En Romance se usa: " + OTROS[t[0].lower()])
    parecida = difflib.get_close_matches(t[0].lower(), RESERVADAS, 1, 0.6)
    if parecida:
        error("'" + t[0] + "' no es una instrucción de Romance", "¿Quisiste decir '" + parecida[0] + "'? Revisa cómo está escrita")
    error("'" + t[0] + "' no es una instrucción válida",
          "Una sentencia empieza con inteiro, real, cadeia, fie, llegeix, scrivi, si, etiquette o allera")


# <declaracion> := <tipo> <lista_decl> ;
# <lista_decl> := <item_decl> | <item_decl> , <lista_decl>
def declaracion():
    tipo = actual()[0]
    avanza()
    item_decl(tipo)
    while ve(",") or actual()[1] in ["Var", "Num", "Cad"]:
        if actual()[1] != "Var" and not ve(","):
            if anterior()[1] == "Var":
                error("Falta '=' entre '" + anterior()[0] + "' y '" + actual()[0] + "'",
                      "Para dar un valor inicial se usa '=': " + tipo + " " + anterior()[0] + " = " + actual()[0] + ";")
            error("Sobra " + encontrado() + " después de '" + anterior()[0] + "'",
                  "Cada variable recibe un solo valor: " + tipo + " x = valor;")
        if actual()[1] == "Var":
            error("Falta ',' entre '" + anterior()[0] + "' y '" + actual()[0] + "'",
                  "Separa las variables con coma: " + tipo + " " + anterior()[0] + ", " + actual()[0] + ";")
        avanza()
        item_decl(tipo)
    punto_y_coma()


# <item_decl> := <id> | <id> = <expresion>
def item_decl(tipo):
    identificador("un nombre de variable", "Después de " + tipo + " va el nombre de la variable: " + tipo + " x;")
    if ve("="):
        avanza()
        expresion()
    elif ve("=="):
        error("Para dar un valor inicial se usa '=' (uno solo)", "Escribe: " + tipo + " " + anterior()[0] + " = valor;")


# <lectura> := llegeix ( <id> ) ;
def lectura():
    avanza()
    come("(", "La variable va entre paréntesis: llegeix(x);")
    if actual()[1] != "Var" and actual()[1] != "PR":
        error("llegeix solo puede leer una variable, se encontró " + encontrado(), "Escribe el nombre de una variable: llegeix(x);")
    identificador("una variable", "llegeix(x);")
    if ve(","):
        error("llegeix lee una sola variable", "Usa un llegeix por variable: llegeix(a); llegeix(b);")
    come(")", "Cierra el paréntesis: llegeix(" + anterior()[0] + ");", True)
    punto_y_coma()


# <escritura> := scrivi ( <lista_esc> ) ;
# <lista_esc> := <expresion> | <expresion> , <lista_esc>
def escritura():
    avanza()
    come("(", "Lo que se escribe va entre paréntesis: scrivi(\"hola\");")
    if ve(")"):
        error("scrivi está vacío", "Pon al menos un valor: scrivi(\"hola\");")
    expresion()
    while ve(",") or actual()[1] in ["Var", "Num", "Cad"]:
        if not ve(","):
            error("Falta ',' antes de " + encontrado(), "Separa los valores de scrivi con coma: scrivi(a, \" \", b);", anterior()[2])
        avanza()
        expresion()
    come(")", "Cierra el paréntesis de scrivi antes del ';'", True)
    punto_y_coma()


# <asignacion> := fie <id> = <expresion> ;
def asignacion():
    avanza()
    identificador("la variable que se asigna", "Escribe: fie x = valor;")
    if ve("=="):
        error("Para asignar se usa '=' (uno solo)", "Escribe: fie " + anterior()[0] + " = valor;")
    if ve(":"):
        error("':=' no existe en Romance", "Escribe: fie " + anterior()[0] + " = valor;")
    come("=", "Escribe: fie " + anterior()[0] + " = valor;")
    expresion()
    punto_y_coma()


# <expresion> := <expr_arit> | <cadena>
def expresion():
    if actual()[1] == "Cad":
        avanza()
    else:
        expr_arit()


# <expr_arit> := ( <op_arit> <expr_arit> <expr_arit> ) | <operando>
def expr_arit():
    t = actual()
    if ve("("):
        linea_abre = t[2]
        avanza()
        if actual()[0] in OP_ARIT:
            avanza()
        elif es_operando(actual()) and siguiente()[0] in OP_ARIT:
            a = actual()[0]
            op = siguiente()[0]
            b = toks[pos + 2][0]
            error("Operación en notación infija: (" + a + " " + op + " " + b + " ...)",
                  "Romance usa notación polaca, el operador va primero: (" + op + " " + a + " " + b + ")")
        elif actual()[0] in OP_REL:
            error("'" + actual()[0] + "' no es operador aritmético",
                  "Dentro de ( ) solo van + - * / %. Las comparaciones van sin paréntesis extra: a < b")
        else:
            error("Falta el operador después de '('", "El operador va primero: (+ a b). Operadores: + - * / %")
        expr_arit()
        expr_arit()
        if not ve(")"):
            if es_operando(actual()) or ve("("):
                error("Una operación lleva exactamente dos operandos",
                      "Si son más de dos, anida otra operación: (+ a (+ b c))")
            error("Falta ')' para cerrar la operación que abre en la línea " + str(linea_abre),
                  "Agrega ')' después de '" + anterior()[0] + "'", anterior()[2])
        avanza()
    elif es_operando(t):
        avanza()
    elif t[1] == "Cad":
        error("No se pueden hacer operaciones ni comparaciones con cadenas", "Usa solo números o variables numéricas")
    elif t[0] in OP_ARIT:
        error("Falta '(' antes de '" + t[0] + "'", "Las operaciones van entre paréntesis: (" + t[0] + " a b)")
    elif t[1] == "PR":
        error("'" + t[0] + "' es palabra reservada y no puede ser un valor", "Usa una variable o un número")
    elif t[0] in [")", ";", ","] or t[1] == "FIN":
        error("Falta un valor antes de " + encontrado(), "Escribe un número, una variable o una operación (op a b)")
    else:
        error("Se esperaba un número, una variable o una operación y se encontró " + encontrado(),
              "Escribe un número, una variable o una operación (op a b)")


# <expr_rel> := <expr_arit> <op_rel> <expr_arit>
def expr_rel():
    expr_arit()
    if actual()[0] in OP_REL:
        avanza()
    elif ve("="):
        error("Para comparar se usa '==' no '='", "Cambia '=' por '=='")
    elif ve(")"):
        error("La condición no tiene operador relacional", "Compara dos valores: (a < b). Operadores: == != < > <= >=")
    else:
        error("Se esperaba un operador relacional y se encontró " + encontrado(), "Usa == != < > <= >= entre los dos valores")
    expr_arit()


# <condicional> := si ( <expr_rel> ) <bloque> <resto_si>
# <resto_si> := sino <bloque> | sino <condicional> | ε
def condicional():
    avanza()
    come("(", "La condición va entre paréntesis: si (a < b) { ... }")
    expr_rel()
    come(")", "Cierra el paréntesis de la condición: si (a < b) {", True)
    bloque("si")
    if ve("sino"):
        avanza()
        if ve("si"):
            condicional()
        elif ve("{"):
            bloque("sino")
        else:
            error("Después de 'sino' va '{' o 'si'", "Escribe: sino { ... }  o  sino si (...) { ... }")


# <bloque> := { <sentencias> }
def bloque(de):
    global sospechoso
    if not ve("{"):
        error("Falta '{' para abrir el bloque del " + de, "Las llaves son obligatorias: " + de + " ... { sentencias }", anterior()[2])
    linea_abre = actual()[2]
    avanza()
    sentencias()
    if not ve("}"):
        error("Falta '}' para cerrar el bloque que abre en la línea " + str(linea_abre), "Agrega '}' al final del bloque", anterior()[2])
    #si las llaves no estan alineadas puede ser la que falta
    if sangria(actual()[2]) != sangria(linea_abre) and sospechoso is None:
        sospechoso = linea_abre
    avanza()


def sangria(linea):
    texto = lineas_codigo[linea - 1].replace("\t", "    ")
    return len(texto) - len(texto.lstrip())


# <etiqueta> := etiquette <id> :
def etiqueta():
    avanza()
    identificador("el nombre de la etiqueta", "Escribe: etiquette ciclo:")
    if ve(";"):
        error("La etiqueta termina con ':' no con ';'", "Escribe: etiquette " + anterior()[0] + ":")
    come(":", "Escribe: etiquette " + anterior()[0] + ":", True)


# <salto> := allera <id> <guarda> ;
# <guarda> := quand ( <expr_rel> ) | ε
def salto():
    avanza()
    identificador("el nombre de la etiqueta", "Escribe: allera ciclo;  o  allera ciclo quand (i <= n);")
    if ve("si"):
        error("El salto con condición usa 'quand' no 'si'", "Escribe: allera " + anterior()[0] + " quand (condicion);")
    if ve("("):
        error("Falta 'quand' antes de la condición", "Escribe: allera " + anterior()[0] + " quand (condicion);")
    if ve("quand"):
        avanza()
        come("(", "La condición va entre paréntesis: quand (i <= n)")
        expr_rel()
        come(")", "Cierra el paréntesis de la condición de quand", True)
    punto_y_coma()


def analisis_sintactico(tokens, codigo, solo_primero=False):
    global toks, pos, errores_sin, lineas_codigo, sospechoso, primer_error
    ultima = tokens[-1][2] if tokens else 1
    toks = tokens + [["fin del archivo", "FIN", ultima]]
    pos = 0
    errores_sin = []
    lineas_codigo = codigo.split("\n")
    sospechoso = None
    primer_error = solo_primero
    try:
        programa()
    except ErrorSintactico as e:
        errores_sin.append([e.args[0], "Sintáctico", e.args[1], e.args[2]])
    return errores_sin


#Interfaz

def validar(evento=None):
    codigo = editor.get("1.0", "end-1c")
    tabla_tokens.delete(*tabla_tokens.get_children())
    tabla_errores.delete(*tabla_errores.get_children())
    editor.tag_remove("error", "1.0", "end")

    tokens, errores = analisis_lexico(codigo, solo_primero.get())
    num = 1
    for t in tokens:
        if t[1] == "Error":
            tabla_tokens.insert("", "end", values=(num, t[0], t[1], t[2]), tags=("malo",))
        else:
            tabla_tokens.insert("", "end", values=(num, t[0], t[1], t[2]))
        num += 1
    lbl_tokens.config(text="Tokens: " + str(len(tokens)))

    if errores:
        lbl_estado.config(text="✖ " + str(len(errores)) + " error(es) léxico(s). Corrígelos para hacer el análisis sintáctico",
                          fg="#b00020")
    else:
        errores = analisis_sintactico(tokens, codigo, solo_primero.get())
        if errores:
            lbl_estado.config(text="✖ " + str(len(errores)) + " error(es) sintáctico(s)", fg="#b00020")
        else:
            lbl_estado.config(text="✔ Programa válido: sin errores léxicos ni sintácticos", fg="#1b7a1b")

    for e in errores:
        tabla_errores.insert("", "end", values=(e[0], e[1], e[2], e[3]))
        editor.tag_add("error", str(e[0]) + ".0", str(e[0]) + ".end+1c")


def colorear(evento=None):
    for tag in ["pr", "cad", "com", "num"]:
        editor.tag_remove(tag, "1.0", "end")
    texto = editor.get("1.0", "end-1c")
    patrones = [("num", r"\b[0-9]+(\.[0-9]+)?\b"), ("pr", r"\b(" + "|".join(RESERVADAS) + r")\b"),
                ("cad", r"\"[^\"\n]*\"?"), ("com", r"//[^\n]*")]
    for tag, patron in patrones:
        for m in re.finditer(patron, texto):
            editor.tag_add(tag, "1.0+%dc" % m.start(), "1.0+%dc" % m.end())
    numeros_linea()


def numeros_linea(evento=None):
    total = int(editor.index("end-1c").split(".")[0])
    numeros.config(state="normal")
    numeros.delete("1.0", "end")
    numeros.insert("1.0", "\n".join(str(i) for i in range(1, total + 1)))
    numeros.config(state="disabled")
    numeros.yview_moveto(editor.yview()[0])


def mover_editor(*args):
    barra.set(*args)
    numeros.yview_moveto(args[0])


def mover_barra(*args):
    editor.yview(*args)
    numeros.yview(*args)


def ir_a_error(evento):
    sel = tabla_errores.selection()
    if sel:
        linea = tabla_errores.item(sel[0])["values"][0]
        editor.see(str(linea) + ".0")
        editor.mark_set("insert", str(linea) + ".0")
        editor.focus_set()


def abrir():
    ruta = filedialog.askopenfilename(filetypes=[("Programas Romance", "*.rom"), ("Todos", "*.*")])
    if ruta:
        with open(ruta, encoding="utf-8") as f:
            editor.delete("1.0", "end")
            editor.insert("1.0", f.read())
        colorear()
        ventana.title("Analizador sintáctico Romance - " + ruta.split("/")[-1])


def guardar():
    ruta = filedialog.asksaveasfilename(defaultextension=".rom", filetypes=[("Programas Romance", "*.rom")])
    if ruta:
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(editor.get("1.0", "end-1c"))


def seleccionar_todo(evento=None):
    editor.tag_add("sel", "1.0", "end-1c")
    editor.mark_set("insert", "end-1c")
    return "break"


def borrar(evento=None):
    #borra lo seleccionado, por ejemplo despues de Ctrl+A
    if editor.tag_ranges("sel"):
        editor.delete("sel.first", "sel.last")
        colorear()
        return "break"


def cargar_ejemplo():
    editor.delete("1.0", "end")
    editor.insert("1.0", EJEMPLO)
    colorear()


ventana = tk.Tk()
ventana.title("Analizador sintáctico Romance")
ventana.geometry("1340x720")

estilo = ttk.Style()
estilo.theme_use("clam")
estilo.configure("Treeview", font=("DejaVu Sans", 10), rowheight=22)
estilo.configure("Treeview.Heading", font=("DejaVu Sans", 10, "bold"))

barra_botones = tk.Frame(ventana, pady=4)
barra_botones.pack(fill="x")
tk.Button(barra_botones, text="Abrir", width=9, command=abrir).pack(side="left", padx=4)
tk.Button(barra_botones, text="Guardar", width=9, command=guardar).pack(side="left", padx=4)
tk.Button(barra_botones, text="Ejemplo", width=9, command=cargar_ejemplo).pack(side="left", padx=4)
tk.Button(barra_botones, text="Validar (F5)", width=12, bg="#2e7d32", fg="white", font=("DejaVu Sans", 10, "bold"),
          command=validar).pack(side="left", padx=4)
solo_primero = tk.BooleanVar(value=True)
tk.Checkbutton(barra_botones, text="Analizar hasta el primer error", variable=solo_primero).pack(side="left", padx=4)
lbl_estado = tk.Label(barra_botones, text="Escribe o modifica el código y presiona Validar", font=("DejaVu Sans", 11, "bold"))
lbl_estado.pack(side="left", padx=15)

paneles = tk.PanedWindow(ventana, orient="vertical", sashwidth=5)
paneles.pack(fill="both", expand=True)
arriba = tk.PanedWindow(paneles, orient="horizontal", sashwidth=5)
paneles.add(arriba, stretch="always")

#Editor de codigo con numeros de linea
marco_editor = tk.LabelFrame(arriba, text="Código fuente (Romance)")
numeros = tk.Text(marco_editor, width=4, bg="#eeeeee", fg="#777777", font=("DejaVu Sans Mono", 11),
                  state="disabled", bd=0, padx=4)
numeros.pack(side="left", fill="y")
barra = tk.Scrollbar(marco_editor, command=mover_barra)
barra.pack(side="right", fill="y")
editor = tk.Text(marco_editor, font=("DejaVu Sans Mono", 11), undo=True, wrap="none",
                 yscrollcommand=mover_editor, tabs="32", insertwidth=2)
editor.pack(side="left", fill="both", expand=True)
editor.tag_config("pr", foreground="#0033b3", font=("DejaVu Sans Mono", 11, "bold"))
editor.tag_config("cad", foreground="#067d17")
editor.tag_config("com", foreground="#8c8c8c")
editor.tag_config("num", foreground="#1750eb")
editor.tag_config("error", background="#ffd9d9")
editor.bind("<KeyRelease>", colorear)
editor.bind("<Control-a>", seleccionar_todo)
editor.bind("<Control-A>", seleccionar_todo)
editor.bind("<BackSpace>", borrar)
arriba.add(marco_editor, stretch="always", width=760)

#Tabla de tokens
marco_tokens = tk.LabelFrame(arriba, text="Análisis léxico")
tabla_tokens = ttk.Treeview(marco_tokens, columns=("no", "token", "tipo", "linea"), show="headings")
for col, titulo, ancho in [("no", "No.", 45), ("token", "Token", 220), ("tipo", "Tipo", 70), ("linea", "Línea", 55)]:
    tabla_tokens.heading(col, text=titulo)
    tabla_tokens.column(col, width=ancho, anchor="w" if col == "token" else "center")
tabla_tokens.tag_configure("malo", background="#ffd9d9", foreground="#b00020")
barra_tokens = ttk.Scrollbar(marco_tokens, command=tabla_tokens.yview)
tabla_tokens.config(yscrollcommand=barra_tokens.set)
lbl_tokens = tk.Label(marco_tokens, text="Tokens: 0", anchor="w")
lbl_tokens.pack(side="top", fill="x")
tk.Label(marco_tokens, text="PR: Palabra reservada   Var: Variable   Num: Número\nCad: Cadena   Simb: Símbolo   SimC: Símbolo compuesto",
         justify="left", fg="#555555", anchor="w").pack(side="bottom", fill="x")
barra_tokens.pack(side="right", fill="y")
tabla_tokens.pack(fill="both", expand=True)
arriba.add(marco_tokens, stretch="always")

#Tabla de errores
marco_errores = tk.LabelFrame(paneles, text="Errores encontrados y cómo corregirlos")
tabla_errores = ttk.Treeview(marco_errores, columns=("linea", "fase", "error", "solucion"), show="headings", height=6)
for col, titulo, ancho in [("linea", "Línea", 55), ("fase", "Fase", 90), ("error", "Error", 470), ("solucion", "Cómo corregirlo", 700)]:
    tabla_errores.heading(col, text=titulo)
    tabla_errores.column(col, width=ancho, anchor="center" if col in ["linea", "fase"] else "w")
tabla_errores.pack(fill="both", expand=True)
tabla_errores.bind("<<TreeviewSelect>>", ir_a_error)
paneles.add(marco_errores, height=190)

ventana.bind("<F5>", validar)
cargar_ejemplo()

if __name__ == "__main__":
    ventana.mainloop()
