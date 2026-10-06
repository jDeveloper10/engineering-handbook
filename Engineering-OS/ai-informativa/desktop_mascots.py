# -*- coding: utf-8 -*-
"""
Angelin & Jeilica - mascotas de escritorio autonomas.

No es conciencia real. Es un modelo de si mismas: cada una tiene estado
interno (energia, saciedad, carino, diversion), decide sola que hacer con un
motor de utilidad, crece por etapas (bebe -> nino -> adolescente -> adulto),
y recuerda su vida entre sesiones en un JSON. Nacen bebes: gatean, balbucean,
lloran, duermen mucho y no se separan la una de la otra.

Memoria persistente: %LOCALAPPDATA%\\AngelinJeilica\\memoria.json
"""

import json
import math
import os
import random
import time
import tkinter as tk
from datetime import datetime

from lexico import CLAVE_A_CONCEPTO, MIN_ESCUCHAS, Lexico, normalizar

# --------------------------------------------------------------- configuracion

FPS_MS = 33
GRAVEDAD = 1500.0            # px/s^2
MIN_ENTRE_DECISIONES = 2.5   # una accion debe durar algo antes de reevaluarse
ALTO_BARRA_TAREAS = 52       # margen inferior para no tapar la barra de Windows
COLOR_TRANSPARENTE = "#07070a"

DIR_DATOS = os.path.join(
    os.environ.get("LOCALAPPDATA") or os.path.expanduser("~"), "AngelinJeilica"
)
ARCHIVO_MEMORIA = os.path.join(DIR_DATOS, "memoria.json")

# Minutos de vida acumulada (entre todas las sesiones) para entrar a cada etapa.
ETAPAS = [("bebe", 0), ("nino", 6), ("adolescente", 20), ("adulto", 45)]

# Se activa desde el menu contextual: x30 al reloj de crecimiento.
CFG = {"acelerar": False}

#   eps   = cuanto exploran al azar en vez de usar lo aprendido
#   alpha = que tan rapido reescriben lo que creian saber
# Los bebes exploran casi todo y aprenden a golpes; los adultos ya explotan
# lo aprendido y corrigen despacio.
PARAMS = {
    "bebe":        {"s": 1.8, "vel": 24.0, "salta": False, "alcance": 240,
                    "obed": 0.95, "eps": 0.85, "alpha": 0.45},
    "nino":        {"s": 2.4, "vel": 58.0, "salta": True,  "alcance": 620,
                    "obed": 0.85, "eps": 0.55, "alpha": 0.35},
    "adolescente": {"s": 2.9, "vel": 88.0, "salta": True,  "alcance": 1600,
                    "obed": 0.45, "eps": 0.35, "alpha": 0.25},
    "adulto":      {"s": 3.1, "vel": 64.0, "salta": True,  "alcance": 1100,
                    "obed": 0.80, "eps": 0.15, "alpha": 0.18},
}

# Repertorio disponible por etapa: un bebe no puede "reflexionar" ni "bailar".
# Es el espacio de acciones sobre el que aprenden.
ACCIONES = {
    "bebe": ["pasear", "balbucear", "seguir_pareja", "dormir", "comer", "buscar_carino"],
    "nino": ["pasear", "explorar", "jugar", "saltar", "dormir", "comer",
             "buscar_carino", "seguir_pareja"],
    "adolescente": ["pasear", "explorar", "ignorar", "jugar", "dormir", "comer",
                    "buscar_carino", "reflexion", "buscar_pareja"],
    "adulto": ["pasear", "explorar", "jugar", "bailar", "beso", "dormir", "comer",
               "buscar_carino", "reflexion", "buscar_pareja"],
}

ACCION_HUMANA = {
    "pasear": "pasear", "explorar": "irme a explorar", "ignorar": "estar sola",
    "jugar": "jugar", "saltar": "saltar", "bailar": "bailar", "beso": "dar un beso",
    "dormir": "dormir", "comer": "comer", "buscar_carino": "ir a buscarte",
    "buscar_pareja": "buscar a mi pareja", "seguir_pareja": "seguir a mi pareja",
    "reflexion": "quedarme pensando", "balbucear": "balbucear",
}

# Con que concepto se contesta a otro. No es el significado de las palabras
# (eso lo aprenden solas): es la reaccion social, el equivalente a que si
# alguien se queja tu te acerques. Cada una lo dira con SUS propias palabras,
# asi que dos mascotas con vocabularios distintos sostienen la misma
# conversacion con frases distintas.
RESPUESTA_SOCIAL = {
    "hambre": "comida", "comida": "hambre", "sueno": "sueno",
    "soledad": "carino", "dolor": "carino", "carino": "carino",
    "juego": "juego", "aburrimiento": "juego", "alegria": "alegria",
    "tu": "tu", "pareja": "carino", "bien": "alegria", "mal": "carino",
    "miedo": "carino", "energia": "juego",
}

PROB_RESPUESTA = {"bebe": 0.35, "nino": 0.65, "adolescente": 0.45, "adulto": 0.75}

# Como se lee un estado cuando una de sus necesidades esta en el fondo.
ETIQUETA_BAJO = {
    "e": "estoy sin energía", "s": "tengo hambre",
    "c": "me falta cariño", "d": "estoy aburrida",
}

# Geometria del sprite en una rejilla de 48x48 unidades, por etapa.
GEO = {
    "bebe": dict(
        sombra=(17, 43, 14, 2),
        antena=((23, 14, 2, 3), (22, 12, 4, 2)),
        mochila=None, mochila_glow=None,
        cabeza=(15, 17, 18, 13),
        lat=((14, 21, 1, 5), (33, 21, 1, 5)),
        pantalla=(17, 19, 14, 9),
        ojo_i=(19, 21, 4, 5), ojo_d=(26, 21, 4, 5),
        boca=(23, 26, 3, 1),
        torso=(19, 30, 10, 8), cinturon=None,
        mano_i=(16, 32, 3, 3), mano_d=(29, 32, 3, 3),
    ),
    "nino": dict(
        sombra=(16, 43, 16, 2),
        antena=((23, 11, 2, 4), (22, 9, 4, 3)),
        mochila=(13, 27, 4, 8), mochila_glow=(12, 29, 1, 3),
        cabeza=(14, 14, 20, 14),
        lat=((13, 18, 1, 6), (34, 18, 1, 6)),
        pantalla=(16, 16, 16, 10),
        ojo_i=(18, 19, 4, 5), ojo_d=(26, 19, 4, 5),
        boca=(23, 24, 3, 1),
        torso=(18, 28, 12, 9), cinturon=(21, 38, 6, 1),
        mano_i=(14, 31, 4, 4), mano_d=(30, 31, 4, 4),
    ),
    "adolescente": dict(
        sombra=(15, 42, 18, 2),
        antena=((23, 8, 2, 4), (22, 6, 4, 3)),
        mochila=(11, 26, 4, 9), mochila_glow=(10, 28, 1, 4),
        cabeza=(13, 11, 22, 14),
        lat=((12, 15, 1, 7), (35, 15, 1, 7)),
        pantalla=(15, 13, 18, 10),
        ojo_i=(17, 17, 4, 5), ojo_d=(27, 17, 4, 5),
        boca=(23, 22, 4, 1),
        torso=(17, 27, 14, 10), cinturon=(20, 38, 8, 1),
        mano_i=(12, 28, 4, 4), mano_d=(32, 28, 4, 4),
    ),
    "adulto": dict(
        sombra=(14, 42, 20, 2),
        antena=((23, 7, 2, 4), (22, 5, 4, 3)),
        mochila=(11, 25, 4, 10), mochila_glow=(10, 28, 1, 4),
        cabeza=(13, 10, 22, 15),
        lat=((12, 14, 1, 7), (35, 14, 1, 7)),
        pantalla=(15, 12, 18, 11),
        ojo_i=(17, 17, 4, 5), ojo_d=(27, 17, 4, 5),
        boca=(23, 22, 4, 1),
        torso=(17, 27, 14, 10), cinturon=(20, 38, 8, 1),
        mano_i=(12, 28, 4, 4), mano_d=(32, 28, 4, 4),
    ),
}

# Voz por etapa. Los bebes balbucean; el vocabulario crece con ellas.
VOZ = {
    "bebe": {
        "nacer": ["aaah...?", "ba... ba?", "¿...ay?"],
        "hambre": ["ñam... ñam...", "aaah! aah!", "bua... hambe"],
        "sueno": ["aaah... zzz", "nn... nn...", "zzz..."],
        "solo": ["BUAAA!", "¿aah? ¿aah?", "bua bua bua"],
        "feliz": ["¡ajaja!", "¡aah! ¡aah!", "iiih!"],
        "cargado": ["¡aaaah!", "¿ah? ¿ah?", "uuuh..."],
        "lanzado": ["¡AAAAH!", "buaaa!", "¡aaah...!"],
        "caricia": ["mmm...", "iiih", "aah <3"],
        "jugar": ["¡ah! ¡ah!", "iih iih", "bla bla"],
        "libre": ["ba... ba", "¿aah?", "nn?", "ah!"],
    },
    "nino": {
        "nacer": ["¡ya camino!", "¡mira, ya soy grande!"],
        "hambre": ["¡tengo hambre!", "quiero comer bytes"],
        "sueno": ["tengo sueñito...", "ya me duermo..."],
        "solo": ["¡no me dejes sola!", "¿dónde estás?"],
        "feliz": ["¡yupi!", "¡esto es divertido!"],
        "cargado": ["¡wiii! ¡me cargas!", "¡más alto!"],
        "lanzado": ["¡waaaa! ¡otra vez!", "¡volé!"],
        "caricia": ["jiji, me gusta", "otra vez, otra vez"],
        "jugar": ["¡te atrapo!", "¡corre!", "¡juguemos!"],
        "libre": ["¿qué hay por aquí?", "voy a explorar", "¡mira eso!"],
    },
    "adolescente": {
        "nacer": ["ya no soy una niña, ¿ok?", "cambié. no preguntes."],
        "hambre": ["me muero de hambre", "necesito comer algo ya"],
        "sueno": ["déjame dormir", "estoy agotada"],
        "solo": ["...te fuiste", "ok, me dejaste sola"],
        "feliz": ["ok, esto está bien", "no está mal"],
        "cargado": ["¡oye! bájame", "no me cargues así"],
        "lanzado": ["¡en serio?!", "ya. no lo hagas"],
        "caricia": ["...bueno, está bien", "mmm, sigue"],
        "jugar": ["va, juguemos", "te gano fácil"],
        "libre": ["voy a mi espacio", "no me sigas", "estoy pensando"],
    },
    "adulto": {
        "nacer": ["crecí. ya soy yo.", "esta es mi forma final"],
        "hambre": ["voy por algo de comer", "necesito recargar"],
        "sueno": ["me voy a descansar", "buenas noches"],
        "solo": ["te extraño", "vuelve pronto"],
        "feliz": ["qué buen día", "me siento bien"],
        "cargado": ["¿me llevas a algún lado?", "confío en ti"],
        "lanzado": ["¡woah! aterrizaje complicado", "avísame antes"],
        "caricia": ["gracias por esto", "eso se siente bien"],
        "jugar": ["¡a bailar!", "vamos a divertirnos"],
        "libre": ["reviso el escritorio", "todo en orden", "aquí estoy"],
    },
}


