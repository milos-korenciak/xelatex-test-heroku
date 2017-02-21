# run the commandline compilation
import bottle
import subprocess
import os
import tempfile
import shutil

app = bottle.default_app()

class TempDirContext:
    def __enter__(self):
        # make a temp dir 
        self.tempdir = tempfile.mkdtemp()
        return self.tempdir

    def __exit__(self, exc_type, exc_val, exc_tb):
        # remove the temp dir
        shutil.rmtree(self.tempdir, ignore_errors=True)
        return (exc_type is None)  # True if everything is OK
    

@bottle.get("/")
def get_index():
    # serve static webpage with JS
    print(os.environ)
    BIN_PATH = os.environ.get("BIN_PATH", "/app/buildpack/bin/x86_64-linux/")
    os.chdir(BIN_PATH)
    subprocess.call("./xelatex --shell-escape -synctex=1 -interaction=nonstopmode  brano2017-02-09_buildpack.tex", shell=True)
    bottle.response.content_type = 'application/pdf'
    return bottle.static_file("brano2017-02-09_buildpack.pdf", root='.')


@bottle.post("/")
def process_tex2pdf():
    # serve static webpage with JS
    with TempDirContext() as tempdir:
        print("I have tempdir:", tempdir)
        os.chdir(tempdir)  # we will work in tempdir
        
        with open(os.path.join(tempdir, "sample.tex"), "wb") as sample_tex:
            buf = bottle.request.body.read()
            sample_tex.write(buf)
        print("I have written the sample.tex")
        
        BIN_PATH = os.environ.get("BIN_PATH", "/app/buildpack/bin/x86_64-linux/")  # we search for the xelatex binary 
        XELATEX_PATH = os.path.join(BIN_PATH, "xelatex")
        print("I have XELATEX_PATH", XELATEX_PATH, " BIN_PATH", BIN_PATH)
        
        subprocess.call(XELATEX_PATH + " --shell-escape -synctex=1 -interaction=nonstopmode sample.tex", shell=True)
        bottle.response.content_type = 'application/pdf'
        # bottle.response.content_type = 'text/plain'
        # print("returning the sample.tex")
        return bottle.static_file("sample.pdf", root=tempdir)


if __name__ == '__main__':
    bottle.run(host="", port=8080, debug=True, reloader=True)
