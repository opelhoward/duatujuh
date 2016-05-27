from models import db
from models.basemodel import BaseModel


class Product(BaseModel):
    __tablename__ = "products"

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    company = db.Column(db.String(50), nullable=True)
    category = db.Column(db.String(50), nullable=True)
    subcategory = db.Column(db.String(50), nullable=True)
    product_name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=True)
    image_link = db.Column(db.String(255), nullable=True)
    product_url = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=True)
    name = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(50), nullable=True)
    phone_number = db.Column(db.String(50), nullable=True)

    def __init__(self, id, company, category, subcategory, product_name, price, image_link, product_url, description):
        self.id = id
        self.company = company
        self.category = category
        self.subcategory = subcategory
        self.product_name = product_name
        self.price = price
        self.image_link = image_link
        self.product_url = product_url
        self.description = description

    def set_owner(self, name, email, phone_number):
        self.name = name
        self.email = email
        self.phone_number = phone_number
