def escape_html(text: str) -> str:
    """Экранирует специальные HTML-символы в строке."""
    return (text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
                .replace("'", "&apos;"))