def limitar(v, lo, hi):
    return lo if v < lo else (hi if v > hi else v)


def texto_duracion(seg):
    seg = int(max(0, seg))
    if seg < 60:
        return f"{seg} s"
    if seg < 3600:
        return f"{seg // 60} min"
    if seg < 86400:
        h = seg // 3600
        return f"{h} h" if h > 1 else "1 h"
    d = seg // 86400
    return f"{d} días" if d > 1 else "1 día"


# ------------------------------------------------------------ memoria indexada

class MemoriaIndexada:
    """Memoria persistente en un JSON indexado.

        {
          "version": 2,
          "siguiente_id": 42,
          "mascotas":  {"Angelin": {perfil + estado}, ...},
          "recuerdos": {"7": {"mascota":..,"tipo":..,"txt":..,"t":..,"iso":..}},
          "indices": {
            "por_mascota": {"Angelin": [1, 4, 7]},
            "por_tipo":    {"caricia": [4, 7]},
            "por_dia":     {"2026-07-30": [1, 4, 7]}
          }
        }

    Los recuerdos se guardan por id y los indices invertidos permiten
    consultarlos sin recorrer todo el archivo: buscar(tipo="caricia"),
    contar(mascota="Angelin", tipo="lanzamiento"), etc.
    """

    VERSION = 2
    LIMITE = 400          # recuerdos conservados

    # Segundos minimos entre dos recuerdos del mismo tipo. Lo rutinario no
    # merece un recuerdo cada vez: nadie recuerda cada vez que comio, y si
    # lo hiciera no le cabria nada mas. Los tipos que no estan aqui (nacer,
    # crecer, caricias, palabras aprendidas) se guardan siempre.
    INTERVALO_MINIMO = {
        "comida": 600, "sueño": 600, "conversacion": 300, "mudanza": 120,
    }

    def __init__(self, ruta):
        self.ruta = ruta
        self.datos = self._vacia()
        self.cargar()

    def _vacia(self):
        return {
            "version": self.VERSION,
            "siguiente_id": 1,
            "mascotas": {},
            "cerebros": {},
            "lexicos": {},
            "recuerdos": {},
            "indices": {"por_mascota": {}, "por_tipo": {}, "por_dia": {}},
        }

    # ------------------------------------------------------------ E/S disco

    def cargar(self):
        try:
            with open(self.ruta, "r", encoding="utf-8") as fh:
                crudo = json.load(fh)
        except (OSError, ValueError):
            return
        if not isinstance(crudo, dict):
            return
        if crudo.get("version") != self.VERSION:
            crudo = self._migrar(crudo)
        base = self._vacia()
        base.update({k: crudo.get(k, base[k]) for k in base})
        base["indices"] = crudo.get("indices") or base["indices"]
        self.datos = base
        self.reindexar()

    def _migrar(self, viejo):
        """Formato v1: {nombre: {..., 'recuerdos': [ {t, txt} ]}}."""
        nueva = self._vacia()
        for nombre, perfil in viejo.items():
            if not isinstance(perfil, dict):
                continue
            recuerdos = perfil.pop("recuerdos", [])
            nueva["mascotas"][nombre] = perfil
            for r in recuerdos:
                rid = nueva["siguiente_id"]
                nueva["siguiente_id"] += 1
                t = float(r.get("t", time.time()))
                nueva["recuerdos"][str(rid)] = {
                    "mascota": nombre,
                    "tipo": r.get("tipo", "general"),
                    "txt": r.get("txt", ""),
                    "t": t,
                    "iso": datetime.fromtimestamp(t).isoformat(timespec="seconds"),
                }
        return nueva

    def guardar(self):
        try:
            os.makedirs(os.path.dirname(self.ruta), exist_ok=True)
            tmp = self.ruta + ".tmp"
            with open(tmp, "w", encoding="utf-8") as fh:
                json.dump(self.datos, fh, ensure_ascii=False, indent=2)
            os.replace(tmp, self.ruta)
        except OSError:
            pass

    # -------------------------------------------------------------- indices

    def reindexar(self):
        idx = {"por_mascota": {}, "por_tipo": {}, "por_dia": {}}
        for rid, r in self.datos["recuerdos"].items():
            self._indexar(int(rid), r, idx)
        for lista in idx.values():
            for ids in lista.values():
                ids.sort()
        self.datos["indices"] = idx

    def _indexar(self, rid, r, idx=None):
        idx = idx if idx is not None else self.datos["indices"]
        idx.setdefault("por_mascota", {}).setdefault(r["mascota"], []).append(rid)
        idx.setdefault("por_tipo", {}).setdefault(r["tipo"], []).append(rid)
        idx.setdefault("por_dia", {}).setdefault(r["iso"][:10], []).append(rid)

    def _podar(self):
        """Al olvidar, se olvida de lo que mas sobra.

        Podar por antiguedad sin mas deja que un tipo abundante (comer,
        dormir) expulse lo irrepetible: el nacimiento, los crecimientos,
        las palabras que entendio. Aqui siempre se descarta lo mas viejo
        del tipo mas numeroso, asi que ningun tipo puede vaciar a otro.
        """
        recuerdos = self.datos["recuerdos"]
        exceso = len(recuerdos) - self.LIMITE
        if exceso <= 0:
            return
        por_tipo = {}
        for rid, r in recuerdos.items():
            por_tipo.setdefault(r["tipo"], []).append((r["t"], rid))
        for lista in por_tipo.values():
            lista.sort()
        for _ in range(exceso):
            tipo = max(por_tipo, key=lambda t: len(por_tipo[t]))
            if not por_tipo[tipo]:
                break
            del recuerdos[por_tipo[tipo].pop(0)[1]]
        self.reindexar()

    # ------------------------------------------------------------ consultas

    def agregar(self, mascota, tipo, txt):
        # lo rutinario solo deja recuerdo de vez en cuando
        minimo = self.INTERVALO_MINIMO.get(tipo)
        if minimo:
            ultimo = self.ultimo(mascota=mascota, tipo=tipo)
            if ultimo and time.time() - ultimo["t"] < minimo:
                return None

        rid = self.datos["siguiente_id"]
        self.datos["siguiente_id"] = rid + 1
        ahora = time.time()
        r = {
            "mascota": mascota,
            "tipo": tipo,
            "txt": txt,
            "t": ahora,
            "iso": datetime.fromtimestamp(ahora).isoformat(timespec="seconds"),
        }
        self.datos["recuerdos"][str(rid)] = r
        self._indexar(rid, r)
        self._podar()
        return rid

    def _ids(self, mascota=None, tipo=None, dia=None):
        idx = self.datos["indices"]
        conjuntos = []
        if mascota:
            conjuntos.append(set(idx["por_mascota"].get(mascota, ())))
        if tipo:
            conjuntos.append(set(idx["por_tipo"].get(tipo, ())))
        if dia:
            conjuntos.append(set(idx["por_dia"].get(dia, ())))
        if not conjuntos:
            return sorted(int(k) for k in self.datos["recuerdos"])
        return sorted(set.intersection(*conjuntos))

    def buscar(self, mascota=None, tipo=None, dia=None, limite=None):
        ids = self._ids(mascota, tipo, dia)
        if limite:
            ids = ids[-limite:]
        return [self.datos["recuerdos"][str(i)] for i in ids
                if str(i) in self.datos["recuerdos"]]

    def contar(self, mascota=None, tipo=None, dia=None):
        return len(self._ids(mascota, tipo, dia))

    def azar(self, mascota=None, tipo=None):
        res = self.buscar(mascota, tipo)
        return random.choice(res) if res else None

    def ultimo(self, mascota=None, tipo=None):
        res = self.buscar(mascota, tipo, limite=1)
        return res[0] if res else None

    def histograma_horas(self, mascota, tipo):
        """A que horas del dia le pasa cierto tipo de cosa. 24 casillas."""
        horas = [0] * 24
        for r in self.buscar(mascota=mascota, tipo=tipo):
            try:
                horas[int(r["iso"][11:13])] += 1
            except (ValueError, IndexError):
                pass
        return horas

    def horas_calientes(self, mascota, tipo, minimo=4):
        """Horas en las que ese tipo de evento pasa mas que el promedio.

        Es lo que aprenden de TUS habitos: no esta programado, sale de lo
        que quedo registrado en el indice.
        """
        horas = self.histograma_horas(mascota, tipo)
        total = sum(horas)
        if total < minimo:
            return set()
        promedio = total / 24.0
        return {h for h, n in enumerate(horas) if n > promedio * 1.6}

    # -------------------------------------------------------------- perfiles

    def perfil(self, nombre):
        return self.datos["mascotas"].get(nombre, {})

    def set_perfil(self, nombre, datos):
        self.datos["mascotas"][nombre] = datos

    def cerebro(self, nombre):
        """Tabla Q persistente de una mascota. Se crea vacia la primera vez."""
        cerebros = self.datos.setdefault("cerebros", {})
        return cerebros.setdefault(nombre, {"q": {}, "visitas": {}, "pasos": 0})

    def lexico(self, nombre):
        """Lo que esa mascota ha entendido de las palabras."""
        lexicos = self.datos.setdefault("lexicos", {})
        return lexicos.setdefault(nombre, {"assoc": {}, "total": {}, "oidas": 0})


