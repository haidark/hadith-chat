"""Loader that loads json directory dump of hadith from sunnah.com.."""
import json
from pathlib import Path
from typing import Any, List, Optional, Tuple

from langchain.docstore.document import Document
from langchain.document_loaders.base import BaseLoader


class HadithJsonLoader(BaseLoader):
    """Loader that loads json directory dump of hadith from sunnah.com."""

    def __init__(
        self,
        path: str,
        encoding: Optional[str] = None,
        errors: Optional[str] = None,
        **kwargs: Optional[Any]
    ):
        """Initialize path."""
        self.file_path = path
        self.encoding = encoding
        self.errors = errors
        self.bs_kwargs = kwargs

    def load(self) -> List[Document]:
        """Load documents."""
        docs = []
        for p in Path(self.file_path).rglob("*"):
            if p.is_dir():
                continue

            with open(p, encoding=self.encoding, errors=self.errors) as f:
                print(p)
                book_data = json.load(f)
                link = book_data['book_link']
                book_name = book_data["english_name"]
                for hadith in book_data['hadith_data']:
                    text = hadith["english"].replace("\n", "")
                    reference = hadith['reference']
                    book_reference = hadith['book_reference']
                    hadith_number = hadith['hadith_number']
                    metadata = {"source": str(link), "reference": f"{reference} {book_reference} {book_name} {hadith_number}"}
                    docs.append(Document(page_content=text, metadata=metadata))
        return docs
