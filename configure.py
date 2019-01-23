#! /usr/bin/python
from __future__ import print_function
import os
from jinja2 import Template
import subprocess
import yaml

inputRoot = "."

syncDir = ["img", "css", "md", "src", "templates"]
# the required directory to build if not exists
requiredDir = syncDir
syncList = syncDir

# (origin, relative path to the built distribution)
tplList = [("tpl/Makefile", "Makefile"), 
           ("tpl/index.md", "index.md"), 
           ("tpl/exemples/default.md", "default.md"),
           ("tpl/exemples/my.letter.md", "my.letter.md")]

compile = [{"input":"index.md", "output":"index.html", "option":"--css css/pandoc_elegent.css"}]
remove = ["index.md"]

pandoc_outputs = ['html', 'pdf', 'epub', 'docx']
pandoc_rules = { 'html' : {'option':'--to html5 --smart --standalone '},
                 'pdf'  : {'option':''}, 
                 'epub' : {'option':'--to epub3 '}, 
                 'docx' : {'option':''}}

pdf_templates = ["letter"]
html_templates = []

def copydir(src, dst):
    subprocess.check_output("rsync -arv %s %s"%(src,dst), shell=True)

def dreccopy(d, default):
    for k,v in default.items():
        sub = d.setdefault(k,v)    
        if isinstance(sub, dict) and isinstance(v, dict):
            dreccopy(sub, v)

            
def prepare_directory():
    for d in requiredDir:
        if not os.path.exists(d):
            os.mkdir(d)
          
def str_or_list(obj):
    if obj is None:
        return []
    if isinstance(obj, str):
        return [obj]
    return obj
    

def config_rules(kinds, publish):
    
    cmds = {
        "opts":[], # options in the make file
        "ftrs":[], 
        "hdrs":[], 
        "tgts":[], # targets matching 
        "rules":[], # rules matching 
        "guards":[], 
        "tgtdep":{}, 
        "deps":[], 
        "srcs":[]
    }
    
    for kind in kinds['custom']:
        config_kind(cmds, kind, kinds['default'], publish)
    config_kind(cmds, kinds['default'], {}, publish)        
    
    for ext, lst in cmds["tgtdep"].items():
        cmds['deps'].append(
            "{ext} : {tgt}".format(ext=ext, tgt=" ".join(lst))
        )
        
    return cmds

    
def config_kind(cmds, kind, d, publish):
    kind.setdefault('ext', '')
    
    mdfooters = str_or_list(kind.get('mdfooters', d.get('mdfooters', [])))
    mdheaders = str_or_list(kind.get('mdheaders', d.get('mdheaders', [])))
    
        
    ftrs = ""
    if mdfooters:
        for mf in mdfooters:
            ftrs += mf+" "
    hdrs = ""
    if mdheaders:
        for mh in mdheaders:
            hdrs += mh+" "
    
    
    outputs = kind.setdefault('outputs', {}) 
    if kind['ext']:
        kindp = ".%s"%kind['ext']
        kinds = "_%s"%kind['ext']
        kindn = kind['ext']
    else:
        kindp = ""
        kinds = ""
        kindn = ""
    
    vars = dict(kindp=kindp, kinds=kinds, kindn=kindn) 
    
    cmds["srcs"].append(
        "SOURCE_PMD{kinds} := $(wildcard $(SOURCE)/*{kindp}.pmd)".format(**vars)
    )
    cmds["srcs"].append(
        "SOURCE_MD{kinds} := $(wildcard $(SOURCE)/*{kindp}.md)".format(**vars)
    )
    for ext in  pandoc_outputs:
        vars['ext'] = ext
        output = outputs.setdefault(ext, {})           
        cmd, tplguard = config_output(ext, output, d.get('outputs', {}).get(ext, {}), publish)
        cmds["opts"].append(
            "PANDOC_OPTS{kinds}_{ext}={cmd}".format(cmd=cmd, **vars)
        )
        cmds['guards'].append(
            "tpl_guard{kinds}_{ext}={tplguard}".format(tplguard=("@%s"%tplguard if tplguard else ""), **vars)
        )
                     
        cmds["tgts"].append(
                "TARGET{kinds}_{ext}= $(subst $(SOURCE)/, $(OUTPUT)/, $(SOURCE_MD{kinds}:{kindp}.md={kindp}.{ext})) $(subst $(SOURCE)/, $(OUTPUT)/, $(SOURCE_PMD{kinds}:{kindp}.pmd={kindp}.{ext}))".format(**vars)    
        )
        cmds["tgtdep"].setdefault(ext, []).append("$(TARGET{kinds}_{ext})".format(**vars))
        cmds["tgtdep"].setdefault("all", []).append("$(TARGET{kinds}_{ext})".format(**vars))
        
    
        mdrule = """
$(OUTPUT)/%{kindp}.{ext} : $(SOURCE)/%{kindp}.md
\t$(dir_guard)
\t$(src_dir_guard)
\t$(src_template_dir_guard)
\t$(tpl_guard{kinds}_{ext})
\t$(PANDOC) $(PANDOC_OPTIONS) $(PANDOC_I_OPTIONS) $(PANDOC_OPTS{kinds}_{ext}) -o $@ $(PANDOC_HDRS{kinds}) $< $(PANDOC_FTRS{kinds})
""".format(**vars)
        cmds['rules'].append(mdrule)
        pmdrule = """
$(OUTPUT)/%{kindp}.{ext} : $(SOURCE)/%{kindp}.pmd
\t$(dir_guard)
\t$(PWEAVE) $(PWEAVE_OPTIONS) $< -o $(OUTPUT)/$(<:.pmd=.md)
\t$(src_dir_guard)
\t$(src_template_dir_guard)
\t$(tpl_guard{kinds}_{ext})
\t$(PANDOC) $(PANDOC_OPTIONS) $(PANDOC_I_OPTIONS) $(PANDOC_OPTS{kinds}_{ext}) -o $@ $(PANDOC_HDRS{kinds}) $(OUTPUT)/$(<:.pmd=.md) $(PANDOC_FTRS{kinds})
""".format(**vars)
        cmds['rules'].append(pmdrule)
    ### END of FOR ext
         
    cmds["ftrs"].append(
        "PANDOC_FTRS{kinds}={ftrs}".format(**vars, ftrs=ftrs)
    )
    cmds["hdrs"].append(
        "PANDOC_HDRS{kinds}={hdrs}".format(**vars, hdrs=hdrs)
    )
    
    
    
    
