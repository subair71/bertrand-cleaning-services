"""Export a self-contained, offline-friendly client preview without a build framework."""
from pathlib import Path
import base64,re,sys,mimetypes
root=Path(__file__).resolve().parent.parent
out=Path(sys.argv[1] if len(sys.argv)>1 else '/tmp/Bertrand-Demo.html')
def data_uri(path):
    mime=mimetypes.guess_type(path)[0] or 'application/octet-stream'
    return 'data:'+mime+';base64,'+base64.b64encode((root/path).read_bytes()).decode()
modules=['data','i18n','repository','logic','config','analytics','app']
code='\n'.join(re.sub(r'^import .*?;\s*','', (root/'js'/f'{m}.js').read_text(),flags=re.M).replace('export ','') for m in modules)
code=code.replace("const $=","const db=repository,esc=escapeHTML;const $=")
code=code.replace("function currentPage(){return location.pathname.split('/').pop()?.replace('.html','')||'index'}", "let offlinePage='index',offlineParams=new URLSearchParams();function currentPage(){return offlinePage}")
# Keep all screens in the same document without requiring file:// History API permissions.
code=code.replace("history.pushState({},'',url);", "const dest=new URL(url,location.href);offlinePage=dest.searchParams.get('page')||'index';offlineParams=dest.searchParams;")
code=code.replace("new URLSearchParams(location.search).get('service')", "offlineParams.get('service')").replace("new URLSearchParams(location.search).get('id')", "offlineParams.get('id')")
code=code.replace("history.replaceState({},'',url);", "/* Offline language selection stays in memory/local preference. */")
# Resolve known same-site route links to an in-document page parameter.
code=code.replace("document.querySelectorAll('a[data-nav]').forEach(a=>{", "document.querySelectorAll('a[data-nav]').forEach(a=>{const target=new URL(a.getAttribute('href'),location.href);const dest=new URL(location.href);dest.search=target.search;dest.searchParams.set('page',target.pathname.split('/').pop().replace('.html',''));a.href=dest.href;")
# Embedded proposal can be downloaded independently from the preview footer.
proposal=(root/'docs/proposal.html').read_text().replace('href="../index.html"','href="Bertrand-Demo.html"')
proposal_uri='data:text/html;base64,'+base64.b64encode(proposal.encode()).decode()
code=code.replace('href="docs/proposal.html"',f'download="Bertrand-Proposal.html" href="{proposal_uri}"')
css=(root/'style.css').read_text()
for p in (root/'assets').rglob('*'):
    if p.is_file() and p.suffix in ['.png','.webp','.woff2','.svg']:
        name=p.relative_to(root).as_posix();uri=data_uri(name)
        code=code.replace(name,uri);css=css.replace(name,uri)
html='<!doctype html><html lang="fr" dir="ltr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><meta name="description" content="Bertrand bilingual demo"><title>Bertrand — Interactive demo</title><style>'+css+'</style></head><body><div id="app"></div><script type="module">'+code+'</script></body></html>'
out.parent.mkdir(parents=True,exist_ok=True);out.write_text(html)
print(str(out),out.stat().st_size)
