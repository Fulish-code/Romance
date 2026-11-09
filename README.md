# Romance

Versión 1.1.0

Romance es un lenguaje de programación pequeño que diseñamos para la materia de Teoría de la Computación. Sus palabras reservadas no están en inglés y las operaciones aritméticas se escriben en notación polaca, por ejemplo `(+ a b)`.

## Archivos

- `Practica6_Gramatica_Romance.pdf`: práctica 6, la gramática libre de contexto del lenguaje en BNF, el programa de ejemplo y sus árboles.
- `analizador_romance.py`: práctica 7, analizador léxico y sintáctico con interfaz gráfica en Tkinter. Muestra la tabla de tokens y, si hay errores, la línea, el error y cómo corregirlo.

## Cómo correrlo

Solo necesita Python 3 con Tkinter.

```
python3 analizador_romance.py
```

Al abrir carga un programa de ejemplo. Se valida con el botón Validar o con F5. También se pueden abrir y guardar archivos `.rom`.

## Ejemplo

```
comezo Ejemplo {
    inteiro n, i = 1, f = 1;
    llegeix(n);
    etiquette ciclo:
    fie f = (* f i);
    fie i = (+ i 1);
    allera ciclo quand (i <= n);
    scrivi(n, "! = ", f);
}
```
