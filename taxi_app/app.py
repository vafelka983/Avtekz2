from flask import Flask, render_template, request, redirect, url_for, session, flash
import database

app = Flask(__name__)
app.secret_key = 'rose_taxi_secret_key_2024'

database.init_db()


@app.route('/')
def index():
    free_cars = database.get_free_cars()
    return render_template('index.html', free_cars=free_cars)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone = request.form.get('phone')
        sms_code = request.form.get('sms_code')

        user = database.authenticate(phone, sms_code)

        if user:
            session['user_phone'] = phone
            session['user_name'] = user[0]
            flash(f'Добро пожаловать, {user[0]}!', 'success')
            return redirect(url_for('order'))
        else:
            flash('Неверный номер телефона или СМС-код', 'error')

    return render_template('login.html')


@app.route('/order', methods=['GET', 'POST'])
def order():
    if 'user_phone' not in session:
        flash('Пожалуйста, авторизуйтесь сначала', 'error')
        return redirect(url_for('login'))

    active_order = database.get_active_order(session['user_phone'])

    if request.method == 'POST':
        destination = request.form.get('destination')

        if not destination:
            flash('Пожалуйста, укажите адрес назначения', 'error')
            return redirect(url_for('order'))

        order_info = database.create_order(session['user_phone'], destination)

        if order_info:
            flash('Такси успешно вызвано!', 'success')
            return render_template('order_info.html', order=order_info, user_name=session['user_name'])
        else:
            flash('К сожалению, нет свободных машин. Попробуйте позже.', 'error')

    return render_template('order.html', user_name=session['user_name'], active_order=active_order)


@app.route('/logout')
def logout():
    session.clear()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)  # nosec
