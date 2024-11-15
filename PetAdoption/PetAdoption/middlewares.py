import time
from http.client import responses

from django.utils.deprecation import MiddlewareMixin

# Middleware with function
# def measure_time_execution(get_response):
#     def middleware(request, *args, **kwargs):
#         start_time = time.time()
#         response = get_response(request, *args, **kwargs)
#         end_time = time.time()
#         execution_time = end_time - start_time
#         print(f"Execution time function: {execution_time} seconds")
#
#         return response
#
#     return middleware


# Middleware with class
# class MeasureTimeMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response
#
#     def __call__(self, request, *args, **kwargs):
#         start_time = time.time()
#         response = self.get_response(request, *args, **kwargs)
#         end_time = time.time()
#         execution_time = end_time - start_time
#         print(f"Execution time class: {execution_time} seconds")
#         return response

class MeasureTimeMiddleware(MiddlewareMixin):
    def process_request(self, request, *args, **kwargs):
        self.start_time = time.time()

    def process_view(self, request, view_func, view_args, view_kwargs):
        print("Processing view")

    def process_template_response(self, request, response):
        print("Template response processed")
        return response

    def process_exception(self, request, exception):
        print("Processing exception")
        return exception

    def process_response(self, request, response):
        end_time = time.time()
        execution_time = end_time - self.start_time
        print(f"Execution time class: {execution_time} seconds")
        return response