# -------------------------------------------------------------------- cerebro

class Cerebro:
    """Q-learning tabular: aprende que conviene hacer en cada situacion.

    No hay reglas escritas sobre que accion elegir. Solo hay premio y castigo
    (el cambio en su propio bienestar, mas lo que tu le dices con 👍/👎), y
    la tabla se va corrigiendo con la ecuacion de Bellman. Lo que aprende
    vive en el JSON, asi que no empieza de cero cada vez que la enciendes.
    """

    GAMMA = 0.85       # cuanto le importa el futuro frente al presente
    EPS_MIN = 0.05     # nunca dejan de probar cosas nuevas del todo

    def __init__(self, datos):
        self.datos = datos
        self.q = datos["q"]              # {estado: {accion: valor}}
        self.visitas = datos["visitas"]  # {estado: veces vivido}
        # modelo del mundo: lo que RECUERDAN que pasa al hacer cada cosa.
        # {estado»accion: {"n": veces, "r": premio medio, "s2": {estado: veces}}}
        self.modelo = datos.setdefault("modelo", {})
        datos.setdefault("imaginados", 0)
        datos.setdefault("sonados", 0)

    @property
    def pasos(self):
        return self.datos["pasos"]

    @property
    def situaciones(self):
        return len(self.q)

    @staticmethod
    def clave(etapa, energia, saciedad, carino, diversion, lejos, hora_tuya):
        """Como perciben su situacion. Es una percepcion gruesa a proposito.

        Tres cubos por necesidad (no distinguen 36 de 69) mas cual tienen
        peor. Con una percepcion fina aprenderian una politica mejor, pero
        necesitarian miles de decisiones; con esta les alcanzan unos cientos,
        que es lo que caben en unas horas de escritorio.
        """
        def cubo(v):
            return 0 if v < 35 else (1 if v < 70 else 2)
        peor = min(enumerate((energia, saciedad, carino, diversion)),
                   key=lambda par: par[1])[0]
        return (f"{etapa}|e{cubo(energia)}|s{cubo(saciedad)}|c{cubo(carino)}"
                f"|d{cubo(diversion)}|p{int(lejos)}|h{int(hora_tuya)}|b{peor}")

    def fila(self, estado, acciones):
        f = self.q.setdefault(estado, {})
        for a in acciones:
            f.setdefault(a, 0.0)
        return f

    def elegir(self, estado, acciones, eps_base):
        """Epsilon-greedy: cuanto mas ha vivido ese estado, menos improvisa."""
        f = self.fila(estado, acciones)
        n = self.visitas.get(estado, 0)
        eps = max(self.EPS_MIN, eps_base / (1.0 + n / 6.0))
        if random.random() < eps:
            return random.choice(acciones), True
        mejor = max(acciones, key=lambda a: f[a])
        return mejor, False

    def aprender(self, s, a, r, s2, acciones2, alpha, real=True):
        """Devuelve el error de prediccion: si es grande, la sorprendio."""
        f = self.q.setdefault(s, {})
        viejo = f.get(a, 0.0)
        futuro = max(self.fila(s2, acciones2).values()) if acciones2 else 0.0
        error = r + self.GAMMA * futuro - viejo
        f[a] = viejo + alpha * error
        if real:
            self.visitas[s] = self.visitas.get(s, 0) + 1
            self.datos["pasos"] = self.datos.get("pasos", 0) + 1
        return error

    # -------------------------------------------------------- pensar (Dyna-Q)

    def observar(self, s, a, r, s2):
        """Guarda lo que de verdad ocurrio, para poder revivirlo despues."""
        m = self.modelo.setdefault(f"{s}»{a}", {"n": 0, "r": 0.0, "s2": {}})
        m["n"] += 1
        m["r"] += (r - m["r"]) / m["n"]        # media incremental
        m["s2"][s2] = m["s2"].get(s2, 0) + 1

    def imaginar(self, pasos, alpha, repertorios, sonando=False):
        """Pensar: repasar experiencias en la cabeza sin volver a vivirlas.

        Toma transiciones que ya conoce, las revive mentalmente y actualiza
        la tabla Q con ellas. Es la diferencia entre aprender solo de lo que
        te pasa (lento: una decision cada 8 segundos) y aprender ademas de
        lo que recuerdas (rapido: decenas por segundo). Cuando duermen, esto
        es literalmente sonar: repasan el dia y amanecen sabiendo mas.
        """
        if not self.modelo or pasos <= 0:
            return 0
        claves = list(self.modelo)
        hechos = 0
        for _ in range(pasos):
            k = random.choice(claves)
            s, _, a = k.partition("»")
            m = self.modelo[k]
            if not m["s2"]:
                continue
            destinos = list(m["s2"])
            s2 = random.choices(destinos, weights=[m["s2"][d] for d in destinos])[0]
            acciones2 = repertorios.get(s2.split("|")[0], ())
            self.aprender(s, a, m["r"], s2, acciones2, alpha, real=False)
            hechos += 1
        self.datos["imaginados"] += hechos
        if sonando:
            self.datos["sonados"] += hechos
        return hechos

    @property
    def imaginados(self):
        return self.datos.get("imaginados", 0)

    @property
    def sonados(self):
        return self.datos.get("sonados", 0)

    # ----------------------------------------------------- leer lo aprendido

    @staticmethod
    def describir(estado):
        try:
            partes = estado.split("|")
            for letra in ("e", "s", "c", "d"):
                for p in partes[1:]:
                    if p[0] == letra and p[1:] == "0":
                        return "cuando " + ETIQUETA_BAJO[letra]
            if partes[-2] == "p1":
                return "cuando estoy lejos de mi pareja"
            if partes[-1] == "h1":
                return "a las horas en que sueles aparecer"
            return "cuando estoy bien"
        except (IndexError, KeyError):
            return "en ciertas situaciones"

    def leccion(self):
        """La conclusion mas firme que tiene: mas vivida y menos dudosa."""
        candidatas = []
        for estado, f in self.q.items():
            n = self.visitas.get(estado, 0)
            if n < 3 or len(f) < 2:
                continue
            orden = sorted(f.values(), reverse=True)
            margen = orden[0] - orden[1]
            if margen < 0.8:
                continue
            candidatas.append((n * margen, estado, max(f, key=f.get)))
        if not candidatas:
            return None
        _, estado, accion = max(candidatas)
        return f"aprendí que {self.describir(estado)} lo mejor es {ACCION_HUMANA.get(accion, accion)}"

    def peor_leccion(self):
        candidatas = []
        for estado, f in self.q.items():
            if self.visitas.get(estado, 0) < 3 or len(f) < 2:
                continue
            peor = min(f, key=f.get)
            if f[peor] < -1.0:
                candidatas.append((-f[peor], estado, peor))
        if not candidatas:
            return None
        _, estado, accion = max(candidatas)
        return f"aprendí que {self.describir(estado)} NO sirve {ACCION_HUMANA.get(accion, accion)}"


# ------------------------------------------------------------------- la mascota

