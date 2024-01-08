import json

from urllib.parse import urlencode

from flask import Response, request


def _create_link(path, limit, offset, order_by, order_how, args_dict):
    # copy of the dict passed in so we don't modify the original
    params = dict(args_dict)
    params["limit"] = limit
    params["offset"] = offset
    params["order_by"] = order_by
    params["order_how"] = order_how
    return "{}?{}".format(path, urlencode(params))


def _create_first_link(path, limit, offset, count, order_by, order_how, args_dict):
    # Example return string:
    # "/api/item-service/v1/items?limit=20&offset=0&order_by=captured_date&order_how=desc"
    return _create_link(path, limit, 0, order_by, order_how, args_dict)


def _create_previous_link(path, limit, offset, count, order_by, order_how, args_dict):
    # if we are at the beginning, do not create a previous link
    # Example return string:
    # "/api/item-service/v1/items?limit=20&offset=20&order_by=captured_date&order_how=desc"
    if offset == 0 or offset - limit < 0:
        return _create_first_link(path, limit, offset, count, order_by, order_how, args_dict)
    return _create_link(path, limit, offset - limit, order_by, order_how, args_dict)


def _create_next_link(path, limit, offset, count, order_by, order_how, args_dict):
    # if we are at the end, do not create a next link
    # Example return string:
    # "/api/item-service/v1/items?limit=20&offset=40&order_by=captured_date&order_how=desc"
    if limit + offset >= count:
        return _create_last_link(path, limit, offset, count, order_by, order_how, args_dict)
    return _create_link(path, limit, limit + offset, order_by, order_how, args_dict)


def _create_last_link(path, limit, offset, count, order_by, order_how, args_dict):
    # Example return string:
    # "/api/item-service/v1/items?limit=20&offset=100&order_by=captured_date&order_how=desc"
    final_offset = count - limit if (count - limit) >= 0 else 0
    return _create_link(path, limit, final_offset, order_by, order_how, args_dict)


def build_paginated_baseline_list_response(
    limit, offset, order_by, order_how, json_list, total_available, count, args_dict={}
):
    json_output = {
        "meta": {
            "count": count,
            "limit": limit,
            "offset": offset,
            "total_available": total_available,
        },
        "links": {
            "first": _create_first_link(
                request.path, limit, offset, count, order_by, order_how, args_dict
            ),
            "next": _create_next_link(
                request.path, limit, offset, count, order_by, order_how, args_dict
            ),
            "previous": _create_previous_link(
                request.path, limit, offset, count, order_by, order_how, args_dict
            ),
            "last": _create_last_link(
                request.path, limit, offset, count, order_by, order_how, args_dict
            ),
        },
        "data": json_list,
    }

    return _build_json_response(json_output)


def _build_json_response(json_data, status=200):
    return Response(json.dumps(json_data), status=status, mimetype="application/json")
