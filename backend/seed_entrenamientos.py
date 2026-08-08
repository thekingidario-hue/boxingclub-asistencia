from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.models import Entrenamiento

ENTRENAMIENTOS = [
    {
        "nombre": "Fundamentos del boxeo",
        "categoria": "tecnica",
        "nivel": "principiante",
        "video_url": "https://www.youtube.com/watch?v=kKDHdsVN0b8",
        "thumbnail": None,
        "duracion": None,
        "objetivo": "Aprender los fundamentos básicos del boxeo, incluyendo postura, movimiento, jab, cross y combinaciones iniciales.",
        "equipamiento": "Ninguno",
        "ejercicios": "1. Posición de boxeo\n2. Guardia\n3. Desplazamiento hacia adelante\n4. Desplazamiento hacia atrás\n5. Desplazamiento lateral\n6. Jab\n7. Cross\n8. Combinación básica",
        "dia_sugerido": "lunes",
    },
    {
        "nombre": "Boxeo 101 — Fundamentos completos",
        "categoria": "tecnica",
        "nivel": "principiante",
        "video_url": "https://www.youtube.com/watch?v=D8DouKeOkfI",
        "thumbnail": None,
        "duracion": None,
        "objetivo": "Realizar una introducción completa al boxeo trabajando postura, desplazamiento, golpes, combinaciones, defensa, pivotes y movimiento.",
        "equipamiento": "Ninguno",
        "ejercicios": "1. Stance\n2. Movimiento\n3. Golpes básicos\n4. Golpes al cuerpo\n5. Combinaciones\n6. Defensa\n7. Pivotes\n8. Movimiento de cabeza\n9. Respiración\n10. Fintas",
        "dia_sugerido": "lunes",
    },
    {
        "nombre": "Golpes básicos de boxeo",
        "categoria": "tecnica",
        "nivel": "principiante",
        "video_url": None,
        "thumbnail": None,
        "duracion": None,
        "objetivo": "Aprender la técnica de los golpes básicos antes de trabajar combinaciones avanzadas.",
        "equipamiento": "Ninguno",
        "ejercicios": "1. Jab\n2. Cross\n3. Hook\n4. Uppercut\n5. Golpes básicos adicionales explicados por el instructor",
        "dia_sugerido": "martes",
    },
    {
        "nombre": "Jab + Cross — Combinación 1-2",
        "categoria": "tecnica",
        "nivel": "principiante",
        "video_url": None,
        "thumbnail": None,
        "duracion": None,
        "objetivo": "Aprender la combinación básica 1-2 y corregir errores frecuentes.",
        "equipamiento": "Ninguno",
        "ejercicios": "1. Jab\n2. Cross\n3. Jab + Cross\n4. Regreso a guardia\n5. Repeticiones técnicas",
        "dia_sugerido": "martes",
    },
    {
        "nombre": "Primeras combinaciones de boxeo",
        "categoria": "tecnica",
        "nivel": "principiante",
        "video_url": "https://www.youtube.com/watch?v=9oN2RCx5peY",
        "thumbnail": None,
        "duracion": None,
        "objetivo": "Aprender las primeras combinaciones que debe dominar un boxeador principiante.",
        "equipamiento": "Ninguno",
        "ejercicios": "1. Combinación 1\n2. Combinación 2\n3. Combinación 3\n4. Repetición técnica",
        "dia_sugerido": "miercoles",
    },
    {
        "nombre": "Desplazamientos básicos de boxeo",
        "categoria": "pies",
        "nivel": "principiante",
        "video_url": None,
        "thumbnail": None,
        "duracion": None,
        "objetivo": "Mejorar coordinación, equilibrio y desplazamiento básico.",
        "equipamiento": "Cinta adhesiva o tiza opcional.",
        "ejercicios": "1. Paso adelante\n2. Paso atrás\n3. Paso lateral\n4. Paso + golpe\n5. Pivot\n6. Control de posición",
        "dia_sugerido": "miercoles",
    },
    {
        "nombre": "Movimiento y golpes para principiantes",
        "categoria": "pies",
        "nivel": "principiante",
        "video_url": None,
        "thumbnail": None,
        "duracion": None,
        "objetivo": "Aprender a coordinar desplazamiento y golpes.",
        "equipamiento": "Ninguno",
        "ejercicios": "1. Movimiento adelante\n2. Movimiento atrás\n3. Movimiento lateral\n4. Jab en movimiento\n5. Cross en movimiento\n6. Combinaciones con desplazamiento",
        "dia_sugerido": "jueves",
    },
    {
        "nombre": "Shadowboxing para principiantes",
        "categoria": "tecnica",
        "nivel": "principiante",
        "video_url": None,
        "thumbnail": None,
        "duracion": None,
        "objetivo": "Aprender a utilizar el shadowboxing para mejorar técnica, coordinación, movimiento y visualización.",
        "equipamiento": "Ninguno",
        "ejercicios": "1. Guardia\n2. Movimiento\n3. Jab\n4. Cross\n5. Combinaciones\n6. Defensa\n7. Visualización",
        "dia_sugerido": "jueves",
    },
    {
        "nombre": "Shadowboxing — entrenamiento de 30 minutos",
        "categoria": "acondicionamiento",
        "nivel": "principiante",
        "video_url": None,
        "thumbnail": None,
        "duracion": 30,
        "objetivo": "Realizar una sesión completa de shadowboxing y acondicionamiento.",
        "equipamiento": "Ninguno",
        "ejercicios": "1. Calentamiento\n2. Shadowboxing\n3. Ejercicios con peso corporal\n4. Shadowboxing\n5. Core\n6. Round final",
        "dia_sugerido": "viernes",
    },
    {
        "nombre": "Respiración y relajación en boxeo",
        "categoria": "tecnica",
        "nivel": "principiante",
        "video_url": None,
        "thumbnail": None,
        "duracion": None,
        "objetivo": "Aprender a respirar correctamente y mantenerse relajado durante el entrenamiento.",
        "equipamiento": "Ninguno",
        "ejercicios": "1. Respiración\n2. Relajación\n3. Respiración durante golpes\n4. Control de tensión",
        "dia_sugerido": "viernes",
    },
]

