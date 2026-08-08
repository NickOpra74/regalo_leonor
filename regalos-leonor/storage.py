"""
storage.py — Capa de datos de las cartitas.

Funciona en dos modos automáticamente:

1. MongoDB Atlas  → si existe la variable de entorno MONGODB_URI (modo producción).
2. Archivo JSON   → si no existe la URI (modo local / respaldo).

Así la página nunca se cae aunque falte la base de datos.
"""

import json
import os
import uuid
from datetime import datetime, timezone
from threading import Lock

# ──────────────────────────────────────────────
#  CARTITAS QUE VIENEN POR DEFECTO (las originales)
# ──────────────────────────────────────────────
CARTAS_INICIALES = [
    {
        "emoji": "💙",
        "titulo": "Lo primero que sentí",
        "subtitulo": "El momento en que todo cambió para mí",
        "texto": (
            "Hubo un instante en que te miré y algo dentro de mí se acomodó en un lugar "
            "que no sabía que existía. No fue un rayo, fue algo más suave: como cuando una "
            "canción te llega sin que estés buscando nada y de pronto ya no puedes imaginar "
            "el silencio.\n\n"
            "Desde ese día empecé a notar cosas pequeñas tuyas que no debería notar, y me di "
            "cuenta de que ya era tarde para no quererte."
        ),
        "firma": "Con todo mi corazón 💙",
        "color": "azul",
    },
    {
        "emoji": "🌸",
        "titulo": "Lo que más amo de ti",
        "subtitulo": "Todo lo que me enamora cada día",
        "texto": (
            "Amo cómo te ríes sin reservas. Amo que te importan las cosas de verdad. Amo la "
            "forma en que ves el mundo, con esa mezcla de ternura, belleza y fuerza de voluntad "
            "que pocas personas tienen.\n\n"
            "Amo que existas, que estés aquí, que seas tan tú. Y amo que por alguna razón "
            "hermosa, decidiste quedarte cerca de mí."
        ),
        "firma": "Siempre tuyo 🌸",
        "color": "rosa",
    },
    {
        "emoji": "🌙",
        "titulo": "Lo que sueño contigo",
        "subtitulo": "El futuro que imagino a tu lado",
        "texto": (
            "Sueño con más tardes juntos, con más risas tontas, con seguir conociéndote en cada "
            "nueva versión que vayas siendo.\n\n"
            "Sueño con que cuando lleguen días difíciles, podamos apoyarnos. Y sueño, sobre todo, "
            "con que sigas eligiéndome así como yo te elijo a ti, cada mañana, sin dudarlo."
        ),
        "firma": "Contigo siempre 🌙",
        "color": "morado",
    },
    {
        "emoji": "✨",
        "titulo": "Gracias por existir",
        "subtitulo": "Todo lo que me has dado sin darte cuenta",
        "texto": (
            "Gracias por hacer que los días normales se sientan especiales. Por las conversaciones "
            "largas, por las veces que me sacas de quisio y no lo digo de mala manera es bonito la "
            "verdad, por la calidez que traes sin ni siquiera intentarlo.\n\n"
            "Gracias por ser la persona que eres. Este regalo lo hice con todo mi amor para decirte "
            "que te quiero más de lo que sé expresar y te prometo que te hare la mujer mas feliz del "
            "mundo."
        ),
        "firma": "Te amo, leonor mi querida mujer y futura esposa✨",
        "color": "rosa",
    },
]

COLORES_VALIDOS = {"azul", "rosa", "morado", "verde", "durazno"}

MAX_LEN = {
    "emoji": 16,
    "titulo": 80,
    "subtitulo": 140,
    "texto": 6000,
    "firma": 120,
}


# ──────────────────────────────────────────────
#  LIMPIEZA / VALIDACIÓN
# ──────────────────────────────────────────────
def limpiar_carta(data, parcial=False):
    """Valida y normaliza lo que llega del formulario.

    Devuelve (carta_limpia, error). Si error no es None, no guardes nada.
    """
    if not isinstance(data, dict):
        return None, "Datos inválidos."

    carta = {}

    def campo(nombre, obligatorio):
        valor = data.get(nombre)
        if valor is None:
            if obligatorio and not parcial:
                return None, f"Falta el campo «{nombre}»."
            return "__SKIP__", None
        valor = str(valor).strip()
        if obligatorio and not valor:
            return None, f"El campo «{nombre}» no puede estar vacío."
        if len(valor) > MAX_LEN[nombre]:
            return None, f"El campo «{nombre}» es demasiado largo (máx. {MAX_LEN[nombre]})."
        return valor, None

    for nombre, obligatorio in (
        ("emoji", True),
        ("titulo", True),
        ("subtitulo", False),
        ("texto", True),
        ("firma", False),
    ):
        valor, error = campo(nombre, obligatorio)
        if error:
            return None, error
        if valor != "__SKIP__":
            carta[nombre] = valor

    color = data.get("color")
    if color is not None:
        color = str(color).strip().lower()
        if color not in COLORES_VALIDOS:
            color = "azul"
        carta["color"] = color
    elif not parcial:
        carta["color"] = "azul"

    if not carta:
        return None, "No enviaste ningún cambio."

    return carta, None


