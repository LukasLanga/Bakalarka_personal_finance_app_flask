import reflex as rx
from dotenv import load_dotenv
import os


dotenv_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(dotenv_path=dotenv_path)

config = rx.Config(
    app_name="frontendApp",
    disable_plugins=['reflex.plugins.sitemap.SitemapPlugin'],
    api_url="http://localhost:80",
)