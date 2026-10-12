import matplotlib.pyplot as plt
import numpy as np

class AstrologyWheelGenerator:
    def __init__(self):
        self.ZODIAC_SIGNS = [
            "Aries", "Tauro", "Géminis", "Cáncer", "Leo", "Virgo",
            "Libra", "Escorpio", "Sagitario", "Capricornio", "Acuario", "Piscis"
        ]
        self.COLORS = [
            "#FF4136", "#FFDC00", "#FF851B", "#2ECC40", "#FF4136", "#FFDC00",
            "#0074D9", "#85144b", "#FF851B", "#3D9970", "#0074D9", "#B10DC9"
        ]

    def generate_wheel(self, planets: dict, houses: dict, title: str, output_path: str):
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={'projection': 'polar'})
        
        # Ocultar grilla por defecto
        ax.axis('off')

        # Dibujar los 12 signos del zodiaco
        theta = np.linspace(0, 2*np.pi, 100)
        for i in range(12):
            angle_start = np.radians(i * 30)
            angle_end = np.radians((i + 1) * 30)
            
            # Anillo exterior
            ax.fill_between(
                np.linspace(angle_start, angle_end, 10), 
                0.8, 1.0, 
                color=self.COLORS[i], alpha=0.3, edgecolor='white', linewidth=2
            )
            
            # Etiqueta del signo
            mid_angle = angle_start + np.radians(15)
            ax.text(mid_angle, 0.9, self.ZODIAC_SIGNS[i], 
                    ha='center', va='center', rotation=np.degrees(mid_angle)-90,
                    fontsize=12, fontweight='bold', color='white')

        # Fondo interior oscuro para estilo "Premium"
        ax.fill_between(theta, 0, 0.8, color='#111111')

        # Dibujar planetas
        for p_name, deg in planets.items():
            rad = np.radians(deg)
            # Agregar un pequeño scatter en la posición
            ax.scatter(rad, 0.65, color='white', s=50, zorder=3)
            ax.text(rad, 0.72, p_name, color='gold', fontsize=10, 
                    ha='center', va='center', rotation=np.degrees(rad)-90, zorder=4)

        # Dibujar casas (líneas que cruzan desde el centro)
        for i, cusp in enumerate(houses['Casas']):
            rad = np.radians(cusp)
            ax.plot([rad, rad], [0, 0.8], color='gray', linestyle='--', linewidth=1)
            ax.text(rad, 0.5, f"Casa {i+1}", color='lightgray', fontsize=8, alpha=0.7,
                    ha='center', va='center', rotation=np.degrees(rad)-90)

        # Configuración final
        plt.title(f"Carta Astral: {title}", color='white', fontsize=16, y=1.05)
        fig.patch.set_facecolor('#000000')  # Fondo negro total

        # Guardar la figura
        plt.savefig(output_path, format='png', facecolor=fig.get_facecolor(), bbox_inches='tight', dpi=150)
        plt.close()
        return output_path

if __name__ == "__main__":
    # Test
    gen = AstrologyWheelGenerator()
    test_planets = {"Sol": 15, "Luna": 45, "Marte": 120}
    test_houses = {"Casas": [0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330]}
    gen.generate_wheel(test_planets, test_houses, "Test", "/home/LAB/astrology_factory/test_wheel.png")
