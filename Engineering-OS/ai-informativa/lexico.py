# -*- coding: utf-8 -*-
"""Adquisicion de lenguaje anclado para las mascotas.

Ninguna palabra tiene significado escrito aqui. Una palabra significa algo
porque la OYERON mientras les pasaba algo: si le escribes "hambre" cuando su
saciedad esta por el suelo, la palabra queda ligada a ese estado. El
significado es la distribucion de contextos en que la escucharon, y solo la
usan cuando esa distribucion es lo bastante clara.

Tres fuentes de lenguaje:
  - tu, cuando les escribes (menu -> 💬 Hablarle)
  - la otra mascota, si esta cerca cuando una habla (se contagian palabras)
  - ellas mismas, inventando sonidos que suenan a español

El diccionario (datos/es_50k.txt, 50.000 palabras por frecuencia) NO aporta
significados: aporta las formas. Sirve para balbucear con la fonotactica del
español de verdad y para distinguir una palabra real de un invento.
"""

import os
import random
import unicodedata

RUTA_LISTA = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "datos", "es_50k.txt")

# Los conceptos son sus propias dimensiones de experiencia, no etiquetas
# arbitrarias: son estados internos y eventos que ya sabian distinguir antes
# de tener una sola palabra.
CONCEPTOS = [
    "hambre", "comida", "sueno", "energia", "carino", "soledad",
    "juego", "aburrimiento", "tu", "pareja", "dolor", "alegria",
    "bien", "mal", "miedo",
]

# Cuando quieren expresar algo, esto dice que concepto buscan en su lexico.
CLAVE_A_CONCEPTO = {
    "hambre": "hambre", "sueno": "sueno", "solo": "soledad",
    "feliz": "alegria", "cargado": "tu", "caricia": "carino",
    "jugar": "juego", "lanzado": "dolor", "nacer": "alegria",
}

MIN_ESCUCHAS = 3        # menos que esto y no saben si entendieron
MIN_CONFIANZA = 0.45    # que tan concentrada debe estar la asociacion


def normalizar(palabra):
    p = palabra.strip().lower()
    p = "".join(c for c in p if c.isalpha() or c in "áéíóúüñ")
    return p


def sin_tildes(p):
    return "".join(c for c in unicodedata.normalize("NFD", p)
                   if unicodedata.category(c) != "Mn")


class Diccionario:
    """Las formas del español. Se carga una vez y la comparten las dos."""

    _instancia = None

    def __init__(self, ruta=RUTA_LISTA, tope_modelo=20000):
        self.formas = {}          # palabra -> puesto por frecuencia
        self.trigramas = {}       # (c1, c2) -> [caracteres siguientes]
        self.cargado = False
        try:
            with open(ruta, "r", encoding="utf-8") as fh:
                for puesto, linea in enumerate(fh):
                    palabra = normalizar(linea.split(" ")[0])
                    if len(palabra) >= 2:
                        self.formas.setdefault(palabra, puesto)
        except OSError:
            return
        self.cargado = bool(self.formas)
        self._entrenar_balbuceo(tope_modelo)

    @classmethod
    def unico(cls):
        if cls._instancia is None:
            cls._instancia = cls()
        return cls._instancia

    def _entrenar_balbuceo(self, tope):
        """Modelo de caracteres: aprende como suena el español, no que dice."""
        for palabra, puesto in self.formas.items():
            if puesto >= tope:
                continue
            seq = "^^" + palabra + "$"
            for i in range(2, len(seq)):
                self.trigramas.setdefault(seq[i - 2:i], []).append(seq[i])

    def es_real(self, palabra):
        return palabra in self.formas

    def frecuencia(self, palabra):
        """0.0 = rarisima, 1.0 = de las mas comunes del idioma."""
        puesto = self.formas.get(palabra)
        if puesto is None:
            return 0.0
        return max(0.0, 1.0 - puesto / max(1, len(self.formas)))

    def balbucear(self, largo_max=7):
        """Un sonido que no existe pero que suena a español."""
        if not self.trigramas:
            return random.choice(["ba", "gu", "ma", "aah"])
        for _ in range(12):
            ctx, salida = "^^", []
            while len(salida) < largo_max:
                siguientes = self.trigramas.get(ctx)
                if not siguientes:
                    break
                c = random.choice(siguientes)
                if c == "$":
                    break
                salida.append(c)
                ctx = ctx[1] + c
            palabra = "".join(salida)
            # un balbuceo no debe ser una palabra real por accidente
            if len(palabra) >= 2 and not self.es_real(palabra):
                return palabra
        return "ba"


