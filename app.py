from ShrekLadder.app import app
from ShrekLadder.config_file import config, configi
import scss
import os
import coffeescript

app.static_folder = os.path.join(os.getcwd(), "static")

if __name__ == '__main__':
    app.debug = True

    app.run(config('host'), configi('port'))

def prepare():
    compiler = scss.Scss(scss_opts = {
        'style': 'compressed' if not app.debug else None
    }, search_paths=[
        os.path.join(os.getcwd(), 'styles')
    ])
    # Compile styles (scss)
    d = os.walk('styles')
    for f in list(d)[0][2]:
        if os.path.splitext(f)[1] == ".scss":
            with open(os.path.join('styles', f)) as r:
                output = compiler.compile(r.read())

            parts = f.rsplit('.')
            css = '.'.join(parts[:-1]) + ".css"

            with open(os.path.join(app.static_folder, css), "w") as w:
                w.write(output)
                w.flush()
        else:
            copyfile(os.path.join('styles', f), os.path.join(app.static_folder, f))
    d = os.walk('coffee')
    for f in list(d)[0][2]:
        print(f)
        outputpath = os.path.join(app.static_folder, "scripts", os.path.basename(f))
        inputpath = os.path.join('coffee', f)

        if os.path.splitext(f)[1] == ".js":
            copyfile(inputpath, outputpath)
        elif os.path.splitext(f)[1] == ".manifest":
            with open(inputpath) as r:
                manifest = r.read().split('\n')

            javascript = ''
            for script in manifest:
                script = script.strip(' ')

                if script == '' or script.startswith('#'):
                    continue

                bare = False
                if script.startswith('bare: '):
                    bare = True
                    script = script[6:]

                with open(os.path.join('coffee', script)) as r:
                    coffee = r.read()
                    if script.endswith('.js'):
                        javascript += coffee # straight up copy
                    else:
                        javascript += coffeescript.compile(coffee, bare=bare)
            output = '.'.join(f.rsplit('.')[:-1]) + '.js'

            # TODO: Bug the slimit guys to support python 3
            #if not app.debug:
            #    javascript = minify(javascript)

            with open(os.path.join(app.static_folder, "scripts", output), "w") as w:
                w.write(javascript)
                w.flush()

        elif os.path.splitext(f)[1] == ".manifest_inline":
            with open(inputpath) as r:
                manifest = r.read().split('\n')

            javascript = ''
            for script in manifest:
                script = script.strip(' ')

                if script == '' or script.startswith('#'):
                    continue

                bare = False
                if script.startswith('bare: '):
                    bare = True
                    script = script[6:]

                with open(os.path.join('coffee', script)) as r:
                    coffee = r.read()
                    if script.endswith('.js'):
                        javascript += coffee # straight up copy
                    else:
                        javascript += coffeescript.compile(coffee, bare=bare)
            output = '.'.join(f.rsplit('.')[:-1]) + '.js'

            # TODO: Bug the slimit guys to support python 3
            #if not app.debug:
            #    javascript = minify(javascript)

            with open(os.path.join(os.getcwd(), "ShrekLadder/templates/scripts", output), "w") as w:
                w.write(javascript)
                w.flush()