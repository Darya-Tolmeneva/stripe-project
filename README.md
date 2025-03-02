# Django + Stripe API для создания платёжных форм

## Описание

Этот проект представляет собой небольшое веб-приложение, которое представляет из себя магазин с товарами. 
Товары можно добавлять в корзину, а затем оплачивать с помощью Stripe. Также внутри администратора можно задать налог и скидку.

---
Проект доступен по ссылке https://web-production-64cd.up.railway.app/
## Установка и запуск

### 1. Клонировать репозиторий

```bash
https://github.com/Darya-Tolmeneva/stripe-project.git
cd stripe-project
```
### 2. Добавьте файл .env
```
SECRET_KEY=ваш_ключ
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
STRIPE_SECRET_KEY=ваш_ключ
STRIPE_PUBLIC_KEY=ваш_ключ
```
### 3. Для быстрого запуска
```
sudo docker build -t stripe .
sudo docker run -p 8000:8000 stripe
```
### 4. Для запуска вручную
```bash
python -m venv venv
source venv/bin/activate  # Для Linux/macOS
venv\Scripts\activate     # Для Windows

pip install -r requirements.txt

python manage.py runserver
```

--- 
Информация только на время сдачи тестового задания. Данные для admin
```
din
Klepa
```
