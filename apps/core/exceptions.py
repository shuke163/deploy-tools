#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@file: exceptions.py 
@time: 2020/01/06 14:50
@software:  Door
"""

from rest_framework.views import exception_handler

import logging

logger = logging.getLogger("door")


def core_exception_handler(exc, context):
    response = exception_handler(exc, context)
    handlers = {
        "Http404": _handle_not_found_error,
        "ValidationError": _handle_generic_error
    }
    exception_class = exc.__class__.__name__
    if exception_class == "Http404":
        return handlers["Http404"](exc, context, response)
    return handlers["ValidationError"](exc, context, response)


def _handle_generic_error(exc, context, response):
    response.data = {
        "errors": response.data
    }
    return response


def _handle_not_found_error(exc, context, response):
    view = context.get("view", None)
    if view and hasattr(view, "queryset") and view.queryset is not None:
        error_key = view.queryset.model._meta_verbose_name
        response.data = {
            "errors": {
                error_key: response.data["detail"]
            }
        }
    else:
        response = _handle_generic_error(exc, context, response)
    return response