CATEGORIAS_MAP = {
    "tecnica": "tecnica",
    "pies": "pies",
    "desplazamiento": "pies",
    "acondicionamiento": "acondicionamiento",
    "fundamentos": "tecnica",
}


def seed_entrenamientos(db: Session):
    creados = 0
    existentes = 0
    sin_video = 0
    urls_verificadas = []

    for data in ENTRENAMIENTOS:
        nombre = data["nombre"].strip()
        existe = db.query(Entrenamiento).filter(Entrenamiento.nombre == nombre).first()
        if existe:
            existentes += 1
            continue

        categoria = CATEGORIAS_MAP.get(data["categoria"], data["categoria"])
        db_ent = Entrenamiento(
            nombre=nombre,
            categoria=categoria,
            dia_sugerido=data.get("dia_sugerido"),
            descripcion=data.get("objetivo"),
            video_url=data.get("video_url"),
            thumbnail=data.get("thumbnail"),
            duracion=data.get("duracion"),
            nivel=data.get("nivel"),
            objetivo=data.get("objetivo"),
            equipamiento=data.get("equipamiento"),
            ejercicios=data.get("ejercicios"),
        )
        db.add(db_ent)
        creados += 1
        if data.get("video_url"):
            urls_verificadas.append(data["video_url"])
        else:
            sin_video += 1

    db.commit()

    print(f"Seed completado:")
    print(f"- Creados: {creados}")
    print(f"- Ya existentes: {existentes}")
    print(f"- Sin video (URL no verificada): {sin_video}")
    print(f"- URLs verificadas cargadas: {len(urls_verificadas)}")
    for url in urls_verificadas:
        print(f"  * {url}")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_entrenamientos(db)
    finally:
        db.close()
