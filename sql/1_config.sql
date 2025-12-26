INSERT INTO public.config ("key",value,created_at,updated_at,description) VALUES
	 ('EDIT_REQUEST_LIMIT','11','2025-12-24 16:15:12.272',NULL,'оганичение на кол-во редактирований профиля в сутки'),
	 ('SIMILARITY_THRESHOLD','0.4','2025-12-24 16:16:45.826',NULL,'граница схожисти при поиске новых сервисов через gpt'),
	 ('BATCH_MESSAGE_LIMIT','1000','2025-12-24 16:16:45.830',NULL,'батч для рассылки сообщений за раз'),
	 ('SCHEDULE_MESSAGES_TO_USERS','{"cron": "*/1 * * * *", "cron_offset": "Asia/Almaty"}','2025-12-24 16:16:45.833',NULL,'расписание рассылки сообщений'),
	 ('SCHEDULE_VALIDATE_MESSAGES','{"cron": "*/1 * * * *", "cron_offset": "Asia/Almaty"}','2025-12-24 16:16:45.834',NULL,'расписание валидации сообщений'),
	 ('SCHEDULE_UPDATE_STATUSES','{"cron": "*/15 * * * *", "cron_offset": "Asia/Almaty"}','2025-12-24 16:16:45.837',NULL,'расписание переноса модерированных данных'),
	 ('UTC_PLUS_5','{"utc_shift": 5}','2025-12-24 16:15:12.270',NULL,'ZoneInfo("Asia/Almaty")'),
	 ('ADMIN_IDS','{988269770,1}','2025-12-24 16:16:45.828',NULL,'список админов');
