create or replace view patches(database, major, minor, database_id, name, installed) as
SELECT d.name as database,
       p.major,
       p.minor,
       p.database_id,
       p.name,
       p.installed
FROM installed_patches p, databases d
WHERE p.database_id = d.id;

alter table patches
    owner to postgres;