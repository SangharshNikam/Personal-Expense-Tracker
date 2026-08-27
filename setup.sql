create table expenses (
    id bigint generated always as identity primary key,
    date date not null,
    amount numeric(10, 2) not null,
    category text not null,
    payment_method text not null,
    description text,
    created_at timestamp with time zone default now()
);

-- Optional: index for faster date-range queries
create index idx_expenses_date on expenses (date);
