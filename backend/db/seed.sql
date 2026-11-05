-- seed.sql: sample data for local development (wipes existing rows)
TRUNCATE handoffs, bookings, customers, holidays, business_hours, services RESTART IDENTITY CASCADE;

-- 8 services
INSERT INTO services (name, duration_min, price) VALUES
    ('Haircut', 30, 500),
    ('Kids haircut', 20, 300),
    ('Shave', 15, 200),
    ('Beard trim', 20, 300),
    ('Hair color', 90, 1500),
    ('Hair spa', 60, 1200),
    ('Facial', 45, 800),
    ('Head massage', 30, 400);

-- weekday: 0 = Monday ... 6 = Sunday (Sunday missing = closed)
INSERT INTO business_hours (weekday, open_time, close_time) VALUES
    (0, '10:00', '19:00'),
    (1, '10:00', '19:00'),
    (2, '10:00', '19:00'),
    (3, '10:00', '19:00'),
    (4, '10:00', '19:00'),
    (5, '09:00', '17:00');

-- 4 holidays
INSERT INTO holidays (date, reason) VALUES
    ('2026-11-11', 'Staff training'),
    ('2026-12-25', 'Christmas'),
    ('2026-12-31', 'New Year''s Eve'),
    ('2027-01-01', 'New Year''s Day');

-- 10 customers (customer 1 = your real Telegram ID, for testing my_bookings)
INSERT INTO customers (telegram_id, name, phone) VALUES
    (5296779278, 'Viki', '+91 90000 00001'),
    (1000000002, 'Asha', '+91 90000 00002'),
    (1000000003, 'Rahul', '+91 90000 00003'),
    (1000000004, 'Meera', '+91 90000 00004'),
    (1000000005, 'Arjun', '+91 90000 00005'),
    (1000000006, 'Priya', '+91 90000 00006'),
    (1000000007, 'Karan', '+91 90000 00007'),
    (1000000008, 'Neha', '+91 90000 00008'),
    (1000000009, 'Sam', '+91 90000 00009'),
    (1000000010, 'Divya', '+91 90000 00010');

-- 20 bookings: past done/cancelled + future booked, no overlaps
-- end_time is calculated from the service duration
INSERT INTO bookings (customer_id, service_id, start_time, end_time, status)
SELECT v.customer_id, v.service_id, v.start_time,
       v.start_time + make_interval(mins => s.duration_min), v.status
FROM (VALUES
    (2,  1, timestamptz '2026-10-27 10:00+05:30', 'done'),
    (3,  5, timestamptz '2026-10-27 11:00+05:30', 'done'),
    (4,  7, timestamptz '2026-10-28 14:00+05:30', 'done'),
    (5,  3, timestamptz '2026-10-29 10:30+05:30', 'cancelled'),
    (6,  6, timestamptz '2026-10-30 15:00+05:30', 'done'),
    (7,  2, timestamptz '2026-10-31 09:30+05:30', 'done'),
    (8,  4, timestamptz '2026-10-31 11:00+05:30', 'done'),
    (1,  1, timestamptz '2026-10-31 12:00+05:30', 'done'),
    (1,  4, timestamptz '2026-11-03 10:00+05:30', 'booked'),
    (2,  7, timestamptz '2026-11-03 11:00+05:30', 'booked'),
    (9,  5, timestamptz '2026-11-03 14:00+05:30', 'booked'),
    (10, 1, timestamptz '2026-11-04 10:00+05:30', 'booked'),
    (3,  8, timestamptz '2026-11-04 12:00+05:30', 'booked'),
    (4,  6, timestamptz '2026-11-05 16:00+05:30', 'booked'),
    (5,  1, timestamptz '2026-11-06 10:30+05:30', 'booked'),
    (6,  3, timestamptz '2026-11-06 11:00+05:30', 'cancelled'),
    (7,  5, timestamptz '2026-11-07 09:00+05:30', 'booked'),
    (8,  2, timestamptz '2026-11-07 11:00+05:30', 'booked'),
    (1,  7, timestamptz '2026-11-09 17:00+05:30', 'booked'),
    (9,  1, timestamptz '2026-11-10 10:00+05:30', 'booked')
) AS v(customer_id, service_id, start_time, status)
JOIN services s ON s.id = v.service_id;

-- 2 handoffs
INSERT INTO handoffs (customer_id, status) VALUES
    (3, 'open'),
    (6, 'closed');
    
CREATE EXTENSION IF NOT EXISTS pgcrypto;

INSERT INTO owners (email, password_hash)
VALUES ('owner@salon.com', crypt('<test-password>', gen_salt('bf')));
