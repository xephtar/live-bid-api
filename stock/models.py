from datetime import datetime
from django.forms import ModelForm
from django_neomodel import DjangoNode
from neomodel import StringProperty, UniqueIdProperty, FloatProperty, RelationshipTo, BooleanProperty, StructuredRel, \
    DateProperty


class ItemCategoryRelationship(StructuredRel):
    created_at = DateProperty(default=datetime.now)


class ItemBidRelationship(StructuredRel):
    pass


class Bid(DjangoNode):
    uid = UniqueIdProperty()
    amount = FloatProperty()
    created_at = DateProperty(default=datetime.now)
    user_email = StringProperty()

    class Meta:
        app_label = 'stock'

    def to_json(self):
        return {
            "uid": self.uid,
            "amount": self.amount,
            "created_at": self.created_at,
            "user_email": self.user_email,
            "id": self.id,
        }


class BidForm(ModelForm):
    class Meta:
        model = Bid
        fields = '__all__'


class Category(DjangoNode):
    uid = UniqueIdProperty()
    name = StringProperty(unique_index=True)

    class Meta:
        app_label = 'stock'

    def to_json(self, items=None):
        if items is not None:
            return {
                "uid": self.uid,
                "name": self.name,
                "id": self.id,
                "items": items
            }

        return {
            "uid": self.uid,
            "name": self.name,
            "id": self.id,
        }


class CategoryForm(ModelForm):
    class Meta:
        model = Category
        fields = '__all__'


class Item(DjangoNode):
    uid = UniqueIdProperty()
    name = StringProperty(index=True)
    price = FloatProperty()
    is_active = BooleanProperty(default=True)
    belong_to = RelationshipTo('Category', 'BELONG_TO', model=ItemCategoryRelationship)
    has_bid = RelationshipTo('Bid', 'HAS_BID', model=ItemBidRelationship)

    class Meta:
        app_label = 'stock'

    def to_json(self, belongings=None, bids=None):
        data = {
            "id": self.id,
            "uid": self.uid,
            "name": self.name,
            "price": self.price,
            "is_active": self.is_active,
        }
        if belongings is not None:
            data["belong_to"] = belongings

        if bids is not None:
            data["has_bid"] = bids

        return data


class ItemForm(ModelForm):
    class Meta:
        model = Item
        fields = '__all__'