class Lexico:
    """Lo que UNA mascota sabe de las palabras. Cada una tiene el suyo."""

    def __init__(self, datos, diccionario=None):
        # datos vive en el JSON: {"assoc": {palabra: {concepto: n}},
        #                         "total": {palabra: n}, "oidas": n}
        self.datos = datos
        self.datos.setdefault("assoc", {})
        self.datos.setdefault("total", {})
        self.datos.setdefault("oidas", 0)
        self.dic = diccionario or Diccionario.unico()

    # ----------------------------------------------------------- aprender

    ATENCION = 2      # a cuantas cosas a la vez pueden prestar atencion

    @classmethod
    def _pesos(cls, conceptos):
        """Reparte la atencion entre lo que esta pasando.

        Acepta ["hambre", ...] o [("hambre", 2.4), ...]. Solo se queda con
        las dos cosas mas salientes: si una palabra se repartiera entre las
        seis cosas que le pasan a la vez, nunca llegaria a significar nada.
        Un bebe tampoco aprende asi; atiende a lo que mas le pesa.
        """
        mejores = {}
        for item in conceptos:
            if isinstance(item, (tuple, list)):
                nombre, p = item[0], float(item[1])
            else:
                nombre, p = item, 1.0
            if nombre in CONCEPTOS and p > 0:
                mejores[nombre] = max(mejores.get(nombre, 0.0), p)
        if not mejores:
            return []
        pares = sorted(mejores.items(), key=lambda t: -t[1])[:cls.ATENCION]
        total = sum(p for _, p in pares)
        return [(n, p / total) for n, p in pares]

    def oir(self, texto, conceptos, peso=1.0):
        """Liga cada palabra del texto con lo que esta pasando AHORA.

        Devuelve las palabras cuyo significado acaba de quedar claro.
        """
        conceptos = self._pesos(conceptos)
        if not conceptos:
            return []
        recien_entendidas = []
        for bruta in texto.split():
            palabra = normalizar(bruta)
            if len(palabra) < 2 or len(palabra) > 16:
                continue
            entendia = self.entiende(palabra)
            # una palabra real del idioma pesa mas que un sonido cualquiera
            w = peso * (1.4 if self.dic.es_real(palabra) else 0.8)
            fila = self.datos["assoc"].setdefault(palabra, {})
            for c, parte in conceptos:
                fila[c] = fila.get(c, 0.0) + w * parte
            self.datos["total"][palabra] = self.datos["total"].get(palabra, 0.0) + w
            self.datos["oidas"] += 1
            if not entendia and self.entiende(palabra):
                recien_entendidas.append(palabra)
        return recien_entendidas

    # ------------------------------------------------------------ conocer

    def significado(self, palabra):
        """(concepto, confianza). La confianza es que tan concentrada esta."""
        fila = self.datos["assoc"].get(palabra)
        total = self.datos["total"].get(palabra, 0.0)
        if not fila or total <= 0:
            return None, 0.0
        concepto = max(fila, key=fila.get)
        return concepto, fila[concepto] / total

    def entiende(self, palabra):
        veces = self.datos["total"].get(palabra, 0.0)
        if veces < MIN_ESCUCHAS:
            return False
        _, conf = self.significado(palabra)
        return conf >= MIN_CONFIANZA

    def palabra_para(self, concepto):
        """La palabra que mejor expresa ese concepto, si la tienen."""
        mejor, mejor_v = None, 0.0
        for palabra, fila in self.datos["assoc"].items():
            v = fila.get(concepto, 0.0)
            if v <= mejor_v or not self.entiende(palabra):
                continue
            c, _ = self.significado(palabra)
            if c == concepto:
                mejor, mejor_v = palabra, v
        return mejor

    def vocabulario(self):
        """Palabras que de verdad entienden, de la mas firme a la mas floja."""
        salida = []
        for palabra in self.datos["assoc"]:
            if not self.entiende(palabra):
                continue
            concepto, conf = self.significado(palabra)
            salida.append((palabra, concepto, conf,
                           self.datos["total"].get(palabra, 0.0)))
        salida.sort(key=lambda t: -t[3])
        return salida

    @property
    def sabidas(self):
        return sum(1 for p in self.datos["assoc"] if self.entiende(p))

    @property
    def en_duda(self):
        """Palabras oidas pero todavia sin significado claro."""
        return sum(1 for p in self.datos["assoc"] if not self.entiende(p))

    # ------------------------------------------------------------- hablar

    def decir(self, concepto, etapa):
        """Como expresan un concepto con lo que saben hasta ahora.

        Bebe: balbucea aunque sepa la palabra (aun no la puede pronunciar).
        Niño: la palabra sola. Adolescente/adulta: la palabra en una frase.
        """
        palabra = self.palabra_para(concepto)
        if palabra is None:
            return None
        if etapa == "bebe":
            return f"¿{palabra[:3]}...?"
        if etapa == "nino":
            return f"¡{palabra}!"
        plantillas = {
            "hambre": ["{p}...", "tengo {p}", "otra vez {p}"],
            "comida": ["quiero {p}", "{p}, por favor"],
            "sueno": ["{p}...", "me gana el {p}"],
            "carino": ["{p}", "necesito {p}"],
            "soledad": ["{p}", "no me gusta la {p}"],
            "juego": ["¡{p}!", "quiero {p}"],
            "tu": ["{p}", "eres {p}"],
            "dolor": ["¡{p}!", "eso es {p}"],
            "alegria": ["¡{p}!", "esto es {p}"],
        }
        forma = random.choice(plantillas.get(concepto, ["{p}", "¡{p}!"]))
        return forma.format(p=palabra)

    def inventar(self):
        return self.dic.balbucear()
