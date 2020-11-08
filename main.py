import webview
import sys
import time

import autorune


class API:
    def close(self):
        print('Shutting down.')
        webview.windows[0].destroy()


api = API()
width, height = (640, 240)
window_options = dict(
    frameless=True, 
    easy_drag=True,
    width=width, 
    height=height,
    js_api=api,
    x=100,
    y=100,
)


if __name__ == '__main__':
    window = webview.create_window('AutoRune', 'assets/index.html', **window_options)
    webview.start(autorune.wait_for_champ, window, debug=True)