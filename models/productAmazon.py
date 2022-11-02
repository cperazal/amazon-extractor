
class ProductAmazon:

    def __init__(self, url="", name="", price="", stars="", ratings="", colors="", features="", details=""):
        self.url = url
        self.name = name
        self.price = price
        self.stars = stars
        self.ratings = ratings
        self.colors = colors
        self.features = features
        self.details = details

    def to_dict(self):
        return {
            "url": self.url,
            "name": self.name,
            "price": self.price,
            "stars": self.stars,
            "ratings": self.ratings,
            "colors": self.colors,
            "features": self.features,
            "details": self.details
        }