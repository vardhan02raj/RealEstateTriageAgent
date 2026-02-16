from flask import Blueprint, request
from utils.auth_middleware import token_required
from utils.role_required import role_required
from models.property_model import (
    create_property,
    get_property_by_id,
    search_properties,
    delete_property,
    update_property,
    city_market_stats,
    recommend_properties,
    city_overview,
    price_by_bedrooms,
    cheapest_segment
)

property_bp = Blueprint("property", __name__, url_prefix="/properties")


# CREATE
@property_bp.route("/", methods=["POST"])
@token_required
@role_required("seller", "admin")
def add_property():
    data = request.json
    data["created_by"] = request.user["email"]
    pid = create_property(data)
    return {"success": True, "id": pid}, 201


# READ
@property_bp.route("/<pid>", methods=["GET"])
def get_property(pid):
    prop = get_property_by_id(pid)
    if not prop:
        return {"error": "Not found"}, 404
    return prop


# SEARCH
@property_bp.route("/search", methods=["GET"])
def search():
    filters = request.args
    results = search_properties(filters)
    return {"results": results}


# DELETE
@property_bp.route("/<pid>", methods=["DELETE"])
@token_required
def delete(pid):
    prop = get_property_by_id(pid)

    if not prop:
        return {"error": "Not found"}, 404

    # Ownership check
    if prop.get("created_by") != request.user["email"]:
        return {"error": "Forbidden"}, 403

    delete_property(pid)
    return {"deleted": True}


@property_bp.route("/<pid>", methods=["PUT"])
@token_required
def update(pid):
    prop = get_property_by_id(pid)

    if not prop:
        return {"error": "Not found"}, 404

    # Ownership check
    if prop.get("created_by") != request.user["email"]:
        return {"error": "Forbidden"}, 403

    data = request.json
    modified = update_property(pid, data)

    if modified:
        return {"success": True}, 200

    return {"error": "Not found or unchanged"}, 404


@property_bp.route("/market/<city>", methods=["GET"])
def market(city):
    stats = city_market_stats(city)
    return {"market": stats}


@property_bp.route("/recommend", methods=["GET"])
def recommend():
    city = request.args.get("city")
    max_price = request.args.get("max_price")
    bedrooms = request.args.get("bedrooms")

    results = recommend_properties(city, max_price, bedrooms)

    return {"recommendations": results}


@property_bp.route("/overview", methods=["GET"])
def overview():
    stats = city_overview()
    return {"cities": stats}


@property_bp.route("/bedroom-stats", methods=["GET"])
def bedroom_stats():
    stats = price_by_bedrooms()
    return {"stats": stats}


@property_bp.route("/cheapest-segment/<city>", methods=["GET"])
def cheapest(city):
    data = cheapest_segment(city)
    return {"segment": data}