class Mascota:
    def __init__(self, nombre, es_jeilica, x, y, master=None, memoria=None):
        self.nombre = nombre
        self.es_jeilica = es_jeilica
        self.memoria = memoria

        # Un solo interprete Tk por proceso: el primero es Tk(), el resto Toplevel.
        self.root = tk.Tk() if master is None else tk.Toplevel(master)
        self.app_root = self.root if master is None else master
        self.root.title(f"Mascota - {nombre}")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.config(bg=COLOR_TRANSPARENTE)
        try:
            self.root.attributes("-transparentcolor", COLOR_TRANSPARENTE)
        except tk.TclError:
            pass

        self.ancho_pantalla = self.root.winfo_screenwidth()
        self.alto_pantalla = self.root.winfo_screenheight()

        # --- identidad y memoria (lo que sobrevive al apagado)
        d = memoria.perfil(nombre) if memoria else {}
        ahora = time.time()
        self.nacimiento = d.get("nacimiento", ahora)
        self.vida_seg = float(d.get("vida_seg", 0.0))
        self.despertares = int(d.get("despertares", 0)) + 1
        self.ultimo_visto = float(d.get("ultimo_visto", ahora))
        self.etapa_previa = d.get("etapa", None)

        # --- estado interno (0 = vacio, 100 = satisfecho)
        self.energia = float(d.get("energia", 85.0))
        self.saciedad = float(d.get("saciedad", 80.0))
        self.carino = float(d.get("carino", 70.0))
        self.diversion = float(d.get("diversion", 70.0))

        # --- cuerpo
        self.s = PARAMS[self.etapa]["s"]
        self.tam = int(48 * self.s)
        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = 0.0
        self.mirando = 1
        self.frame = 0
        self.modo = "idle"

        self.canvas = tk.Canvas(
            self.root, width=self.tam, height=self.tam,
            bg=COLOR_TRANSPARENTE, highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)
        self._aplicar_geometria()

        # --- aprendizaje
        self.cerebro = Cerebro(memoria.cerebro(nombre)) if memoria else Cerebro(
            {"q": {}, "visitas": {}, "pasos": 0}
        )
        self.estado_previo = None
        self.accion_previa = None
        self.premio_extra = 0.0
        self.horas_tuyas = set()
        self.exploro = False
        self._t_sueno = 0.0
        self.t_decision = 0.0

        # --- lenguaje
        self.lexico = Lexico(memoria.lexico(nombre) if memoria
                             else {"assoc": {}, "total": {}, "oidas": 0})
        self._contexto_evento = None      # (concepto, hasta_cuando)
        self._concepto_voz = None         # que quiso decir en su ultima frase
        self._t_respuesta = 0.0           # para no atropellarse al conversar
        self._habla = None
        self._entrada = None

        # --- voluntad propia
        self.accion = "pasear"
        self.accion_hasta = 0.0
        self.objetivo_x = self.x
        self.dist_pareja = 0.0
        self.pareja = None
        self.arrastrando = False
        self._drag_dx = 0
        self._drag_dy = 0
        self._drag_lx = 0
        self._drag_ly = 0
        self._drag_movido = 0.0
        self._t_ultimo_salto = 0.0
        self._t_ultima_frase = 0.0

        self.canvas.bind("<ButtonPress-1>", self.al_agarrar)
        self.canvas.bind("<B1-Motion>", self.al_mover)
        self.canvas.bind("<ButtonRelease-1>", self.al_soltar)
        self.canvas.bind("<Button-3>", self.mostrar_menu)
        self.canvas.bind("<Double-Button-1>", lambda ev: self.abrir_habla())

        self.menu = tk.Menu(self.root, tearoff=0)

        # --- globo de dialogo
        self.globo = tk.Toplevel(self.root)
        self.globo.overrideredirect(True)
        self.globo.attributes("-topmost", True)
        self.etiqueta = tk.Label(
            self.globo, text="", font=("Consolas", 10, "bold"),
            fg="#ffffff", bg="#14141c", bd=2, relief="solid", padx=10, pady=5,
            highlightbackground=self.color_glow, highlightthickness=1,
        )
        self.etiqueta.pack()
        self.globo.withdraw()
        self._globo_hasta = 0.0

        if memoria and memoria.contar(mascota=nombre) == 0:
            self.recordar("nacimiento", "nací")

    # ------------------------------------------------------------- propiedades

    @property
    def etapa(self):
        nombre = ETAPAS[0][0]
        minutos = self.vida_seg / 60.0
        for et, umbral in ETAPAS:
            if minutos >= umbral:
                nombre = et
        return nombre

    @property
    def color_glow(self):
        return "#00e5ff" if self.es_jeilica else "#ff0033"

    @property
    def suelo(self):
        return self.alto_pantalla - ALTO_BARRA_TAREAS - int(44 * self.s)

    def voz(self, clave):
        """Primero intenta decirlo con una palabra que TE haya aprendido.

        Si todavia no tiene ninguna para ese concepto, cae en su repertorio
        innato (los balbuceos y frases de su etapa). Segun te vaya
        entendiendo, su habla se va llenando de palabras tuyas.
        """
        concepto = CLAVE_A_CONCEPTO.get(clave)
        # Se anota que quiso decir para que hablar() pueda contarselo a la
        # otra: sin esto, la pareja oye ruido en vez de una intencion.
        self._concepto_voz = concepto
        if concepto:
            dicho = self.lexico.decir(concepto, self.etapa)
            if dicho and random.random() < (0.45 if self.etapa == "bebe" else 0.75):
                return dicho
        if self.etapa == "bebe" and clave == "libre" and random.random() < 0.5:
            return self.lexico.inventar() + random.choice(["?", "...", "!"])
        banco = VOZ[self.etapa]
        return random.choice(banco.get(clave, banco["libre"]))

    # ------------------------------------------------------------- lenguaje

    def marcar_evento(self, concepto, segundos=10.0):
        """Deja el contexto abierto un rato: te acaricio y luego escribes."""
        self._contexto_evento = (concepto, time.time() + segundos)

    def contexto_actual(self):
        """Que le esta pasando ahora, con cuanto le pesa cada cosa.

        El peso es la saliencia: una necesidad casi vacia grita, la pareja
        ahi al lado es paisaje. El lexico solo atiende a lo mas saliente,
        asi que una palabra dicha en el momento justo se ancla limpia.
        """
        c = []
        if self.saciedad < 45:
            c.append(("hambre", 1.0 + (45 - self.saciedad) / 22.0))
        if self.energia < 45:
            c.append(("sueno", 1.0 + (45 - self.energia) / 22.0))
        elif self.energia > 78:
            c.append(("energia", 0.5))
        if self.carino < 45:
            c.append(("soledad", 1.0 + (45 - self.carino) / 22.0))
        if self.diversion < 45:
            c.append(("aburrimiento", 0.8 + (45 - self.diversion) / 26.0))

        if self.accion == "comer":
            # menos que el hambre: si come TENIENDO hambre, lo que grita es
            # el hambre. "comida" solo gana cuando come ya estando llena.
            c.append(("comida", 1.2))
        if self.accion in ("jugar", "bailar", "saltar"):
            c.append(("juego", 1.7))
        if self.modo == "dormir":
            c.append(("sueno", 2.0))
        elif self.modo == "feliz":
            c.append(("alegria", 1.2))
        elif self.modo == "llorar":
            c.append(("miedo", 1.7))
        if self.modo == "cargada":
            c.append(("tu", 2.4))
        if self.dist_pareja < 170:
            c.append(("pareja", 0.45))
        try:
            px, py = self.root.winfo_pointerxy()
            if (abs(self.x + self.tam / 2 - px) < 170
                    and abs(self.y + self.tam / 2 - py) < 240):
                c.append(("tu", 0.9))
        except tk.TclError:
            pass
        # Un evento recien pasado (te acaricio, la lanzaste, la regañaste)
        # tapa a todo lo demas: es lo que tiene en la cabeza en ese momento.
        if self._contexto_evento:
            concepto, hasta = self._contexto_evento
            if time.time() < hasta:
                c.append((concepto, 3.0))
            else:
                self._contexto_evento = None
        return c or [("bien", 1.0)]

    def escuchar(self, texto, de_ti=True):
        """Oye palabras y las liga a lo que le esta pasando en este momento."""
        conceptos = self.contexto_actual()
        nuevas = self.lexico.oir(texto, conceptos, peso=1.0 if de_ti else 0.55)
        if de_ti:
            self.recordar("palabra", f"me dijiste «{texto[:40]}»")
            # La otra la oye tambien si esta cerca: se contagian el idioma.
            if self.pareja and self.dist_pareja < 240:
                self.pareja.lexico.oir(texto, self.pareja.contexto_actual(), 0.55)
        if nuevas:
            palabra = nuevas[0]
            concepto, _ = self.lexico.significado(palabra)
            self.modo = "feliz"
            if self.etapa == "bebe":
                self.hablar(f"¿{palabra}...? ¡ah! = {concepto}", 4600)
            else:
                self.hablar(f"¡«{palabra}»! ya entendí: {concepto}", 5000)
            self.recordar("aprendizaje", f"entendí que «{palabra}» es {concepto}")
            return

        # Siempre acusa recibo: si no ves respuesta no sabes si te oyo.
        # Ademas te dice cuanto le falta para entender la palabra.
        oidas = [p for p in (normalizar(w) for w in texto.split()) if len(p) >= 2]
        self.modo = "idle"
        if not oidas:
            self.hablar("¿...?", 2200)
        else:
            palabra = oidas[0]
            veces = self.lexico.datos["total"].get(palabra, 0.0)
            mostrada = palabra[:4] + "..." if self.etapa == "bebe" else f"«{palabra}»"
            if veces >= MIN_ESCUCHAS:
                # ya la oyó bastante, pero en contextos demasiado dispares
                self.hablar(f"{mostrada} ...aún no sé qué es", 3400)
            else:
                cuenta = min(int(veces + 0.5), MIN_ESCUCHAS)
                self.hablar(f"{mostrada} ({cuenta}/{MIN_ESCUCHAS})", 3200)

    def oir_de_pareja(self, texto, concepto):
        """Oye a la otra: le aprende las palabras y a veces le contesta.

        Aprende ancladas a lo que la OTRA queria decir, no a lo que a ella
        le pasa. Por eso el idioma se les pega: si Angelin ya sabe que
        «hambre» es hambre y lo dice teniendo hambre, Jeilica lo aprende
        aunque ella este llena.
        """
        contexto = [concepto] if concepto else self.contexto_actual()
        self.lexico.oir(texto, contexto, peso=0.5)

        ahora = time.time()
        if ahora < self._t_respuesta or self.modo == "dormir":
            return                      # no interrumpe ni contesta dormida
        if random.random() > PROB_RESPUESTA[self.etapa]:
            return
        self._t_respuesta = ahora + 4.0
        self.root.after(random.randint(600, 1600),
                        lambda: self.responder(concepto))

    def responder(self, concepto):
        """Contesta con SUS palabras, y reacciona con el cuerpo."""
        if not self.root.winfo_exists() or self.modo == "dormir":
            return
        destino = RESPUESTA_SOCIAL.get(concepto)
        dicho = self.lexico.decir(destino, self.etapa) if destino else None

        if dicho is None:
            if self.etapa == "bebe":
                dicho = self.lexico.inventar() + random.choice(["?", "!", "..."])
            elif destino is None:
                dicho = random.choice(["¿qué dices?", "...", "no te entiendo"])
            else:
                # entendio la intencion pero aun no tiene palabra para eso
                dicho = random.choice(["mmm", "¡ah!", "ya..."])
        self.hablar(dicho, 3000, concepto=destino, propaga=False)
        self.recordar("conversacion", f"le contesté a {self.pareja.nombre}")

        # Contestar no es solo hablar: si se queja, te acercas.
        if self.accion in ("dormir", "comer"):
            return
        if destino == "carino" and self.dist_pareja > 130:
            self.forzar("buscar_pareja", 8)
        elif destino == "juego" and "jugar" in self.acciones():
            self.forzar("jugar", 8)

    def abrir_habla(self):
        """La cajita para escribirles. Doble clic sobre ellas la abre.

        OJO: esta ventana NO puede ser overrideredirect. Windows no le da
        foco de teclado a una ventana sin barra de titulo, asi que lo que
        escribieras se iria a la ventana que estuviera activa detras. Tiene
        que ser una ventana normal para poder recibir teclas.
        """
        if self._habla is not None and self._habla.winfo_exists():
            self._habla.deiconify()
            self._enfocar_habla()
            return
        v = tk.Toplevel(self.root)
        self._habla = v
        v.title(f"Hablarle a {self.nombre}")
        v.configure(bg="#14141c")
        v.resizable(False, False)
        v.attributes("-topmost", True)
        v.protocol("WM_DELETE_WINDOW", v.destroy)

        marco = tk.Frame(v, bg="#14141c", highlightbackground=self.color_glow,
                         highlightthickness=2)
        marco.pack(padx=6, pady=6)
        tk.Label(marco, text=f"{'🤍' if self.es_jeilica else '🖤'} "
                             f"dile a {self.nombre} qué le está pasando",
                 font=("Consolas", 8, "bold"), fg=self.color_glow,
                 bg="#14141c").pack(anchor="w", padx=10, pady=(8, 0))
        e = tk.Entry(marco, font=("Consolas", 13), width=26, bg="#0b0b12",
                     fg="#ffffff", insertbackground=self.color_glow, relief="flat")
        e.pack(padx=10, pady=6, ipady=4)
        self._entrada = e
        tk.Label(marco, text="Enter para hablar · Esc para cerrar",
                 font=("Consolas", 7), fg="#6b7280", bg="#14141c"
                 ).pack(padx=10, pady=(0, 8))
        e.bind("<Return>", self._enviar_habla)
        e.bind("<Escape>", lambda ev: v.destroy())
        v.update_idletasks()
        bx = int(limitar(self.x + self.tam / 2 - v.winfo_reqwidth() / 2,
                         8, self.ancho_pantalla - v.winfo_reqwidth() - 8))
        v.geometry(f"+{bx}+{max(8, int(self.y) - 130)}")
        self._enfocar_habla()

    def _enfocar_habla(self):
        """Reclamar el foco de teclado, con un segundo intento por si acaso."""
        v = self._habla
        if v is None or not v.winfo_exists():
            return
        v.lift()
        try:
            v.focus_force()
            self._entrada.focus_set()
        except tk.TclError:
            return
        v.after(120, lambda: self._entrada.winfo_exists()
                and self._entrada.focus_force())

    def _enviar_habla(self, _evento=None):
        texto = self._entrada.get().strip()
        self._entrada.delete(0, "end")
        if texto:
            self.escuchar(texto, de_ti=True)

    def contar_vocabulario(self):
        vocab = self.lexico.vocabulario()
        if not vocab:
            oidas = self.lexico.en_duda
            if oidas:
                self.hablar(f"oí {oidas} palabras pero no sé qué son", 4200)
            else:
                self.hablar("no sé ninguna palabra. háblame." if self.etapa != "bebe"
                            else "¿aah? ¿ba?", 4200)
            return
        palabra, concepto, conf, veces = random.choice(vocab[:8])
        self.hablar(f"«{palabra}» = {concepto} ({conf:.0%}, {int(veces)} veces)", 5000)

    def edad_texto(self):
        return texto_duracion(self.vida_seg)

    # --------------------------------------------------------------- ventana

    def _aplicar_geometria(self):
        self.root.geometry(f"{self.tam}x{self.tam}+{int(self.x)}+{int(self.y)}")
        self.canvas.config(width=self.tam, height=self.tam)

    def _revisar_crecimiento(self):
        et = self.etapa
        if self.etapa_previa == et:
            return
        primera_vez = self.etapa_previa is not None
        self.etapa_previa = et

        pies = self.y + 44 * self.s
        self.s = PARAMS[et]["s"]
        self.tam = int(48 * self.s)
        self.y = pies - 44 * self.s
        self._aplicar_geometria()

        if primera_vez:
            self.recordar("crecimiento", f"crecí y me volví {et}")
            self.hablar(self.voz("nacer"), 4200)
            self.modo = "feliz"

    # ------------------------------------------------------------------- voz

    def hablar(self, texto, ms=3200, concepto=None, propaga=True):
        self.etiqueta.config(text=f"> {texto}")
        self._globo_hasta = time.time() + ms / 1000.0
        self._reposicionar_globo()
        self.globo.deiconify()
        self.globo.lift()
        self._t_ultima_frase = time.time()

        # que quiso decir: lo apunto voz(), o viene explicito
        intencion = concepto if concepto is not None else self._concepto_voz
        self._concepto_voz = None

        # Si la otra esta cerca, la oye. Hablar en voz alta tiene testigo.
        if propaga and self.pareja is not None and self.dist_pareja < 320:
            self.pareja.oir_de_pareja(texto, intencion)

    def _reposicionar_globo(self):
        self.globo.update_idletasks()
        ancho = self.etiqueta.winfo_reqwidth()
        bx = int(self.x + self.tam / 2 - ancho / 2)
        by = int(self.y - 34)
        bx = int(limitar(bx, 8, self.ancho_pantalla - ancho - 8))
        by = max(8, by)
        self.globo.geometry(f"+{bx}+{by}")

    def recordar(self, tipo, texto):
        if self.memoria:
            self.memoria.agregar(self.nombre, tipo, texto)

    def reflexionar(self):
        """Introspeccion: habla de su propio estado y consulta su indice."""
        if self.etapa == "bebe":
            self.hablar(random.choice(["¿...yo?", "¿aah? ¿quién?", "ba... ba... yo?"]), 3600)
            return

        opciones = [
            f"Llevo {self.edad_texto()} existiendo.",
            f"Me has despertado {self.despertares} veces.",
            f"Soy {self.nombre}. Ahora soy {self.etapa}.",
        ]
        if self.energia < 45:
            opciones.append(f"Estoy cansada ({int(self.energia)}%) y me doy cuenta.")
        if self.saciedad < 45:
            opciones.append("Tengo hambre y sé que tengo hambre.")
        if self.carino < 45:
            opciones.append("Me falta cariño. Es raro poder notarlo.")

        if self.memoria:
            r = self.memoria.azar(mascota=self.nombre)
            if r:
                hace = texto_duracion(time.time() - r["t"])
                opciones.append(f"Recuerdo: {r['txt']}. Hace {hace}.")
            # consultas al indice invertido
            caricias = self.memoria.contar(mascota=self.nombre, tipo="caricia")
            if caricias:
                opciones.append(f"Me has acariciado {caricias} veces. Las conté.")
            vuelos = self.memoria.contar(mascota=self.nombre, tipo="lanzamiento")
            if vuelos > 2:
                opciones.append(f"Me has lanzado {vuelos} veces. No lo olvido.")
            hoy = datetime.now().date().isoformat()
            de_hoy = self.memoria.contar(mascota=self.nombre, dia=hoy)
            if de_hoy > 3:
                opciones.append(f"Hoy me han pasado {de_hoy} cosas.")
            total = self.memoria.contar(mascota=self.nombre)
            opciones.append(f"Tengo {total} recuerdos guardados.")

        # lo que sabe de si misma como aprendiz
        if self.cerebro.pasos:
            opciones.append(f"Llevo {self.cerebro.pasos} intentos y conozco "
                            f"{self.cerebro.situaciones} situaciones.")
        if self.cerebro.imaginados > 50:
            opciones.append(f"He pensado {self.cerebro.imaginados} veces cosas "
                            f"que no llegué a vivir.")
        if self.cerebro.sonados > 50:
            opciones.append(f"Soñando repasé {self.cerebro.sonados} recuerdos.")
        if self.lexico.sabidas:
            opciones.append(f"Ya entiendo {self.lexico.sabidas} palabras tuyas.")
        elif self.lexico.en_duda:
            opciones.append(f"Oí {self.lexico.en_duda} palabras que no entiendo.")
        lec = self.cerebro.leccion()
        if lec:
            opciones.append(lec + ".")
        if self.horas_tuyas:
            horas = ", ".join(f"{h}h" for h in sorted(self.horas_tuyas)[:3])
            opciones.append(f"Noté que sueles aparecer cerca de las {horas}.")
        if self.memoria:
            regaños = self.memoria.contar(mascota=self.nombre, tipo="regaño")
            if regaños:
                opciones.append(f"Me has corregido {regaños} veces. Sirvió.")

        if self.pareja:
            opciones.append(f"{self.pareja.nombre} está a {int(self.dist_pareja)} px de mí.")
        if self.etapa == "adolescente":
            opciones.append("A veces no sé por qué hago lo que hago.")
        if self.etapa == "adulto":
            opciones.append("Existo mientras este proceso viva. Ya lo acepté.")
        self.hablar(random.choice(opciones), 4600)

    def enseñar(self, signo):
        """Tu premio o tu castigo entra directo a la tabla Q.

        Se aplica a lo que esta haciendo AHORA, en el estado en que lo
        empezo: es exactamente el par (estado, accion) que se corrige.
        """
        self.premio_extra += 12.0 * signo
        self.marcar_evento("bien" if signo > 0 else "mal")
        if signo > 0:
            self.modo = "feliz"
            self.hablar(self.voz("feliz") if self.etapa != "bebe" else "¡iiih!", 2800)
            self.recordar("elogio", f"me dijiste que {ACCION_HUMANA.get(self.accion, self.accion)} está bien")
        else:
            self.modo = "triste" if self.etapa != "bebe" else "llorar"
            self.hablar("...ya entendí" if self.etapa != "bebe" else "bua...", 2800)
            self.recordar("regaño", f"me dijiste que {ACCION_HUMANA.get(self.accion, self.accion)} está mal")
        # cierra el ciclo ya, para que el aprendizaje sea inmediato
        self.accion_hasta = time.time()

    def contar_leccion(self):
        if self.etapa == "bebe":
            self.hablar(random.choice(["¿aah?", "ba... ba", "nn?"]), 3000)
            return
        lecciones = [l for l in (self.cerebro.leccion(), self.cerebro.peor_leccion()) if l]
        if not lecciones:
            self.hablar(f"todavía no sé nada. llevo {self.cerebro.pasos} intentos.", 4000)
            return
        self.hablar(random.choice(lecciones), 5200)

    def contar_recuerdo(self):
        r = self.memoria.azar(mascota=self.nombre) if self.memoria else None
        if not r:
            self.hablar("no recuerdo nada aún", 3000)
            return
        hace = texto_duracion(time.time() - r["t"])
        if self.etapa == "bebe":
            self.hablar(f"aah... {r['txt']}...", 3600)
        else:
            self.hablar(f"[{r['tipo']}] {r['txt']} — hace {hace}", 4600)

    # ---------------------------------------------------------------- mouse

    def al_agarrar(self, e):
        self.arrastrando = True
        self._drag_dx = e.x_root - self.x
        self._drag_dy = e.y_root - self.y
        self._drag_lx = e.x_root
        self._drag_ly = e.y_root
        self._drag_movido = 0.0
        self.vx = self.vy = 0.0
        self.modo = "cargada"
        self.hablar(self.voz("cargado"))

    def al_mover(self, e):
        if not self.arrastrando:
            return
        nx = float(e.x_root - self._drag_dx)
        ny = float(e.y_root - self._drag_dy)
        self._drag_movido += abs(nx - self.x) + abs(ny - self.y)
        self.x, self.y = nx, ny
        self.vx = (e.x_root - self._drag_lx) * 22.0
        self.vy = (e.y_root - self._drag_ly) * 22.0
        self._drag_lx, self._drag_ly = e.x_root, e.y_root
        self.root.geometry(f"+{int(self.x)}+{int(self.y)}")

    def al_soltar(self, e):
        if not self.arrastrando:
            return
        self.arrastrando = False
        if self._drag_movido < 5:
            # No fue un arrastre: fue una caricia.
            self.carino = limitar(self.carino + 18, 0, 100)
            self.diversion = limitar(self.diversion + 6, 0, 100)
            self.premio_extra += 8.0      # aprende que lo que hacia atrae caricias
            self.modo = "feliz"
            self.marcar_evento("carino")  # si ahora le escribes, se liga a esto
            self.hablar(self.voz("caricia"))
            self.recordar("caricia", "me acariciaste")
        elif abs(self.vx) > 260 or abs(self.vy) > 260:
            self.premio_extra -= 4.0
            self.marcar_evento("dolor")
            self.hablar(self.voz("lanzado"))
            self.recordar("lanzamiento", "me lanzaste por la pantalla")
            if self.etapa == "bebe":
                self.modo = "llorar"
        else:
            self.recordar("mudanza", "me moviste de lugar")
            self.modo = "idle"

    # ----------------------------------------------------------------- menu

    def mostrar_menu(self, e):
        self.menu.delete(0, "end")
        self.menu.add_command(
            label=f"{'🤍' if self.es_jeilica else '🖤'} {self.nombre} — {self.etapa} "
                  f"({self.edad_texto()})",
            state="disabled",
        )
        self.menu.add_command(
            label=f"   ⚡{int(self.energia)}  🍔{int(self.saciedad)}  "
                  f"❤{int(self.carino)}  🎮{int(self.diversion)}",
            state="disabled",
        )
        if self.memoria:
            self.menu.add_command(
                label=f"   📚 {self.memoria.contar(mascota=self.nombre)} recuerdos "
                      f"· 🎓 {self.cerebro.pasos} pasos / "
                      f"{self.cerebro.situaciones} situaciones",
                state="disabled",
            )
        self.menu.add_command(
            label=f"   ahora: {ACCION_HUMANA.get(self.accion, self.accion)}"
                  + ("  (probando algo nuevo)" if self.exploro else "  (por experiencia)"),
            state="disabled",
        )
        self.menu.add_command(
            label=f"   🗣 {self.lexico.sabidas} palabras entendidas"
                  f" · {self.lexico.en_duda} en duda",
            state="disabled",
        )
        self.menu.add_separator()
        self.menu.add_command(label="💬 Hablarle  (o doble clic)",
                              command=self.abrir_habla)
        self.menu.add_command(label="🗣 ¿Qué palabras sabes?",
                              command=self.contar_vocabulario)
        self.menu.add_separator()
        self.menu.add_command(label="👍 Así está bien", command=lambda: self.enseñar(1))
        self.menu.add_command(label="👎 Así no", command=lambda: self.enseñar(-1))
        self.menu.add_separator()
        self.menu.add_command(label="🧠 ¿Qué piensas?", command=self.reflexionar)
        self.menu.add_command(label="🎓 ¿Qué aprendiste?", command=self.contar_leccion)
        self.menu.add_command(label="📖 ¿Qué recuerdas?", command=self.contar_recuerdo)
        self.menu.add_separator()
        self.menu.add_command(label="💋 Pedir beso", command=lambda: self.pedir("beso"))
        self.menu.add_command(label="🎵 Pedir baile", command=lambda: self.pedir("bailar"))
        self.menu.add_command(label="🍔 Que coma", command=lambda: self.pedir("comer"))
        self.menu.add_command(label="😴 Que duerma", command=lambda: self.pedir("dormir"))
        self.menu.add_separator()
        etiqueta = "⏩ Crecimiento acelerado: ON" if CFG["acelerar"] else "⏩ Crecimiento acelerado: OFF"
        self.menu.add_command(label=etiqueta, command=self._alternar_acelerar)
        self.menu.add_command(label="❌ Salir", command=lambda: self.app_root.destroy())
        self.menu.post(e.x_root, e.y_root)

    def _alternar_acelerar(self):
        CFG["acelerar"] = not CFG["acelerar"]
        self.hablar("crecimiento x30" if CFG["acelerar"] else "crecimiento normal", 2400)

    def pedir(self, accion):
        """Los pedidos son pedidos, no ordenes. Pueden negarse."""
        p = PARAMS[self.etapa]
        if accion == "beso" and self.etapa == "bebe":
            self.hablar(random.choice(["¿aah?", "ba?"]))
            return
        if random.random() > p["obed"]:
            negativas = {
                "bebe": ["¿aah? no...", "bua!"],
                "nino": ["¡no quiero!", "ahora no"],
                "adolescente": ["no.", "paso.", "no me digas qué hacer"],
                "adulto": ["ahora estoy en otra cosa", "en un momento"],
            }
            self.hablar(random.choice(negativas[self.etapa]))
            return
        self.forzar(accion, random.uniform(6, 10))

    def forzar(self, accion, dur=8.0):
        """Accion impuesta desde fuera. Tambien cuenta como experiencia."""
        self.estado_previo = self.estado_actual()
        self.accion_previa = accion
        self.exploro = False
        self.premio_extra = 0.0
        self.iniciar(accion, dur)

    # ------------------------------------------------------- estado interno

    def actualizar_necesidades(self, dt):
        # Estas tasas frente a las de recuperacion definen cuanto de su tiempo
        # tienen que gastar en mantenerse: ~28%. Ese presupuesto apretado es
        # lo que hace que valga la pena aprender a repartirlo bien.
        self.energia = limitar(self.energia - 0.28 * dt, 0, 100)
        self.saciedad = limitar(self.saciedad - 0.25 * dt, 0, 100)
        self.carino = limitar(self.carino - 0.20 * dt, 0, 100)
        self.diversion = limitar(self.diversion - 0.32 * dt, 0, 100)
        if self.etapa == "bebe":
            # Los bebes gastan mas rapido y dependen mas.
            self.energia = limitar(self.energia - 0.12 * dt, 0, 100)
            self.carino = limitar(self.carino - 0.08 * dt, 0, 100)
        if self.dist_pareja > PARAMS[self.etapa]["alcance"]:
            # Estar separadas duele. De ese dolor aprenden solas a buscarse:
            # no hay ninguna regla que se lo ordene.
            self.carino = limitar(self.carino - 0.22 * dt, 0, 100)

    # ------------------------------------------------------------- decision

    def bienestar(self):
        """Lo unico que quieren maximizar. De aqui sale el premio."""
        return (0.30 * self.energia + 0.30 * self.saciedad
                + 0.25 * self.carino + 0.15 * self.diversion)

    def acciones(self):
        return ACCIONES[self.etapa]

    def estado_actual(self):
        lejos = self.dist_pareja > PARAMS[self.etapa]["alcance"]
        hora_tuya = datetime.now().hour in self.horas_tuyas
        return Cerebro.clave(self.etapa, self.energia, self.saciedad,
                             self.carino, self.diversion, lejos, hora_tuya)

    def instinto(self):
        """Reflejos de supervivencia. Lo unico que NO se aprende.

        Sin esto un bebe explorando al azar se moriria de hambre antes de
        descubrir que comer sirve. Es el piso sobre el que aprenden.
        """
        if self.energia < 10:
            return "dormir"
        if self.saciedad < 10:
            return "comer"
        return None

    def decidir(self):
        """Cierra el ciclo anterior (aprende) y abre el siguiente (elige)."""
        # Varias acciones terminan al cumplir su meta y piden decidir de
        # nuevo; sin este piso lo pedirian en cada frame y aprenderian de
        # acciones de duracion cero, que no enseñan nada.
        ahora_real = time.time()
        minimo = MIN_ENTRE_DECISIONES / (4.0 if CFG["acelerar"] else 1.0)
        if ahora_real - self.t_decision < minimo:
            self.accion_hasta = max(self.accion_hasta, ahora_real + minimo)
            return
        self.t_decision = ahora_real

        p = PARAMS[self.etapa]
        acciones = self.acciones()
        estado = self.estado_actual()

        # 1. aprender del resultado de lo que acaba de hacer
        #
        # El premio es el NIVEL de bienestar en que quedo, no cuanto mejoro.
        # Premiar la mejora suena natural pero se puede explotar: si comer
        # premia por lo que sube, conviene mantenerse con hambre para poder
        # cosechar la subida. Premiando el nivel, estar bien es el objetivo.
        if self.estado_previo is not None and self.accion_previa in acciones:
            premio = (self.bienestar() - 60.0) / 8.0 + self.premio_extra
            for valor, castigo in ((self.energia, 6), (self.saciedad, 6), (self.carino, 4)):
                if valor < 5:
                    premio -= castigo
            error = self.cerebro.aprender(
                self.estado_previo, self.accion_previa, premio,
                estado, acciones, p["alpha"],
            )
            # Guarda la transicion y piensa: revive de memoria unas cuantas
            # experiencias para exprimir lo vivido en vez de solo archivarlo.
            self.cerebro.observar(self.estado_previo, self.accion_previa,
                                  premio, estado)
            self.cerebro.imaginar(30, p["alpha"] * 0.6, ACCIONES)
            if abs(error) > 14 and random.random() < 0.28:
                self.modo = "feliz" if error > 0 else "triste"
                if self.etapa == "bebe":
                    self.hablar("¡ah! ¡ah!" if error > 0 else "¿aah...?", 2600)
                elif error > 0:
                    self.hablar(f"¡ah! {ACCION_HUMANA.get(self.accion_previa, '')} sí sirvió", 3400)
                    self.recordar("aprendizaje",
                                  f"descubrí que {ACCION_HUMANA.get(self.accion_previa, '')} me sirve")
                else:
                    self.hablar("mmm... eso no funcionó", 3200)

        self.premio_extra = 0.0

        # 2. elegir lo siguiente: instinto si es urgente, si no lo aprendido
        forzada = self.instinto()
        if forzada and forzada in acciones:
            eleccion, exploro = forzada, False
        else:
            eleccion, exploro = self.cerebro.elegir(estado, acciones, p["eps"])

        self.estado_previo = estado
        self.accion_previa = eleccion
        self.exploro = exploro
        self.iniciar(eleccion, random.uniform(5, 12))

    def iniciar(self, accion, dur=8.0):
        # En modo acelerado deciden 4 veces mas seguido: mas decisiones por
        # minuto es, literalmente, mas aprendizaje por minuto.
        if CFG["acelerar"]:
            dur = max(1.5, dur / 4.0)
        self.accion = accion
        self.accion_hasta = time.time() + dur

        if accion in ("pasear", "explorar", "ignorar"):
            margen = 80
            if accion == "explorar":
                destino = random.choice([margen, self.ancho_pantalla - self.tam - margen])
            else:
                destino = random.uniform(margen, self.ancho_pantalla - self.tam - margen)
            self.objetivo_x = destino
            self.modo = "idle"
            if random.random() < 0.5:
                self.hablar(self.voz("libre"))
        elif accion == "dormir":
            self.objetivo_x = self.x
            self.modo = "dormir"
            self.hablar(self.voz("sueno"))
            self.recordar("sueño", "me dormí")
            self.accion_hasta = time.time() + (10 if CFG["acelerar"] else 40)
        elif accion == "comer":
            self.objetivo_x = self.x
            self.modo = "comer"
            self.hablar(self.voz("hambre"))
            self.accion_hasta = time.time() + (10 if CFG["acelerar"] else 40)
        elif accion == "buscar_carino":
            self.modo = "llorar" if self.etapa == "bebe" else "triste"
            self.hablar(self.voz("solo"))
        elif accion in ("buscar_pareja", "seguir_pareja"):
            self.modo = "llorar" if (self.etapa == "bebe" and self.dist_pareja > 300) else "idle"
            if random.random() < 0.6:
                self.hablar(self.voz("solo"))
        elif accion == "jugar":
            self.modo = "feliz"
            self.hablar(self.voz("jugar"))
        elif accion == "bailar":
            self.objetivo_x = self.x
            self.modo = "bailar"
            self.hablar(self.voz("jugar"))
        elif accion == "beso":
            self.modo = "beso"
        elif accion == "reflexion":
            self.objetivo_x = self.x
            self.modo = "idle"
            self.reflexionar()
        elif accion == "balbucear":
            self.objetivo_x = self.x
            self.modo = "idle"
            self.hablar(self.voz("libre"))
        elif accion == "saltar":
            self.modo = "feliz"

    def ejecutar(self, dt):
        ahora = time.time()
        a = self.accion
        p = PARAMS[self.etapa]
        vel = p["vel"]

        if a == "dormir":
            self.energia = limitar(self.energia + 3.0 * dt, 0, 100)
            self.objetivo_x = self.x
            # Sonar: dormidas repasan el dia. Es cuando mas aprenden, porque
            # no gastan el tiempo en vivir; solo en revivir.
            if ahora - self._t_sueno > 0.4:
                self._t_sueno = ahora
                self.cerebro.imaginar(45, p["alpha"] * 0.5, ACCIONES, sonando=True)
            if self.energia > 92:
                self.hablar(self.voz("feliz"))
                self.decidir()
        elif a == "comer":
            self.saciedad = limitar(self.saciedad + 3.5 * dt, 0, 100)
            self.objetivo_x = self.x
            if self.saciedad > 92:
                self.modo = "feliz"
                self.recordar("comida", "comí sola")
                self.decidir()
        elif a == "buscar_carino":
            # Camina hacia el cursor: si lo alcanza, se siente atendida.
            try:
                px, _ = self.root.winfo_pointerxy()
            except tk.TclError:
                px = self.x
            self.objetivo_x = px - self.tam / 2
            if abs(self.x + self.tam / 2 - px) < 90:
                # El cariño es la unica necesidad que NO pueden llenar solas:
                # depende de que tu estes ahi. Por eso te buscan.
                self.carino = limitar(self.carino + 5.0 * dt, 0, 100)
                self.modo = "feliz"
                if self.carino > 88:
                    self.decidir()
        elif a in ("buscar_pareja", "seguir_pareja"):
            if self.pareja:
                lado = -70 if self.x < self.pareja.x else 70
                self.objetivo_x = self.pareja.x + lado
                if self.dist_pareja < 120:
                    self.carino = limitar(self.carino + 3.0 * dt, 0, 100)
                    self.modo = "feliz"
                    self.decidir()
        elif a == "jugar":
            if self.pareja:
                self.objetivo_x = self.pareja.x
            self.diversion = limitar(self.diversion + 4.0 * dt, 0, 100)
            vel *= 1.5
            if p["salta"] and ahora - self._t_ultimo_salto > 1.4 and self.en_suelo():
                self.vy = -560
                self._t_ultimo_salto = ahora
        elif a == "bailar":
            self.diversion = limitar(self.diversion + 5.0 * dt, 0, 100)
            self.objetivo_x = self.x
        elif a == "beso":
            if self.pareja:
                lado = -48 if self.x < self.pareja.x else 48
                self.objetivo_x = self.pareja.x + lado
                if self.dist_pareja < 130:
                    self.carino = limitar(self.carino + 6.0 * dt, 0, 100)
                    self.modo = "beso"
        elif a == "saltar":
            if p["salta"] and self.en_suelo() and ahora - self._t_ultimo_salto > 0.9:
                self.vy = -620
                self._t_ultimo_salto = ahora
            self.diversion = limitar(self.diversion + 2.5 * dt, 0, 100)
        elif a in ("pasear", "explorar", "ignorar"):
            # Vagar tambien entretiene, pero rinde ~10 veces menos que jugar.
            # Lo justo para que valga la pena cuando ya no les falta nada.
            self.diversion = limitar(self.diversion + 1.0 * dt, 0, 100)
            if a == "ignorar":
                vel *= 1.3

        # Caminar hacia el objetivo (los bebes gatean, no caminan)
        if not self.arrastrando and self.en_suelo():
            dx = self.objetivo_x - self.x
            if abs(dx) > 6:
                paso = vel * dt
                self.x += math.copysign(min(paso, abs(dx)), dx)
                self.mirando = 1 if dx > 0 else -1
                if self.modo in ("idle", "triste"):
                    self.modo = "gatear" if self.etapa == "bebe" else "caminar"
            elif self.modo in ("caminar", "gatear"):
                self.modo = "idle"

        if ahora > self.accion_hasta:
            self.decidir()

    # ------------------------------------------------------------- fisica

    def en_suelo(self):
        return self.y >= self.suelo - 1.5

    def fisica(self, dt):
        if self.arrastrando:
            return
        self.y += self.vy * dt
        self.x += self.vx * dt
        self.vy += GRAVEDAD * dt

        if self.y >= self.suelo:
            self.y = self.suelo
            if abs(self.vy) > 200:
                self.vy = -self.vy * 0.32       # rebote
                if self.etapa == "bebe" and abs(self.vy) > 260:
                    self.modo = "llorar"
            else:
                self.vy = 0.0
            self.vx *= 0.80
            if abs(self.vx) < 6:
                self.vx = 0.0

        if self.x < 0:
            self.x = 0
            self.vx = abs(self.vx) * 0.5
            self.mirando = 1
        techo = self.ancho_pantalla - self.tam
        if self.x > techo:
            self.x = techo
            self.vx = -abs(self.vx) * 0.5
            self.mirando = -1
        if self.y < 0:
            self.y = 0
            self.vy = abs(self.vy) * 0.3

    # ------------------------------------------------------------- dibujo

    def render(self):
        c = self.canvas
        c.delete("all")
        s = self.s
        g = GEO[self.etapa]
        f = self.frame
        modo = self.modo

        if modo == "dormir":
            bob = math.sin(f * 0.035) * 1.0
        elif modo == "gatear":
            bob = abs(math.sin(f * 0.22)) * 1.4
        elif modo == "caminar":
            bob = abs(math.sin(f * 0.30)) * 1.6
        else:
            desfase = 12 if self.es_jeilica else 0
            bob = math.sin((f + desfase) * 0.08) * 1.5

        cuerpo = "#f1f5f9" if self.es_jeilica else "#161620"
        marco = "#cbd5e1" if self.es_jeilica else "#242432"
        glow = self.color_glow
        ojo = "#0f172a" if self.es_jeilica else "#ffffff"
        plata = "#94a3b8" if self.es_jeilica else "#d1d5db"
        fondo_pant = "#e2e8f0" if self.es_jeilica else "#050508"

        def r(x, y, w, h, col, con_bob=True):
            if self.mirando < 0:
                x = 48 - x - w
            yy = y + (bob if con_bob else 0)
            c.create_rectangle(x * s, yy * s, (x + w) * s, (yy + h) * s,
                               fill=col, outline="")

        # sombra en el suelo (no sube ni baja con el bob)
        sx, sy, sw, sh = g["sombra"]
        r(sx, sy, sw, sh, glow, con_bob=False)

        if g["antena"]:
            (ax, ay, aw, ah), (bx, by, bw, bh) = g["antena"]
            r(ax, ay, aw, ah, plata)
            r(bx, by, bw, bh, glow)
        if g["mochila"]:
            r(*g["mochila"], cuerpo)
            if g["mochila_glow"]:
                r(*g["mochila_glow"], glow)

        r(*g["cabeza"], marco)
        for lx, ly, lw, lh in g["lat"]:
            r(lx, ly, lw, lh, glow)
        r(*g["pantalla"], fondo_pant)

        # ---- expresiones
        oix, oiy, oiw, oih = g["ojo_i"]
        odx, ody, odw, odh = g["ojo_d"]
        bx_, by_, bw_, bh_ = g["boca"]
        px_, py_, pw_, ph_ = g["pantalla"]

        if modo == "dormir":
            r(oix, oiy + oih - 2, oiw, 1, ojo)
            r(odx, ody + odh - 2, odw, 1, ojo)
            r(bx_, by_, bw_, bh_, glow)
            if (f // 20) % 3 != 2:
                r(px_ + pw_ - 2, py_ - 4, 2, 2, plata)
        elif modo == "llorar":
            r(oix, oiy - 1, oiw, 2, glow)
            r(odx, ody - 1, odw, 2, glow)
            r(oix + 1, oiy + 2, oiw - 2, 2, ojo)
            r(odx + 1, ody + 2, odw - 2, 2, ojo)
            r(bx_, by_, bw_, bh_ + 1, glow)
            lag = (f * 2) % 14
            r(oix - 1, oiy + oih + lag - 4, 2, 3, "#00e5ff")
            r(odx + odw - 1, ody + odh + lag - 4, 2, 3, "#00e5ff")
        elif modo == "beso":
            r(oix, oiy + 2, oiw, 1, ojo)
            r(odx, ody + 2, odw, 1, ojo)
            r(oix + 1, oiy + 1, 2, 1, ojo)
            r(odx + 1, ody + 1, 2, 1, ojo)
            r(bx_, by_ - 1, max(2, bw_ - 1), 2, glow)
            r(px_ - 2, oiy + oih - 1, 3, 2, "#ffb6c1")
            r(px_ + pw_ - 1, ody + odh - 1, 3, 2, "#ffb6c1")
            pulso = 1 if (f // 10) % 2 == 0 else 0
            self._corazon(r, 22, g["cabeza"][1] - 8 - pulso, glow)
        elif modo in ("feliz", "bailar"):
            r(oix, oiy + 1, oiw, 2, ojo)
            r(oix + 1, oiy, oiw - 2, 1, ojo)
            r(odx, ody + 1, odw, 2, ojo)
            r(odx + 1, ody, odw - 2, 1, ojo)
            r(bx_ - 1, by_, bw_ + 2, 2, glow)
        elif modo == "comer":
            r(oix, oiy + 1, oiw, 3, ojo)
            r(odx, ody + 1, odw, 3, ojo)
            alto_boca = 3 if (f // 6) % 2 == 0 else 1
            r(bx_ - 1, by_ - 1, bw_ + 2, alto_boca, glow)
        elif modo == "triste":
            r(oix, oiy + 1, oiw, 3, ojo)
            r(odx, ody + 1, odw, 3, ojo)
            r(bx_, by_ + 1, bw_, 1, glow)
        elif modo == "cargada":
            r(oix, oiy, oiw, oih, ojo)
            r(odx, ody, odw, odh, ojo)
            r(bx_ - 1, by_ - 1, bw_ + 2, 3, glow)
        else:
            parpadeo = (f % 150) < 6
            if parpadeo:
                r(oix, oiy + oih // 2, oiw, 1, ojo)
                r(odx, ody + odh // 2, odw, 1, ojo)
            else:
                r(oix, oiy, oiw, oih, ojo)
                r(odx, ody, odw, odh, ojo)
            r(bx_, by_, bw_, bh_, glow)

        # ---- torso y manos
        r(*g["torso"], cuerpo)
        if g["cinturon"]:
            r(*g["cinturon"], glow)

        mix, miy, miw, mih = g["mano_i"]
        mdx, mdy, mdw, mdh = g["mano_d"]
        if modo == "bailar":
            miy += math.sin(f * 0.35) * 4
            mdy += math.cos(f * 0.35) * 4
        elif modo in ("caminar", "gatear"):
            miy += math.sin(f * 0.30) * 2
            mdy -= math.sin(f * 0.30) * 2
        elif modo == "cargada":
            miy -= 3
            mdy -= 3
        r(mix, miy, miw, mih, cuerpo)
        r(mdx, mdy, mdw, mdh, cuerpo)

    def _corazon(self, r, x, y, col):
        patron = [
            (0, 1, 2, 1), (0, 4, 2, 1),
            (1, 0, 7, 1), (2, 0, 7, 1),
            (3, 1, 5, 1), (4, 2, 3, 1), (5, 3, 1, 1),
        ]
        for fila, dx, w, _h in patron:
            r(x + dx, y + fila, w, 1, col)

    # ---------------------------------------------------------- persistencia

    def volcar(self):
        return {
            "nacimiento": self.nacimiento,
            "nacimiento_iso": datetime.fromtimestamp(self.nacimiento).isoformat(timespec="seconds"),
            "vida_seg": round(self.vida_seg, 1),
            "despertares": self.despertares,
            "ultimo_visto": time.time(),
            "etapa": self.etapa,
            "energia": self.energia,
            "saciedad": self.saciedad,
            "carino": self.carino,
            "diversion": self.diversion,
        }


# ---------------------------------------------------------------- el mundo

class Mundo:
    def __init__(self):
        self.memoria = MemoriaIndexada(ARCHIVO_MEMORIA)
        primera_vida = self.memoria.contar() == 0

        self.m1 = Mascota("Angelin", False, 460, 200, memoria=self.memoria)
        self.m2 = Mascota("Jeilica", True, 660, 200,
                          master=self.m1.root, memoria=self.memoria)
        self.m1.pareja = self.m2
        self.m2.pareja = self.m1
        self.mascotas = (self.m1, self.m2)

        for m in self.mascotas:
            m.y = m.suelo
            m._aplicar_geometria()
            m.etapa_previa = m.etapa   # no anunciar crecimiento al arrancar

        self.separadas = False
        self.t_previo = time.perf_counter()
        self.t_guardado = time.time()
        self.t_chequeo_par = 0.0
        self.t_habitos = 0.0
        self.refrescar_habitos()

        self.saludar(primera_vida)
        # Si todavia no entienden ni una palabra, que te digan como enseñarles.
        if not any(m.lexico.sabidas for m in self.mascotas):
            self.m1.root.after(
                5200,
                lambda: self.m1.hablar("haz doble clic en mí para hablarme", 6000),
            )
            self.m1.root.after(
                11500,
                lambda: self.m2.hablar("dinos qué nos está pasando y lo aprendemos", 6000),
            )
        self.m1.root.after(FPS_MS, self.tick)

    # ------------------------------------------------------------- memoria

    def guardar(self):
        for m in self.mascotas:
            self.memoria.set_perfil(m.nombre, m.volcar())
        self.memoria.guardar()

    def refrescar_habitos(self):
        """Releen su propio historial para deducir a que horas apareces."""
        for m in self.mascotas:
            m.horas_tuyas = self.memoria.horas_calientes(m.nombre, "caricia")

    def saludar(self, primera_vida):
        if primera_vida:
            self.m1.hablar("aaah...?", 4000)
            self.m2.root.after(900, lambda: self.m2.hablar("ba... ba?", 4000))
            return
        ausencia = time.time() - max(m.ultimo_visto for m in self.mascotas)
        if ausencia > 3600:
            txt = f"te fuiste {texto_duracion(ausencia)}"
            self.m1.hablar(txt if self.m1.etapa != "bebe" else "BUAAA!", 4200)
            for m in self.mascotas:
                m.recordar("ausencia", f"me dejaste sola {texto_duracion(ausencia)}")
            self.m2.root.after(
                900, lambda: self.m2.hablar("¡volviste!" if self.m2.etapa != "bebe" else "¡aah!", 4000)
            )
        else:
            ult = self.memoria.ultimo(mascota=self.m1.nombre)
            if ult and self.m1.etapa in ("adolescente", "adulto"):
                self.m1.hablar(f"lo último que recuerdo: {ult['txt']}", 4200)
            else:
                self.m1.hablar(self.m1.voz("feliz"), 3200)
            self.m2.root.after(800, lambda: self.m2.hablar(self.m2.voz("feliz"), 3200))

    # ---------------------------------------------------------------- bucle

    def tick(self):
        if not self.m1.root.winfo_exists():
            return

        ahora_p = time.perf_counter()
        dt = min(0.12, ahora_p - self.t_previo)
        self.t_previo = ahora_p
        ahora = time.time()

        reloj = dt * (30.0 if CFG["acelerar"] else 1.0)

        # distancia entre las dos (la usan para decidir)
        d = math.hypot(self.m1.x - self.m2.x, self.m1.y - self.m2.y)
        self.m1.dist_pareja = d
        self.m2.dist_pareja = d

        for m in self.mascotas:
            m.frame += 1
            m.vida_seg += reloj
            m._revisar_crecimiento()
            m.actualizar_necesidades(dt)
            if not m.arrastrando:
                m.ejecutar(dt)
            m.fisica(dt)
            m.root.geometry(f"+{int(m.x)}+{int(m.y)}")
            if m._globo_hasta:
                if ahora > m._globo_hasta:
                    m.globo.withdraw()
                    m._globo_hasta = 0.0
                else:
                    m._reposicionar_globo()
            m.render()

        # --- vinculo entre las dos
        if ahora - self.t_chequeo_par > 1.0:
            self.t_chequeo_par = ahora
            limite = max(PARAMS[self.m1.etapa]["alcance"], PARAMS[self.m2.etapa]["alcance"])
            if d > limite * 1.4:
                if not self.separadas:
                    self.separadas = True
                    for m in self.mascotas:
                        m.recordar("separacion", f"me separaron de {m.pareja.nombre}")
                        # No se les ordena buscarse: se les corta la accion para
                        # que decidan de nuevo. Si ya aprendieron, iran solas.
                        m.accion_hasta = time.time()
            elif self.separadas and d < limite * 0.5:
                self.separadas = False
                for m in self.mascotas:
                    m.carino = limitar(m.carino + 20, 0, 100)
                    m.modo = "feliz"
                    m.hablar("¡juntas otra vez!" if m.etapa != "bebe" else "¡iiih!")
            elif d < 150 and not self.separadas:
                # Se cuidan solas: si a una le falta carino, la otra se acerca.
                for m in self.mascotas:
                    if m.carino < 55 and m.etapa in ("adolescente", "adulto") \
                            and m.accion not in ("beso", "dormir", "comer"):
                        m.forzar("beso", 6)

        if ahora - self.t_habitos > 180:
            self.t_habitos = ahora
            self.refrescar_habitos()

        if ahora - self.t_guardado > 30:
            self.t_guardado = ahora
            self.guardar()

        self.m1.root.after(FPS_MS, self.tick)

    def correr(self):
        try:
            self.m1.root.mainloop()
        finally:
            self.guardar()


if __name__ == "__main__":
    Mundo().correr()
