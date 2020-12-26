\echo mantra.sql
CREATE TABLE engine.__mantra (
    id serial unique not null primary key,
    description text,
    author text,
    reference text,
    datecreated timestamp with time zone,
    createdbyid integer constraint fk_mantra_postedbyid references engine.__member(id) on update cascade on delete set null,
    dateupdated timestamp with time zone,
    updatedbyid integer constraint fk_mantra_modifiedbyid references engine.__member(id) on update cascade on delete set null
);

create view engine.mantra as
    select 
        *,
        extract(epoch from datecreated) as datecreatedepoch,
        extract(epoch from dateupdated) as dateupdatedepoch
    from engine.__mantra;

grant select on engine.mantra to apache;
grant insert, update, delete on engine.__mantra to apache;
