### Паук для сбора информации из профиля Instagram

Установка:<br>
pip install -r requirements.txt<br>
Создать файл config.py в директории spiders с параметрами login и passwd для входа в аккаунт, который будет использоваться для доступа к социальной сети<br>
Запуск:<br>
В файле main.py заменить natgeo на нужный профиль<br>
python main.py<br>
Паук обходит ленту постов пользователя собирает в MongoDB следующие данные:<br>

1. user_name - Имя пользователя
2. user_id - ID пользователя
3. post_photos - Все фото из поста
4. post_pub_date - Дата публикации поста
5. like_count - Количество лайков поста
6. Скачивает фотографии. В БД сохраняется ссылка и путь для каждой фотографии
