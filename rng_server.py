import shlex
import subprocess
from tornado.gen import coroutine, Task, Return
from tornado.process import Subprocess
import tornado.ioloop
import tornado.web
import tornado.websocket
 
from tornado.options import define, options, parse_command_line

define("port", default=8888, help="Run on the given port", type=int)
define("serial", default='/dev/tty.usbserial-FTH9JLQX', help="Run on the given serial port", type=str)
 
clients = dict()
 
 
class IndexHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self, **kwargs):
        self.render("index.html")
 
 
class RngWebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self, *args, **kwargs):
        self.id = kwargs["Id"]
        self.stream.set_nodelay(True)
        clients[self.id] = {"id": self.id, "object": self}
 
    def on_message(self, message):
        tornado.ioloop.IOLoop.instance().add_callback(rng_process, self, options.serial, message)
 
    def on_close(self):
        if self.id in clients:
            # print "close"
            del clients[self.id]
 
    def check_origin(self, origin):
        return True
 
app = tornado.web.Application([
    (r'/', IndexHandler),
    (r'/(?P<Id>\w*)', RngWebSocketHandler),
])

@coroutine
def call_subprocess(cmd, stdin_data=None, stdin_async=True):
    """call sub process async
 
        Args:
            cmd: str, commands
            stdin_data: str, data for standard in
            stdin_async: bool, whether use async for stdin
    """
    stdin = Subprocess.STREAM if stdin_async else subprocess.PIPE
    sub_process = Subprocess(shlex.split(cmd),
                             stdin=stdin,
                             stdout=Subprocess.STREAM,
                             stderr=Subprocess.STREAM,)
 
    if stdin_data:
        if stdin_async:
            yield Task(sub_process.stdin.write, stdin_data)
        else:
            sub_process.stdin.write(stdin_data)
 
    if stdin_async or stdin_data:
        sub_process.stdin.close()
 
    result, error = yield [Task(sub_process.stdout.read_until_close),
                           Task(sub_process.stderr.read_until_close),]
 
    raise Return((result, error))
 
@coroutine
def rng_process(wsh, serial, n):
    result, error = yield call_subprocess('python rng.py %s %s' % (serial, n))
    print "Random Number from sensor - %s" % result
    wsh.write_message("%s" % (result))
    
if __name__ == '__main__':
    parse_command_line()
    app.listen(options.port)

    tornado.ioloop.IOLoop.instance().start()