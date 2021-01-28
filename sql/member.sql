\echo member.sql

create table engine.__member (
  "id" bigserial unique not null primary key,
  "username" text unique not null,
  "name" text,
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

create view engine.member as
  select m.*,
  extract(epoch from datecreated) as datecreatedepoch,
  extract(epoch from lastlogin) as lastloginepoch,
  extract(epoch from dateapproved) as dateapprovedepoch,
  extract(epoch from dateupdated) as dateupdatedepoch

  from engine.__member as m
;

grant select on engine.member to apache;
