drop table if exists purchase;
    create table purchase (
    id integer primary key autoincrement,
    num_tickets integer,
    show_time text,
    show_date text,
    zip text,
    self_input text
);