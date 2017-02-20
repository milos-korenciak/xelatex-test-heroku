# run the commandline compilation
import bottle
import subprocess
import os

app = btl.default_app()

@btl.get("/")
def get_index():
    # serve static webpage with JS
    BIN_PATH = os.environ["BIN_PATH"]
    os.chdir(BIN_PATH)
    subprocess.call("xelatex --shell-escape -synctex=1 -interaction=nonstopmode  brano2017-02-09_buildpack.tex", shell=True)
    btl.response.content_type = 'application/pdf'
    return btl.static_file("brano2017-02-09_buildpack.pdf", root='.')

if __name__ == '__main__':
    btl.run(host="", port=8080, debug=True, reloader=True)
