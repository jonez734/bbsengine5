\echo notify
create table engine.__notify (
  "id" serial unique not null primary key,
  "memberid" integer not null constraint fk_notify_memberid references engine.__member(id) on update cascade on delete cascade,
  "sessionid" text constraint fk_notify_sessionid references engine.__session(id) on update cascade on delete set null,
  "type" text not null,
  "status" text not null,
  "template" text not null,
  "urgent" boolean default 'f',
  "datecreated" timestamptz,
  "createdbyid" integer constraint fk_notify_createdbyid references engine.__member(id) on update cascade on delete set null,
  "dateupdated" timestamptz,
  "updatedbyid" integer constraint fk_notify_updatedbyid references engine.__member(id) on update cascade on delete set null,
  "data" jsonb
);

grant all on engine.__notify to "apache";
grant all on engine.__notify_id_seq to "apache";

--create view engine.notify as
--  select engine.__notify.*,
--    extract(epoch from datecreated) as datecreatedepoch,
--    extract(epoch from datedisplayed) as datedisplayedepoch
--  from engine.__notify
--;

create or replace view engine.notify as
  select n.*,
    extract(epoch from datecreated) as datecreatedepoch,
    extract(epoch from dateupdated) as dateupdatedepoch
  from engine.__notify as n
;

grant select on engine.notify to apache;

create or replace language plpython2u;

-- copied from trailersdemo, originally written 2016-mar-31 with help from #postgresql
-- this trigger deletes a notify if the memberid and the sessionid are both None
CREATE FUNCTION checknotify()
  RETURNS trigger
AS $$
    plpy.log("checknotify.100: inside checknotify()")
    if TD["when"] == "BEFORE" and TD["level"] == "ROW" and TD["event"] == "UPDATE" and TD["old"]["memberid"] is None and TD["old"]["sessionid"] is None:
      plpy.execute("delete from __notify where memberid is null and sessionid is null")
      plpy.log("checknotify.110: executed delete")
      return "SKIP"
    plpy.log("checknotify.115: did not execute delete")
    return "OK"
$$ LANGUAGE plpython2u;

create trigger checknotify before update on engine.__notify for each row execute procedure checknotify();

-- grant select, insert, update on engine.__notify to apache;
grant select on engine.notify to apache;

--alter table engine.__notify drop column displayed;
--alter table engine.__notify alter column data type jsonb using data::jsonb;
--alter table engine.__notify drop column datedisplayed;
--alter table engine.__notify add column template text not null;
--alter table engine.__notify add column urgent boolean default 'f';
--alter table engine.__notify alter column sessionid drop not null ;
