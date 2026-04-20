from dataclasses import dataclass


@dataclass(frozen=True)
class MenuItem:
    dish: str
    description: str
    price: str
    category: str | None = None

    def to_json_dict(self) -> dict[str, str]:
        result = {
            "prato": self.dish,
            "descricao": self.description,
            "preco": self.price,
        }
        if self.category is not None:
            result["categoria"] = self.category
        return result
