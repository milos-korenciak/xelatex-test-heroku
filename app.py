# run the commandline compilation
import bottle
import subprocess
import os

app = bottle.default_app()

@bottle.get("/")
def get_index():
    # serve static webpage with JS
    print(os.environ)
    BIN_PATH = os.environ.get("BIN_PATH", "/app/buildpack/bin/x86_64-linux/")
    os.chdir(BIN_PATH)
    subprocess.call("xelatex --shell-escape -synctex=1 -interaction=nonstopmode  brano2017-02-09_buildpack.tex", shell=True)
    bottle.response.content_type = 'application/pdf'
    return bottle.static_file("brano2017-02-09_buildpack.pdf", root='.')


@bottle.get("/log")
def get_log():
    # serve logfile
    bottle.response.content_type = 'text/plain; charset=latin9'
    return bottle.static_file("logfile.log", root='/tmp/')

if __name__ == '__main__':
    bottle.run(host="", port=8080, debug=True, reloader=True)
