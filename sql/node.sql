\echo node.sql
--create extension ltree; -- moved to extensions.sql

create table if not exists engine.__node (
    "id" bigserial unique not null primary key,
    "parentid" bigint constraint fk_engine_node_parentid references engine.__node(id) on update cascade on delete set null,
    "attributes" jsonb,
    "datecreated" timestamptz,
    "createdbyid" bigint constraint fk_engine_node_createdbyid references engine.__member(id) on update cascade on delete set null,
    "dateupdated" timestamptz,
    "updatedbyid" bigint constraint fk_engine_node_updatedbyid references engine.__member(id) on update cascade on delete set null,
    "dateapproved" timestamptz,
    "approvedbyid" bigint constraint fk_engine_node_approvedbyid references engine.__member(id) on update cascade on delete set null
);

---create index idx_node_sigs_gist on engine.__node using gist(sigs);
grant insert, update, delete on engine.__node to apache;

create index idx_node_attributes ON engine.__node USING GIN (attributes);

create table if not exists engine.map_node_sig (
    "nodeid" bigint constraint fk_engine_map_node_sig_nodeid references engine.__node(id) on update cascade on delete cascade,
    "sigpath" ltree constraint fk_engine_map_node_sig_sigpath references engine.__sig(path) on update cascade on delete cascade
);

grant insert, update, delete, select on engine.map_node_sig to apache;

create or replace view engine.node as
    select
        n.*,
--        array_to_json(array(select sigpath from engine.map_node_sig where engine.map_node_sig.nodeid = engine.__node.id order by sigpath)) as sigs,
        extract(epoch from n.datecreated) as datecreatedepoch,
        extract(epoch from n.dateupdated) as dateupdatedepoch,
        extract(epoch from n.dateapproved) as dateapprovedepoch,
        coalesce(m1.name, 'a. nonymous'::text) as createdbyname,
        coalesce(m2.name, 'a. nonymous'::text) as updatedbyname,
        coalesce(m3.name, 'a. nonymous'::text) as approvedbyname,
        array(select distinct map.sigpath from engine.map_node_sig as map where map.nodeid = n.id order by map.sigpath) AS sigs,
        (select count(id) from (select id from engine.__node as subnode where subnode.parentid=n.id) as subnodes) as subnodecount
    from engine.__node as n
    left join engine.__member as m1 ON (m1.id = n.createdbyid)
    left join engine.__member as m2 ON (m2.id = n.updatedbyid)
    left join engine.__member as m3 ON (m3.id = n.approvedbyid)
;

grant select on engine.node to apache;

create unique index if not exists idx_map_node_sig on engine.map_node_sig (nodeid, sigpath);

grant select, update on engine.__node_id_seq to apache;

-- alter table engine.__node add column parentid bigint;
-- alter table engine.__node add constraint fk_engine_node_parentid foreign key (parentid) references engine.__node(id) on update cascade on delete set null;
