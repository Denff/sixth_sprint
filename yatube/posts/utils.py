from django.core.paginator import Paginator

NUMBER_OF_POSTS: int = 10


def get_paginator_context(request, items_list):
    paginator = Paginator(items_list, NUMBER_OF_POSTS)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
