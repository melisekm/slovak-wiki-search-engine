from typing import Optional


class WikiPage:
    def __init__(self, title: str, text: str):
        self.title = title
        self.raw_text = text
        self.terms: Optional[list[str]] = None
        self.tfidf_vector: Optional[list[float]] = None

    def __str__(self):
        return f'WikiPage(title={self.title})'

    def __repr__(self):
        return str(self)


class WikiParser:
    def __init__(self):
        pass

    def parse(self, wikipedia_data_file) -> list[WikiPage]:
        pass
