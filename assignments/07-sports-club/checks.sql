-- 1. Active memberships as of today
SELECT m.id AS member_id,
       m.first_name || ' ' || m.last_name AS member_name,
       mt.name AS membership_type,
       ms.start_date,
       ms.end_date
FROM memberships ms
JOIN members m ON m.id = ms.member_id
JOIN membership_types mt ON mt.id = ms.membership_type_id
WHERE date('now') BETWEEN date(ms.start_date) AND date(ms.end_date)
ORDER BY member_name;

-- 2. Enrollments count by class date
SELECT date(c.starts_at) AS class_date,
       COUNT(ce.id) AS enrolled_count
FROM classes c
JOIN class_enrollments ce ON ce.class_id = c.id
GROUP BY date(c.starts_at)
ORDER BY class_date;

-- 3. Trainers and their classes
SELECT t.first_name || ' ' || t.last_name AS trainer,
       t.specialization,
       c.name AS class_name,
       c.room,
       c.starts_at,
       c.ends_at
FROM trainers t
JOIN classes c ON c.trainer_id = t.id
ORDER BY trainer, c.starts_at;

-- 4. Members who have not visited in the last 30 days (but are still members)
SELECT m.id,
       m.first_name || ' ' || m.last_name AS member_name,
       MAX(v.visited_at) AS last_visit
FROM members m
LEFT JOIN visits v ON v.member_id = m.id
WHERE EXISTS (
    SELECT 1 FROM memberships ms
    WHERE ms.member_id = m.id
      AND date('now') BETWEEN date(ms.start_date) AND date(ms.end_date)
)
GROUP BY m.id
HAVING last_visit IS NULL OR julianday('now') - julianday(last_visit) > 30
ORDER BY last_visit;

-- 5. Top-3 most popular classes (by visit count)
SELECT c.name AS class_name,
       COUNT(v.id) AS visit_count
FROM classes c
LEFT JOIN visits v ON v.class_id = c.id
GROUP BY c.id
ORDER BY visit_count DESC, class_name
LIMIT 3;

-- 6. Revenue by membership type (linked payments)
SELECT mt.name AS membership_type,
       ROUND(SUM(p.amount), 2) AS total_revenue
FROM payments p
JOIN memberships ms ON ms.id = p.membership_id
JOIN membership_types mt ON mt.id = ms.membership_type_id
GROUP BY mt.id
ORDER BY total_revenue DESC;

-- 7. Schedule conflicts: same member, overlapping class times
SELECT m.first_name || ' ' || m.last_name AS member_name,
       c1.name AS class_a,
       c1.starts_at AS start_a,
       c1.ends_at AS end_a,
       c2.name AS class_b,
       c2.starts_at AS start_b,
       c2.ends_at AS end_b
FROM class_enrollments e1
JOIN class_enrollments e2
  ON e1.member_id = e2.member_id AND e1.class_id < e2.class_id
JOIN members m ON m.id = e1.member_id
JOIN classes c1 ON c1.id = e1.class_id
JOIN classes c2 ON c2.id = e2.class_id
WHERE c1.starts_at < c2.ends_at
  AND c2.starts_at < c1.ends_at
ORDER BY member_name, start_a;

-- 8. Classes with free seats (capacity vs enrollments)
SELECT c.name,
       c.capacity,
       COUNT(ce.id) AS enrolled,
       c.capacity - COUNT(ce.id) AS seats_left
FROM classes c
LEFT JOIN class_enrollments ce ON ce.class_id = c.id
GROUP BY c.id
HAVING seats_left > 0
ORDER BY seats_left, c.name;

-- 9. Trainer workload: number of classes per trainer
SELECT t.first_name || ' ' || t.last_name AS trainer,
       COUNT(c.id) AS class_count
FROM trainers t
LEFT JOIN classes c ON c.trainer_id = t.id
GROUP BY t.id
ORDER BY class_count DESC;

-- 10. Members with expired membership who still have future enrollments
SELECT DISTINCT m.first_name || ' ' || m.last_name AS member_name,
       c.name AS upcoming_class,
       c.starts_at
FROM members m
JOIN class_enrollments ce ON ce.member_id = m.id
JOIN classes c ON c.id = ce.class_id
WHERE NOT EXISTS (
    SELECT 1 FROM memberships ms
    WHERE ms.member_id = m.id
      AND date(c.starts_at) BETWEEN date(ms.start_date) AND date(ms.end_date)
)
ORDER BY c.starts_at;