def config_output(ext, output, d, publish):
    
    cmd = pandoc_rules.get(ext, {'option':''}).get('option', '')
    
    tplguard = ""
    
    css = str_or_list(output.get('css', d.get('css', [])))
    template = output.get('template', d.get('template', None))  
    header = str_or_list(output.get('header', d.get('header', [])))
    footer = str_or_list(output.get('footer', d.get('footer', [])))    
    
    
    if css:
        for c in css:            
            cmd += "--css %s "%c
    
    if template:
        if publish['remote']:
            root, name = os.path.split(template)
            cmd += "--template=.pandoc/templates/%s "%name
            tplguard += "if [ ! -f .pandoc/templates/{name} ]; then $(CURL) {url}/{template} > .pandoc/templates/{name}; fi".format(template=template,name=name,url=publish['url'])
        else:
            cmd += "--template=%s "%(os.path.join(publish['url'], template))
    if header:
        for h in header:
            cmd += "--include-before-body %s "%h
        
    if footer:
        for f in footer:
            cmd += "--include-after-body %s "%f
    return cmd, tplguard
        
if __name__ == "__main__":    
    with open("config.yaml") as f:
        conf = yaml.load(f.read())
    prepare_directory()
    
    # to avoid any errors fill the configure yaml with the 
    # basics
    dreccopy(conf, {"pandoc":{"packages":[]}, 
                     "kinds": {"default":{}, "custom":[]}, 
                     "publish":{}})
    
    
    pandoc = conf["pandoc"]
    rules  = conf["publish"]
    
    packages = "-f markdown"+"".join("+"+p for p in pandoc['packages'])+" "
    
    vars = {k:v for k,v in globals().items() if not k.startswith("_")}
    install = []
    clear = []
    
    vars = {'pandoc_outputs': pandoc_outputs, 
            'pandoc':conf['pandoc'], 
            'pdc':{'option':packages}, 
            'conf':conf
            }        
        
    for rule in conf['publish']:
        name = rule.get('name', 'tmp')
        url    = rule.get('url', ".")
        dest   = rule.get('destination', name)
        remote = rule.get('remote', False)
        
        cmds = config_rules(conf['pandoc']['kinds'], rule)
        
        vars.update(urlRoot=url, outputRoot=dest, remote=remote, cmds=cmds)
            
        if remote:
            # create a subdirectory with the publish name 
            # than a rsync will be enough to upload
            if not os.path.exists(name):
                os.mkdir(name)
            installDir = name
        else:
            if not os.path.exists(dest):
                os.mkdir(dest)
            installDir = dest
            
        syncl = list(syncList) 
        install.append("#########################")
        install.append("# %s"%name)
        # build the templates
        for fname, sname in tplList:
            with open(fname) as f:
                tpl = Template(f.read())
                tpldest = os.path.join(name, sname)
                with open(tpldest, "w") as g:
                    g.write(tpl.render(**vars))            
            syncl.append(os.path.join(installDir, sname))    
                
        #copydir(os.path.join(inputRoot, "img"), local)
        #copydir(os.path.join(inputRoot, "md"), local)
        #copydir(os.path.join(inputRoot, "css"), local)
        for r in compile:
            pandoc = "pandoc -o {name}/{output} {name}/{input} {option}".format(**r, name=name)
            install.append(pandoc)
            syncl.append("{name}/{output}".format(**r, name=name)) 
        
        install.append("rsync -arv %s %s"%(" ".join(syncl), dest))
                
        if name!=dest:
            clear.append("rm -rf %s"%name)
    
    with open("install", "w") as g:
        g.write("#! /bin/sh\n")
        g.write( "\n".join(install))
    os.chmod("install", 0o755)
    
    with open("clear", "w") as g:
        g.write("#! /bin/sh\n")
        g.write( "\n".join(clear))
    os.chmod("clear", 0o755)
        
        