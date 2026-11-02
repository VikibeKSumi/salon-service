from psycopg.rows import class_row
from psycopg_pool import ConnectionPool
from schemas.capability_services_schema import Service, Customer, BusyInterval, Hours, Booking, Handoff


# every booking query returns the service name too, so callers can show it
BOOKING_COLUMNS = "b.id, b.customer_id, b.service_id, s.name AS service_name, b.start_time, b.end_time, b.status"


class PostgresRepository:

    def __init__(self, pool: ConnectionPool):
        self.pool = pool

    # ==services / hours===
    def list_services(self) -> list[Service]:
        with self.pool.connection() as conn:
            with conn.cursor(row_factory=class_row(Service)) as cur:
                return cur.execute(
                    "SELECT id, name, duration_min, price FROM services ORDER BY id"
                ).fetchall()

    def get_service(self, service_id: int) -> Service | None:
        with self.pool.connection() as conn:
            with conn.cursor(row_factory=class_row(Service)) as cur:
                return cur.execute(
                    "SELECT id, name, duration_min, price FROM services WHERE id = %s", (service_id,)
                ).fetchone()

    def is_holiday(self, day) -> bool:
        with self.pool.connection() as conn:
            return conn.execute("SELECT 1 FROM holidays WHERE date = %s", (day,)).fetchone() is not None

    def get_hours(self, weekday: int) -> Hours | None:
        with self.pool.connection() as conn:
            with conn.cursor(row_factory=class_row(Hours)) as cur:
                return cur.execute(
                    "SELECT open_time, close_time FROM business_hours WHERE weekday = %s", (weekday,)
                ).fetchone()

    # ==customers===
    def upsert_customer(self, telegram_id: int, name: str | None) -> Customer:
        with self.pool.connection() as conn:
            with conn.cursor(row_factory=class_row(Customer)) as cur:
                return cur.execute(
                    """
                    INSERT INTO customers (telegram_id, name)
                    VALUES (%s, %s)
                    ON CONFLICT (telegram_id)
                    DO UPDATE SET name = COALESCE(EXCLUDED.name, customers.name)
                    RETURNING id, telegram_id, name, phone
                    """,
                    (telegram_id, name),
                ).fetchone()

    def get_customer(self, telegram_id: int) -> Customer | None:
        with self.pool.connection() as conn:
            with conn.cursor(row_factory=class_row(Customer)) as cur:
                return cur.execute(
                    "SELECT id, telegram_id, name, phone FROM customers WHERE telegram_id = %s",
                    (telegram_id,),
                ).fetchone()

    # ==bookings===
    def get_busy(self, start, end, exclude_booking_id: int | None = None) -> list[BusyInterval]:
        with self.pool.connection() as conn:
            with conn.cursor(row_factory=class_row(BusyInterval)) as cur:
                return cur.execute(
                    """
                    SELECT start_time, end_time FROM bookings
                    WHERE status = 'booked' AND start_time < %s AND end_time > %s
                      AND id IS DISTINCT FROM %s
                    """,
                    (end, start, exclude_booking_id),
                ).fetchall()

    def insert_booking(self, customer_id, service_id, start, end) -> Booking:
        with self.pool.connection() as conn:
            with conn.cursor(row_factory=class_row(Booking)) as cur:
                return cur.execute(
                    f"""
                    WITH b AS (
                        INSERT INTO bookings (customer_id, service_id, start_time, end_time)
                        VALUES (%s, %s, %s, %s)
                        RETURNING *
                    )
                    SELECT {BOOKING_COLUMNS} FROM b JOIN services s ON s.id = b.service_id
                    """,
                    (customer_id, service_id, start, end),
                ).fetchone()

    def get_upcoming_bookings(self, customer_id: int) -> list[Booking]:
        with self.pool.connection() as conn:
            with conn.cursor(row_factory=class_row(Booking)) as cur:
                return cur.execute(
                    f"""
                    SELECT {BOOKING_COLUMNS} FROM bookings b JOIN services s ON s.id = b.service_id
                    WHERE b.customer_id = %s AND b.status = 'booked' AND b.start_time > now()
                    ORDER BY b.start_time
                    """,
                    (customer_id,),
                ).fetchall()

    def get_upcoming_booking(self, booking_id: int, customer_id: int) -> Booking | None:
        # filtered by customer_id: a customer can only ever see their own booking
        with self.pool.connection() as conn:
            with conn.cursor(row_factory=class_row(Booking)) as cur:
                return cur.execute(
                    f"""
                    SELECT {BOOKING_COLUMNS} FROM bookings b JOIN services s ON s.id = b.service_id
                    WHERE b.id = %s AND b.customer_id = %s AND b.status = 'booked' AND b.start_time > now()
                    """,
                    (booking_id, customer_id),
                ).fetchone()

    def cancel_booking(self, booking_id: int, customer_id: int) -> Booking | None:
        with self.pool.connection() as conn:
            with conn.cursor(row_factory=class_row(Booking)) as cur:
                return cur.execute(
                    f"""
                    WITH b AS (
                        UPDATE bookings SET status = 'cancelled'
                        WHERE id = %s AND customer_id = %s AND status = 'booked' AND start_time > now()
                        RETURNING *
                    )
                    SELECT {BOOKING_COLUMNS} FROM b JOIN services s ON s.id = b.service_id
                    """,
                    (booking_id, customer_id),
                ).fetchone()

    def move_booking(self, booking_id: int, customer_id: int, start, end) -> Booking | None:
        with self.pool.connection() as conn:
            with conn.cursor(row_factory=class_row(Booking)) as cur:
                return cur.execute(
                    f"""
                    WITH b AS (
                        UPDATE bookings SET start_time = %s, end_time = %s
                        WHERE id = %s AND customer_id = %s AND status = 'booked'
                        RETURNING *
                    )
                    SELECT {BOOKING_COLUMNS} FROM b JOIN services s ON s.id = b.service_id
                    """,
                    (start, end, booking_id, customer_id),
                ).fetchone()

    # ==handoffs===
    def open_handoff(self, customer_id: int) -> Handoff:
        with self.pool.connection() as conn:
            with conn.cursor(row_factory=class_row(Handoff)) as cur:
                created = cur.execute(
                    """
                    INSERT INTO handoffs (customer_id) VALUES (%s)
                    ON CONFLICT (customer_id) WHERE status = 'open' DO NOTHING
                    RETURNING id, customer_id, status
                    """,
                    (customer_id,),
                ).fetchone()
                if created:
                    return created
                # already open: return the existing one
                return cur.execute(
                    "SELECT id, customer_id, status FROM handoffs WHERE customer_id = %s AND status = 'open'",
                    (customer_id,),
                ).fetchone()

    def has_open_handoff(self, customer_id: int) -> bool:
        with self.pool.connection() as conn:
            return conn.execute(
                "SELECT 1 FROM handoffs WHERE customer_id = %s AND status = 'open'", (customer_id,)
            ).fetchone() is not None
