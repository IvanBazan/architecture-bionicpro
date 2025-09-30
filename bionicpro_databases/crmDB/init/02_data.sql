INSERT INTO users (user_id, username, email, first_name, last_name, created_at) VALUES
(1, 'ivan.petrov', 'ivan.petrov@bionicpro.com', 'Иван', 'Петров', '2025-01-01 08:00:00'),
(2, 'maria.sidorova', 'maria.sidorova@bionicpro.com', 'Мария', 'Сидорова', '2025-06-01 12:00:00'),
(3, 'alexei.ivanov', 'alexei.ivanov@bionicpro.com', 'Алексей', 'Иванов', '2025-07-01 08:23:00')
ON CONFLICT (user_id) DO UPDATE SET
username = EXCLUDED.username,
email = EXCLUDED.email,
first_name = EXCLUDED.first_name,
last_name = EXCLUDED.last_name,
created_at = EXCLUDED.created_at;