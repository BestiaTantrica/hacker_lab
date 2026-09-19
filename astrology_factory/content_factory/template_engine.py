import sqlite3
import os
import random

db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'astrology_meanings.sqlite')

class TemplateEngine:
    def __init__(self):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

    def get_planet_info(self, planet_name):
        self.cursor.execute("SELECT keywords, empathic_description FROM planets WHERE name = ?", (planet_name,))
        res = self.cursor.fetchone()
        return res if res else (planet_name, "nuestra energía vital")

    def get_sign_info(self, sign_name):
        self.cursor.execute("SELECT element, quality, keywords FROM signs WHERE name = ?", (sign_name,))
        res = self.cursor.fetchone()
        return res if res else ("Desconocido", "Desconocido", sign_name)

    def generate_transit_text(self, planet_name, sign_name):
        """
        Busca una plantilla específica en la BD o usa un fallback armando la oración
        con los diccionarios base de signos y planetas.
        """
        self.cursor.execute("SELECT template_text FROM transit_templates WHERE planet_name = ? AND sign_name = ?", (planet_name, sign_name))
        res = self.cursor.fetchall()
        
        if res:
            return random.choice(res)[0]
        else:
            # Fallback empático si no hay plantilla redactada a mano
            p_keys, p_desc = self.get_planet_info(planet_name)
            s_elem, s_qual, s_keys = self.get_sign_info(sign_name)
            
            return f"Actualmente {planet_name} se encuentra en la energía de {sign_name}. Este es un período ideal para enfocarnos en {p_desc}. Su cualidad de {s_elem} nos invita a integrar {s_keys} en nuestra rutina diaria, dándonos una oportunidad hermosa para crecer."

    def generate_aspect_text(self, p1, p2, aspect_name):
        """
        Busca cómo interpretar la relación (aspecto) entre dos planetas.
        """
        self.cursor.execute("SELECT template_text FROM transit_templates WHERE aspect_name = ?", (aspect_name,))
        res = self.cursor.fetchall()
        if res:
            text = random.choice(res)[0]
            # Reemplazar placeholders si los hubiera
            return text.replace('{p1}', p1).replace('{p2}', p2)
        else:
            return f"El aspecto de {aspect_name} entre {p1} y {p2} marca un intercambio de energías interesante que puede movilizarnos internamente hoy."

    def __del__(self):
        self.conn.close()
