create table __tag as (
    name text unique
);

create table if not exists engine.map_node_tag (
    "nodeid" bigint constraint fk_engine_map_node_tag_nodeid references engine.__node(id) on update cascade on delete cascade,
    "tag" text constraint fk_engine_map_node_sig_sigpath references engine.__tag(name) on update cascade on delete cascade
);

create unique index if not exists idx_map_node_tag on engine.map_node_tag (nodeid, tag);
