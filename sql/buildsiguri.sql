\echo buildsiguri.sql
create extension "ltree_plpython2u" cascade;

create or replace language "plpython2u";

create or replace function engine.buildsiguri(path ltree)
returns text as $$
    res = []
    for p in path:
      if p is not None:
        p = p.replace("top", "")
        p = p.replace("top.", "")
        p = p.replace("_", "-")
#        p = p.replace(".", "/")
#        p = p + "/"
#        p = p.replace("//", "/")
#        p = p.lstrip("/")
        if p is not None and p != "":
          res.append(p)
    uri = "/".join(res)+"/"
    uri = uri.lstrip("/")
    return uri

$$
language plpython2u transform for type ltree;
