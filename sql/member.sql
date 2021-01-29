\echo member.sql

create table engine.__member (
  "id" bigserial unique not null primary key,
  "name" text unique not null,
  "email" text,
  "password" text,
  "datecreated" timestamptz,
  "createdbyid" bigint constraint fk_member_createdbyid references engine.__member(id) on update cascade on delete set null,
  "dateupdated" timestamptz,
  "updatedbyid" bigint constraint fk_member_updatedbyid references engine.__member(id) on update cascade on delete set null,
  "approvedbyid" bigint constraint fk_member_approvedbyid references engine.__member(id) on update cascade on delete set null,
  "dateapproved" timestamptz,
  "lastlogin" timestamptz,
  "lastloginfrom" inet,
  "attributes" jsonb
);

grant all on engine.__member to apache;
grant all on engine.__member_id_seq to apache;

create or replace view engine.member as
  select m.*,
  (select count(notify1.id) from engine.notify as notify1 where notify1.memberid = m.id) as notifycount,
  (select count(notify2.id) from engine.notify as notify2 where notify2.memberid = m.id) and notify2.status ='sent') as sentnotifycount
  extract(epoch from m.datecreated) as datecreatedepoch,
  extract(epoch from m.lastlogin) as lastloginepoch,
  extract(epoch from m.dateapproved) as dateapprovedepoch,
  extract(epoch from m.dateupdated) as dateupdatedepoch
  from engine.__member as m
;

grant select on engine.member to apache;
