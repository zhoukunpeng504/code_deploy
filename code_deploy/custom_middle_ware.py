# coding:utf-8
__author__ = "zkp"
# create by zkp on 2021/9/29
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
import config
import json


environ_config = config.ENVIRON_CONFIG
environ_config_json = json.dumps(environ_config, ensure_ascii=False)

class MyMiddleware(MiddlewareMixin):
    """
    """
    # def process_response(self, request, response):
    #     # Don't set it if it's already in the response
    #
    #
    #     response['P3P'] = 'policyref="/w3c/p3p.xml",
    #     CP="NOI DSP PSAa OUR BUS IND ONL UNI COM NAV INT LOC"'
    #     return response
    def process_request(self, request):
        request.environ_config = environ_config
        print(request, request.environ_config)
        request.environ_config_json = environ_config_json

