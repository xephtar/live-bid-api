import json
from django.http import JsonResponse, HttpResponseNotAllowed
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from neomodel import db

from .consumers import send_item_created_message
from .models import Category, Item, Bid
from .utils import get_key_from_dict


class BaseView(View):
    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(BaseView, self).dispatch(*args, **kwargs)


class CategoryView(BaseView):
    def get(self, request):
        expand = request.GET.get('expand', "")
        categories = Category.nodes.all()

        if expand == "items":
            response = []
            for category in categories:
                results, cols = db.cypher_query(f"""MATCH (item)-[belong_to]-(category)
                                                    WHERE id(category)={category.id}
                                                    RETURN item, belong_to, category""")
                items = []

                for row in results:
                    item = Item.inflate(row[cols.index('item')])
                    items.append(item)

                item_json = category.to_json([item.to_json() for item in items])
                response.append(item_json)

            return JsonResponse(response, safe=False)

        return JsonResponse([category.to_json() for category in categories], safe=False)

    def post(self, request):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        category_name = get_key_from_dict(body, "name", False)
        if not category_name:
            return JsonResponse({"error": "there should be name in request body"}, safe=False)
        category = Category(name=category_name)
        category.save()
        return JsonResponse(category.to_json(), safe=False)


class ItemView(BaseView):
    def get(self, request):
        category_id = request.GET.get('category_id', "")
        response = []

        if category_id:
            items, _ = db.cypher_query(
                f"""MATCH (item)-[belong_to]-(category) WHERE id(category)={category_id} RETURN item""")
            response = [Item.inflate(row[0]).to_json() for row in items]
            return JsonResponse(response, safe=False)

        items = Item.nodes.all()

        for item in items:
            results, cols = db.cypher_query(f"""MATCH (item)-[belong_to]-(category)
                                                WHERE id(item)={item.id}
                                                RETURN item, belong_to, category""")
            categories = []

            for row in results:
                category = Category.inflate(row[cols.index('category')])
                categories.append(category)

            item_json = item.to_json(belongings=[category.to_json() for category in categories])
            response.append(item_json)

        return JsonResponse(response, safe=False)

    def post(self, request):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        item_name = get_key_from_dict(body, "name", False)
        item_price = get_key_from_dict(body, "price", False)
        item_category_uid = get_key_from_dict(body, "category_uid", False)
        if not item_name or not item_price or not item_category_uid:
            return JsonResponse({"error": "there should be name, price and category_uid fields in request body"},
                                safe=False)
        item = Item(name=item_name, price=item_price)
        item.save()
        category = Category.nodes.get(uid=item_category_uid)
        item.belong_to.connect(category)
        send_item_created_message(category.id, item)
        return JsonResponse(item.to_json(belongings=[category.to_json()]), safe=False)

    def put(self, request):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        item_uid = get_key_from_dict(body, "uid", False)
        if not item_uid:
            return JsonResponse({"error": "there should be uid field in request body"}, safe=False)
        item_name = get_key_from_dict(body, "name", False)
        item_price = get_key_from_dict(body, "price", False)
        item_category_uid = get_key_from_dict(body, "category_uid", False)
        item = Item.nodes.get(uid=item_uid)
        if item_price:
            item.price = item_price

        if item_name:
            item.name = item_name

        if item_category_uid:
            category = Category.nodes.get(uid=item_category_uid)
            item.belong_to.connect(category)
        item.save()

        results, cols = db.cypher_query(f"""MATCH (item)-[belong_to]-(category)
                                                        WHERE id(item)={item.id}
                                                        RETURN item, belong_to, category""")
        categories = []

        for row in results:
            category = Category.inflate(row[cols.index('category')])
            categories.append(category.to_json())

        return JsonResponse(item.to_json(belongings=categories), safe=False)


@csrf_exempt
def create_bid_for_item(request, item_uid):
    if request.method != "POST":
        return HttpResponseNotAllowed(permitted_methods=('POST',))

    item = Item.nodes.get(uid=item_uid)
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    bid_amount = get_key_from_dict(body, "amount", False)
    user_email = get_key_from_dict(body, "user_email", False)
    if not bid_amount or not user_email:
        return JsonResponse({"error": "there should be amount and user_email fields in request body"}, safe=False)
    bid = Bid(amount=bid_amount, user_email=user_email)
    bid.save()
    item.has_bid.connect(bid)

    response = item.to_json(bids=[bid.to_json()])
    return JsonResponse(response, safe=False)


@csrf_exempt
def get_bids_for_item(request, item_uid):
    item = Item.nodes.get(uid=item_uid)

    results, cols = db.cypher_query(f"""MATCH (item)-[:HAS_BID]-(bid)
                                                        WHERE id(item)={item.id}
                                                        RETURN item, bid""")
    bids = []

    for row in results:
        bid = Bid.inflate(row[cols.index('bid')])
        bids.append(bid.to_json())

    response = item.to_json(bids=bids)
    return JsonResponse(response, safe=False)