def _ahora():
    return datetime.now(timezone.utc).isoformat()


# ──────────────────────────────────────────────
#  BACKEND MONGODB
# ──────────────────────────────────────────────
class MongoStore:
    modo = "mongodb"

    def __init__(self, uri, db_name="regalo_leonor"):
        from pymongo import MongoClient, ASCENDING

        self.client = MongoClient(uri, serverSelectionTimeoutMS=8000, tz_aware=True)
        self.client.admin.command("ping")  # falla rápido si la URI está mal
        self.col = self.client[db_name]["cartas"]
        self.col.create_index([("orden", ASCENDING)])
        self._sembrar()

    def _sembrar(self):
        if self.col.count_documents({}, limit=1) == 0:
            docs = []
            for i, c in enumerate(CARTAS_INICIALES):
                doc = dict(c)
                doc.update({"_id": uuid.uuid4().hex, "orden": i, "creada": _ahora()})
                docs.append(doc)
            self.col.insert_many(docs)

    @staticmethod
    def _salida(doc):
        doc = dict(doc)
        doc["id"] = doc.pop("_id")
        return doc

    def listar(self):
        return [self._salida(d) for d in self.col.find().sort([("orden", 1), ("creada", 1)])]

    def crear(self, carta):
        ultimo = self.col.find_one(sort=[("orden", -1)])
        carta = dict(carta)
        carta.update(
            {
                "_id": uuid.uuid4().hex,
                "orden": (ultimo.get("orden", 0) + 1) if ultimo else 0,
                "creada": _ahora(),
            }
        )
        self.col.insert_one(carta)
        return self._salida(carta)

    def actualizar(self, carta_id, cambios):
        cambios = dict(cambios)
        cambios["editada"] = _ahora()
        doc = self.col.find_one_and_update(
            {"_id": carta_id},
            {"$set": cambios},
            return_document=True,
        )
        return self._salida(doc) if doc else None

    def borrar(self, carta_id):
        return self.col.delete_one({"_id": carta_id}).deleted_count > 0


# ──────────────────────────────────────────────
#  BACKEND JSON (local / respaldo)
# ──────────────────────────────────────────────
class JsonStore:
    modo = "json"

    def __init__(self, ruta):
        self.ruta = ruta
        self.lock = Lock()
        os.makedirs(os.path.dirname(ruta) or ".", exist_ok=True)
        if not os.path.exists(ruta):
            inicial = []
            for i, c in enumerate(CARTAS_INICIALES):
                doc = dict(c)
                doc.update({"id": uuid.uuid4().hex, "orden": i, "creada": _ahora()})
                inicial.append(doc)
            self._escribir(inicial)

    def _leer(self):
        try:
            with open(self.ruta, "r", encoding="utf-8") as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError):
            return []

    def _escribir(self, datos):
        tmp = self.ruta + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)
        os.replace(tmp, self.ruta)

    def listar(self):
        return sorted(self._leer(), key=lambda c: (c.get("orden", 0), c.get("creada", "")))

    def crear(self, carta):
        with self.lock:
            datos = self._leer()
            orden = max((c.get("orden", 0) for c in datos), default=-1) + 1
            carta = dict(carta)
            carta.update({"id": uuid.uuid4().hex, "orden": orden, "creada": _ahora()})
            datos.append(carta)
            self._escribir(datos)
            return carta

    def actualizar(self, carta_id, cambios):
        with self.lock:
            datos = self._leer()
            for c in datos:
                if c.get("id") == carta_id:
                    c.update(cambios)
                    c["editada"] = _ahora()
                    self._escribir(datos)
                    return c
            return None

    def borrar(self, carta_id):
        with self.lock:
            datos = self._leer()
            quedan = [c for c in datos if c.get("id") != carta_id]
            if len(quedan) == len(datos):
                return False
            self._escribir(quedan)
            return True


# ──────────────────────────────────────────────
#  FÁBRICA
# ──────────────────────────────────────────────
def crear_store(uri=None, ruta_json=None):
    """Devuelve (store, aviso). aviso != None cuando hubo que usar el respaldo."""
    uri = uri if uri is not None else os.environ.get("MONGODB_URI", "").strip()
    ruta_json = ruta_json or os.path.join(os.path.dirname(__file__), "data", "cartas.json")

    if uri:
        try:
            return MongoStore(uri), None
        except Exception as e:  # noqa: BLE001
            return JsonStore(ruta_json), f"No se pudo conectar a MongoDB ({e}). Usando archivo JSON."

    return JsonStore(ruta_json), "MONGODB_URI no configurada. Usando archivo JSON local."
