from app.integrations.web_base import get_catalog_item

DEFAULT_LINK = "https://abito.com.ar/reservar"


def describe_price(text: str) -> str:
    item = get_catalog_item("abito_muestra")
    if not item:
        return "Tenemos precios y catálogo en la web. Podés verlo allí o preguntarme por una visita."
    return f"El {item['name']} cuesta {item['price']} {item['currency']}. Podés reservar en la web: {DEFAULT_LINK}"


def catalog_link() -> str:
    return DEFAULT_LINK
