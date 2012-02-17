# Tweepy
# Copyright 2009-2010 Joshua Roesslein
# See LICENSE for details.

import httplib
import urllib
import time
import re

from tweepy.error import TweepError
from tweepy.utils import convert_to_utf8_str
from tweepy import error

re_path_template = re.compile('{\w+}')

def set_api(cache_result, api):
    if isinstance(cache_result, list) or isinstance(cache_result, tuple):
        for result in cache_result:
            set_api(result, api)
    else:
        try:
            cache_result._api = api
        except:
            pass


def bind_api(**config):

    class APIMethod(object):

        path = config['path']
        payload_type = config.get('payload_type', None)
        payload_list = config.get('payload_list', False)
        allowed_param = config.get('allowed_param', [])
        method = config.get('method', 'GET')
        require_auth = config.get('require_auth', False)
        search_api = config.get('search_api', False)

        def __init__(self, api, args, kargs):
            # If authentication is required and no credentials
            # are provided, throw an error.
            if self.require_auth and not api.auth:
                raise TweepError('Authentication required!')

            self.api = api
            self.post_data = kargs.pop('post_data', None)
            self.retry_count = kargs.pop('retry_count', api.retry_count)
            self.retry_delay = kargs.pop('retry_delay', api.retry_delay)
            self.retry_errors = kargs.pop('retry_errors', api.retry_errors)
            self.headers = kargs.pop('headers', {})
            self.build_parameters(args, kargs)

            # Pick correct URL root to use
            if self.search_api:
                self.api_root = api.search_root
            else:
                self.api_root = api.api_root

            # Perform any path variable substitution
            self.build_path()

            if api.secure:
                self.scheme = 'https://'
            else:
                self.scheme = 'http://'

            if self.search_api:
                self.host = api.search_host
            else:
                self.host = api.host

            # Manually set Host header to fix an issue in python 2.5
            # or older where Host is set including the 443 port.
            # This causes Twitter to issue 301 redirect.
            # See Issue http://github.com/joshthecoder/tweepy/issues/#issue/12
            self.headers['Host'] = self.host

        def build_parameters(self, args, kargs):
            self.parameters = {}
            for idx, arg in enumerate(args):
                if arg is None:
                    continue

                try:
                    self.parameters[self.allowed_param[idx]] = convert_to_utf8_str(arg)
                except IndexError:
                    raise TweepError('Too many parameters supplied!')

            for k, arg in kargs.items():
                if arg is None:
                    continue
                if k in self.parameters:
                    raise TweepError('Multiple values for parameter %s supplied!' % k)

                self.parameters[k] = convert_to_utf8_str(arg)

        def build_path(self):
            for variable in re_path_template.findall(self.path):
                name = variable.strip('{}')

                if name == 'user' and 'user' not in self.parameters and self.api.auth:
                    # No 'user' parameter provided, fetch it from Auth instead.
                    value = self.api.auth.get_username()
                else:
                    try:
                        value = urllib.quote(self.parameters[name])
                    except KeyError:
                        raise TweepError('No parameter value found for path variable: %s' % name)
                    del self.parameters[name]

                self.path = self.path.replace(variable, value)

        def execute(self):
            # Build the request URL
            url = self.api_root + self.path
            nocache = False
            if self.parameters.has_key("nocache"):
                nocache = True
                self.parameters.pop("nocache")
            if len(self.parameters):
                url = '%s?%s' % (url, urllib.urlencode(self.parameters))
            
            # Query the cache if one is available
            # and this request uses a GET method.
            if not nocache and self.api.cache and self.method == 'GET':
                cache_result = self.api.cache.get(url)
                # if cache result found and not expired, return it
                if cache_result:
#                    # must restore api reference
#                    if isinstance(cache_result, list) or isinstance(cache_result, tuple):
#                        for result in cache_result:
#                            print result
#                            result._api = self.api
#                    else:
#                        print cache_result
#                        cache_result._api = self.api
                    set_api(cache_result, self.api)
                    return cache_result

            # Continue attempting request until successful
            # or maximum number of retries is reached.
            retries_performed = 0
            while retries_performed < self.retry_count + 1:
                # Open connection
                # FIXME: add timeout
                if self.api.secure:
                    conn = httplib.HTTPSConnection("127.0.0.1", 8118, timeout=60)
                    #conn = httplib.HTTPSConnection(self.host)
                else:
                    conn = httplib.HTTPConnection("127.0.0.1", 8118, timeout=60)
                    #conn = httplib.HTTPConnection(self.host)

                # Apply authentication
                if self.api.auth:
                    self.api.auth.apply_auth(
                            self.scheme + self.host + url,
                            self.method, self.headers, self.parameters
                    )

                # Execute request
                try:
            	    #print self.method,self.scheme + self.host + url, self.headers
                    conn.request(self.method, self.scheme + self.host + url, headers=self.headers, body=self.post_data)
                    #conn.request(self.method, url, headers=self.headers, body=self.post_data)
                    resp = conn.getresponse()
                    print "BIND REQUEST"
                except Exception, e:
                    raise TweepError('Failed to send request: %s' % e)

                # Exit request loop if non-retry error code
                if self.retry_errors:
                    if resp.status not in self.retry_errors: break
                else:
                    if resp.status == 200: break

                # Sleep before retrying request again
                time.sleep(self.retry_delay)
                retries_performed += 1

            # If an error was returned, throw an exception
            self.api.last_response = resp
            if resp.status != 200:
                try:
                    error_msg = self.api.parser.parse_error(resp.read())
                except Exception:
                    error_msg = "Twitter error response: status code = %s" % resp.status
                if "Not authorized" in error_msg:
                    self.api.cache.store(url, None)
                raise TweepError(error_msg, resp)

            # Parse the response payload
            result = self.api.parser.parse(self, resp.read())

            conn.close()

            # Store result into cache if one is available.
            if self.api.cache and self.method == 'GET':
                self.api.cache.store(url, result)

            return result


    def _call(api, *args, **kargs):

        method = APIMethod(api, args, kargs)
        return method.execute()


    # Set pagination mode
    if 'cursor' in APIMethod.allowed_param:
        _call.pagination_mode = 'cursor'
    elif 'page' in APIMethod.allowed_param:
        _call.pagination_mode = 'page'

    return _call

