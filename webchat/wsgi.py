import sys
import os.path

par_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                       os.path.pardir)
sys.path.append(par_dir)

from flask import Flask, request, redirect, url_for
from flask import render_template
from flask_wtf import CsrfProtect
from werkzeug.exceptions import NotFound
from flask_login import LoginManager, login_user, logout_user, login_required
from flask_login import current_user
from flask_bootstrap import Bootstrap
from flask_socketio import SocketIO, emit, join_room, leave_room

from webchat import db
from webchat.forms import RegisterForm, LoginForm, SubscribeForm
from webchat.forms import UnsubscribeForm, SendForm

DEBUG = True
SECRET_KEY = 'secret key for development'
USERNAME = 'admin'
PASSWORD = 'default'

app = Flask(__name__)
app.config.from_object(__name__)

Bootstrap(app)

CsrfProtect(app)
login_manger = LoginManager(app)

socketio = SocketIO(app)


@login_manger.user_loader
def load_user(user_id):
    return db.user_get_by_id(int(user_id))


@socketio.on('my event', namespace='/test')
def test_message(message):
    pass


@socketio.on('join', namespace='/test')
def join(message):
    join_room(message['room'])


@socketio.on('leave', namespace='/test')
def leave(message):
    leave_room(message['room'])


@socketio.on('my room event', namespace='/test')
def send_room_message(message):
    print 5, message
    m = db.message_add(message['data'], message['user_id'], message['room'])
    emit('my response',
         {'data': message['data'], 'date': m.when_str(),
          'user': message['username']},
         room=message['room'])


@socketio.on('connect', namespace='/test')
def test_connect():
    pass


@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def log_in():
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            login = form.login.data
            password = form.password.data
            print login, password
            user = db.user_get_by_login_and_password(login, password)
            if user:
                login_user(user)
                return redirect(url_for('my_channels'))
    return render_template('login.html', form=form)


@app.route('/channels/<path:name>')
@login_required
def room(name):
    channel = db.channel_get_by_name(name)
    if not channel:
        raise NotFound
    print channel.messages
    context = {'channel': channel,
               'form': SendForm(),
               'user': current_user,
               'room': name}
    return render_template('room.html', **context)


@app.route('/logout')
@login_required
def log_out():
    logout_user()
    return redirect(url_for('index'))


@app.route('/registration', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            print 'validate'
            login = form.login.data
            if not db.user_is_login_free(login):
                return redirect(url_for('register'))
            password = form.password.data
            db.user_add(login, password)
            return redirect(url_for('index'))
    return render_template('registration.html', form=form)


@app.route('/my_channels')
@login_required
def my_channels():
    form = UnsubscribeForm()
    channels = current_user.channels
    return render_template('my_channels.html', form=form,
                           channels=channels)


@app.route('/channel_list')
@login_required
def channel_list():
    subscribe_form = SubscribeForm()
    unsubscribe_form = UnsubscribeForm()
    channels = db.channels_get_all()
    return render_template('channel_list.html', channels=channels,
                           user=current_user, s_form=subscribe_form,
                           u_form=unsubscribe_form)


@app.route('/subscribe', methods=['POST'])
@login_required
def subscribe():
    form = SubscribeForm()
    if form.validate_on_submit():
        channel = db.channel_get_by_id(form.channel_id.data)
        current_user.subscribe(channel)
        db.session.commit()
        return redirect(url_for('room', name=channel.name))
    return redirect(url_for('channel_list'))


@app.route('/unsubscribe', methods=['POST'])
@login_required
def unsubscribe():
    form = UnsubscribeForm()
    if form.validate_on_submit():
        current_user.unsubscribe(form.channel_id.data)
        db.session.commit()
        return redirect(url_for(form.return_to.data))


@app.route('/create_channel', methods=['GET', 'POST'])
@login_required
def create_channel():
    form = SendForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            ch_name = unicode(form.text.data)
            db.channel_create(ch_name, current_user)
            return redirect(url_for('room', name=ch_name))
    return render_template('create_channel.html', form=form)


@app.route('/search')
@login_required
def search_channel():
    string = request.args.get('search')
    channels = db.channels_search(string)
    subscribe_form = SubscribeForm()
    unsubscribe_form = UnsubscribeForm()
    return render_template('channel_list.html', channels=channels,
                           user=current_user, s_form=subscribe_form,
                           u_form=unsubscribe_form)


@app.route('/channels/<path:name>/search')
@login_required
def search_message(name):
    messages = db.messages_search(name, request.args.get('search'))
    return render_template('message_search.html', messages=messages)


if __name__ == '__main__':
    socketio.run(app)