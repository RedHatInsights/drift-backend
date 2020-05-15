from flask import request, Response
import json

pagination_link_template = "%s?limit=%s&offset=%s&order_by=%s&order_how=%s"


def _create_first_link(path, limit, offset, count, order_by, order_how):
    # Example return string:
    # "/api/item-service/v1/items?limit=20&offset=0&order_by=captured_date&order_how=desc"
    first_link = pagination_link_template % (path, limit, 0, order_by, order_how)
    return first_link


def _create_previous_link(path, limit, offset, count, order_by, order_how):
    # if we are at the beginning, do not create a previous link
    # Example return string:
    # "/api/item-service/v1/items?limit=20&offset=20&order_by=captured_date&order_how=desc"
    if offset == 0 or offset - limit < 0:
        return _create_first_link(path, limit, offset, count, order_by, order_how)
    previous_link = pagination_link_template % (
        request.path,
        limit,
        offset - limit,
        order_by,
        order_how,
    )
    return previous_link


def _create_next_link(path, limit, offset, count, order_by, order_how):
    # if we are at the end, do not create a next link
    # Example return string:
    # "/api/item-service/v1/items?limit=20&offset=40&order_by=captured_date&order_how=desc"
    if limit + offset >= count:
        return _create_last_link(path, limit, offset, count, order_by, order_how)
    next_link = pagination_link_template % (
        request.path,
        limit,
        limit + offset,
        order_by,
        order_how,
    )
    return next_link


def _create_last_link(path, limit, offset, count, order_by, order_how):
    # Example return string:
    # "/api/item-service/v1/items?limit=20&offset=100&order_by=captured_date&order_how=desc"
    final_offset = count - limit if (count - limit) >= 0 else 0
    last_link = pagination_link_template % (
        path,
        limit,
        final_offset,
        order_by,
        order_how,
    )
    return last_link


def build_paginated_baseline_list_response(
    limit, offset, order_by, order_how, json_list, total_available, count
):
    link_params = {
        "path": request.path,
        "limit": limit,
        "offset": offset,
        "order_by": order_by,
        "order_how": order_how,
        "count": count,
    }
    json_output = {
        "meta": {"count": count, "total_available": total_available},
        "links": {
            "first": _create_first_link(**link_params),
            "next": _create_next_link(**link_params),
            "previous": _create_previous_link(**link_params),
            "last": _create_last_link(**link_params),
        },
        "data": json_list,
    }

    return _build_json_response(json_output)


def _build_json_response(json_data, status=200):
    return Response(json.dumps(json_data), status=status, mimetype="application/json")
