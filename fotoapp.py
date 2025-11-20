from PIL import Image, ImageFilter, ImageOps
import requests
from io import BytesIO
import matplotlib.pyplot as plt

# Dimensiones por plataforma.
PLATFORM_SIZES = {
    "youtube": (1280, 720),
    "instagram": (1080, 1080),
    "twitter": (1200, 675),
    "facebook": (1200, 630)
}

# Carga una imagen desde archivo o URL.
def load_image(url):
    if url.lower().startswith(("http://", "https://")):
      response = requests.get(url)
      response.raise_for_status()
      return Image.open(BytesIO(response.content)).convert("RGB")
    else:
      return Image.open(url).convert("RGB")

# Redimensiona una imagen al tamaño recomendado por plataforma.
def resize(url, platform):
    """
    - Se ajusta la foto al tamaño adecuado mateniendo la proporción, centrando la imagen y rellenando el fondo si es necesario
    - Permite mostrar fotos adaptadas para cada plataforma.
    """

    image = load_image(url)
    platform = platform.lower()

    if platform not in PLATFORM_SIZES:
      raise ValueError("Plataforma no valida.")

    target_width, target_height = PLATFORM_SIZES[platform]

    width, height = image.size

    scale = min(target_width / width, target_height / height)
    new_width = int(width * scale)
    new_height = int(height * scale)

    resized = image.resize((new_width, new_height), Image.LANCZOS)
    final_image = Image.new("RGB", (target_width, target_height), (255, 255, 255))

    offset = ((target_width - new_width) // 2, (target_height - new_height) // 2)
    final_image.paste(resized, offset)

    return final_image

def equalize(image):
    """
    Lee una imagen y aplica ecualizacion de histograma para mejorar el contraste
    Distribuye mejor los niveles de intensidad.
    Ayuda a recuperar detalles en imagenes muy oscuras o muy claras.
    """

    img = Image.open(image).convert("RGB")
    equalize_image = ImageOps.equalize(img)
    return img, equalize_image

def compare(original, equalized, output_name):
    """
    Muestra la imagen original y la ecualizada en una misma figura
    y guarda el resultado.
    """

    plt.figure(figsize=(10,5))

    plt.subplot(1,2,1)
    plt.title("Original")
    plt.imshow(original)
    plt.axis("off")

    plt.subplot(1,2,2)
    plt.title("Ecualizada")
    plt.imshow(equalized)
    plt.axis("off")

    plt.tight_layout()
    plt.savefig(output_name, dpi=300)
    plt.show()

FILTERS = {
    "BLUR": ImageFilter.BLUR,
    "CONTOUR": ImageFilter.CONTOUR,
    "DETAIL": ImageFilter.DETAIL,
    "EDGE_ENHANCE": ImageFilter.EDGE_ENHANCE,
    "EDGE_ENHANCE_MORE": ImageFilter.EDGE_ENHANCE_MORE,
    "EMBOSS": ImageFilter.EMBOSS,
    "FIND_EDGES": ImageFilter.FIND_EDGES,
    "SHARPEN": ImageFilter.SHARPEN,
    "SMOOTH": ImageFilter.SMOOTH,
}

def apply_filter(image, filter_name):
    # Se aplica uno de los 9 filtros disponibles en Pillow a una imagen.
    filter_name = filter_name.upper()
    if filter_name not in FILTERS:
      raise ValueError("Filtro invalido")

    img = Image.open(image)
    img_filter = img.filter(FILTERS[filter_name])

    save_name = f"result_{filter_name}.jpg"
    img_filter.save(save_name)

    plt.figure(figsize=(8, 4))

    plt.subplot(1, 2, 1)
    plt.imshow(img)
    plt.title("Original")
    plt.axis("off")

    plt.subplot(1, 2, 2)
    plt.imshow(img_filter)
    plt.title(f"Filtro: {filter_name}", color="red")
    plt.axis("off")

    plt.show()

    return img_filter

def see_filters(image):
    # Genera un mosaico con la imagen original mas las 9 variaciones filtradas.
    img = Image.open(image)

    plt.figure(figsize=(14, 6))

    plt.subplot(2, 5, 1)
    plt.imshow(img)
    plt.title("Original")
    plt.axis("off")

    i = 2
    for name, filter in FILTERS.items():
      img_f = img.filter(filter)
      plt.subplot(2, 5, i)
      plt.imshow(img_f)
      plt.title(name)
      plt.axis("off")
      i += 1

    plt.tight_layout()
    plt.savefig("mosaico_9_filters.jpg")

    plt.show()

def sketch_person(image, output="boceto.png", persona=True):
    """
    Genera un boceto en base a una foto de una persona.
    Solo funciona si persona=True
    """

    if not persona:
      raise ValueError("No se detecto una persona en la imagen.")
    
    img = Image.open(image).convert("L")

    blurred = img.filter(ImageFilter.GaussianBlur(5))
    inverted = ImageOps.invert(blurred)
    sketch = Image.blend(img, inverted, alpha=0.7)
    sketch = sketch.filter(ImageFilter.FIND_EDGES)

    sketch.save(output)
    return sketch

# Variables globales
current_image = None
current_url = None

def main():
    global current_image, current_url

    while True:
      print("\n=== MENU ===")
      print("""
        [1] - Cargar imagen
        [2] - Redimensionar imagen
        [3] - Ecualizar contraste
        [4] - Aplicar filtro Pillow
        [5] - Generar boceto para pintores
        [0] - Salir

      """)

      option = input("Ingrese una opcion: ")

      try:
        if option == "1":
          current_url = input("Ingrese URL o ruta de la imagen: ")
          
          try:
            current_image = Image.open(current_url)
            print("[+] Imagen cargada correctamente [+]")
          except Exception as e:
            print(f"[x] Error al cargar la imagen [x] > {e}")
            current_image = None

        elif option in ["2", "3", "4", "5"]:
          if current_image is None:
            raise ValueError("Debes de cargar la imagen primero.")
          
          if option == "2":
            platform = input("Plataforma (youtube / instagram / twitter / facebook): ")
            output = resize(current_url, platform)
            output.save("redimensionada.png")
            print("[+] La imagen acaba de ser redimensionada y guardada como redimensionada.png [+]")
          
          elif option == "3":
            original, eq = equalize(current_url)
            compare(original, eq, "ecualizada.png")
            print("[+] Imagen ecualizada y guardada como ecualizada.png [+]")
          
          elif option == "4":
            filter = input("Ingresa el filtro (blur, contour, detail, sharpen...): ")
            output = apply_filter(current_url, filter)
            output.save(f"filter_{filter}.png")
            print(f"[+] Imagen filtrada guardada como filter_{filter}.png")
          
          elif option == "5":
            output = sketch_person(current_url, "boceto.png", persona=True)
            print("[+] Boceto generado como boceto.png [+]")
        
        elif option == "0":
          print("saliendo...")
          break
        else:
          print("Opcion invalida")
      except Exception as error:
        print(f"Error: {error}")