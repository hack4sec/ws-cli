import threading

from libs.common import is_binary_content_type
from classes.Registry import Registry


class HttpThread(threading.Thread):
    def is_response_content_binary(self, resp):
        return resp is not None \
            and 'content-type' in resp.headers \
            and is_binary_content_type(resp.headers['content-type'])

    def get_headers_text(self, resp):
        response_headers_text = ''
        for header in resp.headers:
            response_headers_text += '{0}: {1}\r\n'.format(header, resp.headers[header])
        return response_headers_text

    def is_response_right(self, resp):
        if resp is None:
            return False

        if self.not_found_size != -1 and self.not_found_size == len(resp.content):
            return False

        if self.not_found_re and not self.is_response_content_binary(resp) and (
                    self.not_found_re.findall(resp.content) or
                    self.not_found_re.findall(self.get_headers_text(resp))):
            return False

        if str(resp.status_code) in self.not_found_codes:
            return False

        return True

    def log_item(self, item_str, resp, is_positive):
        Registry().get('logger').item(
            item_str,
            resp.content if not resp is None else "",
            self.is_response_content_binary(resp),
            positive=is_positive
        )

    def check_positive_limit_stop(self, result, rate=1):
        import requests
        requests.get('http://localhost/' + str(len(result)))
        requests.get('http://localhost/' + str(int(Registry().get('config')['main']['positive_limit_stop']) * rate))
        if len(result) >= (int(Registry().get('config')['main']['positive_limit_stop']) * rate):
            Registry().set('positive_limit_stop', True)

    def is_retest_need(self, word, resp):
        if resp is not None and len(self.retest_codes) and str(resp.status_code) in self.retest_codes:
            if word not in self.retested_words.keys():
                self.retested_words[word] = 0
            self.retested_words[word] += 1

            return self.retested_words[word] <= self.retest_limit
        return False