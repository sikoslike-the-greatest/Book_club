# Book club | Medium | Web
---
## Информация
---
Первое правило клуба любителей книг - не говорить о клубе любителей книг. Но у вас будет шанс войти в него и поделиться своим мнением о ваших любымых книгах.

http://:5000
## Деплой
---
```
sudo docker build -t book-club-app .
sudo docker run -d -p 5000:5000 book-club-app
```
## Выдать участникам
---
IP:PORT сервера
## Описание
--- 
IDOR чтобы узнать почту админа + infromation disclosure в api книг (Можно узнать приватный комент) и Race Condition при генерации токена при входе по почте.
## Решение
---
Подробное решение в папке solve.
## Флаг
---
antiflag{57up1d_r4c3_c0nd1710n_bruh}