
class ProductAmazon:

    def __init__(self, url="", name="", price="", stars="", ratings="", colors="", features="", details="", note=""):
        self.url = url
        self.name = name
        self.price = price
        self.stars = stars
        self.ratings = ratings
        self.colors = colors
        self.features = features
        self.details = details
        self.note = note

    def to_dict(self):
        return {
            "url": self.url,
            "name": self.name,
            "price": self.price,
            "stars": self.stars,
            "ratings": self.ratings,
            "colors": self.colors,
            "features": self.features,
            "details": self.details,
            "note": self.note
        }