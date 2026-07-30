from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate
from app.repositories.base import BaseRepository

class ProductRepository(BaseRepository[Product, ProductCreate, ProductUpdate]):
    def __init__(self):
        super().__init__(Product)

product_repository = ProductRepository()
