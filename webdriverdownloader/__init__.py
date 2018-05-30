try:
    from webdriverdownloader import GeckoDriverDownloader
except ImportError:
    from .webdriverdownloader import GeckoDriverDownloader

__all__ = ['GeckoDriverDownloader']
